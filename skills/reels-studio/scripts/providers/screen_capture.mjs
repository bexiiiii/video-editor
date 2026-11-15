#!/usr/bin/env node
/* reels-studio · screen capture of ONE public page as a smooth vertical scroll (frames → broll.py encodes).
 *
 * Dependency-free: Node ≥ 22 (global WebSocket + fetch) drives the Chrome that HyperFrames already installed
 * (`npx hyperframes browser path`) over the DevTools protocol. Deterministic frame stepping: for frame i the page
 * is scrolled to y(i) (sine ease-in-out) and a screenshot is taken, so the clip is perfectly smooth at any fps
 * however slow the capture is.
 *
 *   node screen_capture.mjs --chrome PATH --url https://… --out DIR [--seconds 8] [--fps 30] [--speed 90]
 *        [--width 432 --height 768 --dpr 2.5] [--desktop] [--timeout 45000] [--shot FILE]
 *   → DIR/f_00000.jpg … + DIR/meta.json {final_url, title, frames, fps, scroll_px, page_height, dismissed, blurred}
 *
 * Safety (the caller — broll.py — has already checked scheme/host/redirects; this re-checks the final URL):
 *   - https only; the main frame never navigates anywhere else: no clicks on links, no typing, no form submits,
 *     downloads denied, pop-ups closed; a final URL that is not https or resolves to a private host aborts.
 *   - cookie banners: one click on an obvious "accept / ok / принять" button inside a cookie/consent container,
 *     nothing else. Logins / paywalls are not handled (capture whatever is public).
 *   - personal data: visible phone numbers (+… 10–15 digits, or 7/8 + 9–10 digits) and e-mail addresses, tel:/mailto:
 *     links are blurred in the DOM before every capture.
 * `--allow-file` (tests only) permits file:// URLs for local layout checks.
 */
import { spawn } from "node:child_process";
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { lookup } from "node:dns/promises";
import { isIP, connect as netConnect } from "node:net";
import { createServer } from "node:http";

const A = {};
for (let i = 2; i < process.argv.length; i++) {
  const k = process.argv[i];
  if (!k.startsWith("--")) continue;
  const n = process.argv[i + 1];
  if (n == null || n.startsWith("--")) A[k.slice(2)] = true; else { A[k.slice(2)] = n; i++; }
}
const die = (m, c = 1) => { console.error("screen_capture: " + m); process.exit(c); };
if (!A.chrome || !A.url || (!A.out && !A.shot)) die("usage: --chrome PATH --url https://… --out DIR");
const url = new URL(A.url);
if (url.protocol !== "https:" && !(A["allow-file"] && url.protocol === "file:")) die("https URLs only");
const SECONDS = +(A.seconds ?? 8), FPS = +(A.fps ?? 30), SPEED = +(A.speed ?? 90);
const W = +(A.width ?? (A.desktop ? 1080 : 432)), H = +(A.height ?? (A.desktop ? 1920 : 768));
const DPR = +(A.dpr ?? (A.desktop ? 1 : 2.5));
const TIMEOUT = +(A.timeout ?? 45000);
const DESKTOP_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36";
const MOBILE_UA = "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Mobile Safari/537.36";

const PRIVATE = /^(localhost|.*\.local|.*\.internal|127\.|10\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.|169\.254\.|0\.|\[?::1\]?|\[?f[cd]|\[?fe80)/i;

// Network policy. The captured page is untrusted: it can redirect, navigate, embed, open WebSockets
// or start workers. All of Chrome's traffic is forced through a local policy proxy that (1) accepts
// only CONNECT tunnels to port 443 (https/wss), (2) resolves the host ONCE, requires every address
// to be public, and (3) connects to that same vetted IP — so Chrome never resolves anything itself
// and DNS rebinding cannot swap the address after the check. Plain-HTTP proxy requests are refused.

/** Parse an IPv4/IPv6 literal into bytes (Uint8Array of 4 or 16) or null. Handles "::" and an
 *  embedded dotted IPv4 tail (::ffff:1.2.3.4, 64:ff9b::1.2.3.4). Hex forms are parsed the same way. */
function ipBytes(raw) {
  const ip = raw.replace(/^\[|\]$/g, "").split("%")[0];
  const fam = isIP(ip);
  if (fam === 4) return Uint8Array.from(ip.split(".").map(Number));
  if (fam !== 6) return null;
  let s = ip, tail = [];
  const m = /^(.*:)(\d+\.\d+\.\d+\.\d+)$/.exec(s);
  if (m) {
    const q = m[2].split(".").map(Number);
    tail = [(q[0] << 8) | q[1], (q[2] << 8) | q[3]];
    s = m[1].endsWith("::") ? m[1] : m[1].slice(0, -1);
  }
  const parts = s.split("::");
  if (parts.length > 2) return null;
  const grp = (x) => (x ? x.split(":").map((h) => (/^[0-9a-f]{1,4}$/i.test(h) ? parseInt(h, 16) : NaN)) : []);
  const head = grp(parts[0]), rest = parts.length === 2 ? grp(parts[1]) : [];
  const fill = 8 - head.length - rest.length - tail.length;
  const groups = parts.length === 2 ? [...head, ...Array(Math.max(fill, 0)).fill(0), ...rest, ...tail] : [...head, ...tail];
  if (groups.length !== 8 || groups.some((g) => Number.isNaN(g))) return null;
  const out = new Uint8Array(16);
  groups.forEach((g, i) => { out[2 * i] = g >> 8; out[2 * i + 1] = g & 255; });
  return out;
}
function publicV4(b) {
  const [a, c] = b;
  return !(a === 0 || a === 10 || a === 127 || a >= 224 || (a === 100 && c >= 64 && c <= 127) ||
    (a === 169 && c === 254) || (a === 172 && c >= 16 && c <= 31) || (a === 192 && c === 168) ||
    (a === 192 && c === 0) || (a === 198 && (c === 18 || c === 19)) || (a === 192 && c === 88 && b[2] === 99));
}
/** Deny by default: only global unicast IPv4, and IPv6 2000::/3 minus documentation/6to4/Teredo
 *  tunnels to private v4; IPv4-mapped/compatible/NAT64 forms are judged by their embedded IPv4. */
function publicIp(ip) {
  const b = ipBytes(ip);
  if (!b) return false;
  if (b.length === 4) return publicV4(b);
  const zero = (n) => b.slice(0, n).every((x) => x === 0);
  if (zero(10) && b[10] === 0xff && b[11] === 0xff) return publicV4(b.slice(12));           // ::ffff:a.b.c.d / ::ffff:7f00:1
  if (zero(12)) return false;                                                               // ::, ::1, ::a.b.c.d (deprecated compat)
  if (b[0] === 0x00 && b[1] === 0x64 && b[2] === 0xff && b[3] === 0x9b) return publicV4(b.slice(12)); // 64:ff9b::/96 NAT64
  if ((b[0] & 0xe0) !== 0x20) return false;                                                 // outside 2000::/3 (ULA fc00::/7, link-local, multicast…)
  if (b[0] === 0x20 && b[1] === 0x01 && b[2] === 0x0d && b[3] === 0xb8) return false;       // 2001:db8::/32 documentation
  if (b[0] === 0x20 && b[1] === 0x01 && b[2] === 0x00 && b[3] === 0x00) return false;       // 2001::/32 Teredo
  if (b[0] === 0x20 && b[1] === 0x02) return publicV4(b.slice(2, 6));                       // 2002::/16 6to4
  return true;
}

let blockedCount = 0;
const blockedList = [];
const block = (what) => { blockedCount++; if (blockedList.length < 20) blockedList.push(String(what).slice(0, 120)); };

/** Resolve once and return a vetted public address (or null). */
async function vettedAddress(host) {
  host = host.replace(/^\[|\]$/g, "");
  if (/^(localhost|.*\.localhost|.*\.local|.*\.internal)$/i.test(host)) return null;
  if (isIP(host)) return publicIp(host) ? host : null;
  try {
    const addrs = await lookup(host, { all: true, verbatim: true });
    if (!addrs.length || !addrs.every((a) => publicIp(a.address))) return null;
    return addrs[0].address;
  } catch { return null; }
}

const proxy = createServer((req, res) => { block(`plain-http ${req.url}`); res.writeHead(403); res.end(); });
proxy.on("connect", async (req, client, head) => {
  const m = /^\[?([^\]]+?)\]?:(\d+)$/.exec(req.url || "");
  const host = m?.[1], port = Number(m?.[2]);
  const ip = m && port === 443 ? await vettedAddress(host) : null;
  if (!ip) { block(`connect ${req.url}`); client.end("HTTP/1.1 403 Forbidden\r\n\r\n"); return; }
  const up = netConnect({ host: ip, port }, () => {
    client.write("HTTP/1.1 200 Connection Established\r\n\r\n");
    if (head?.length) up.write(head);
    up.pipe(client); client.pipe(up);
  });
  const kill = () => { up.destroy(); client.destroy(); };
  up.on("error", kill); client.on("error", kill);
});
const proxyPort = await new Promise((res) => proxy.listen(0, "127.0.0.1", () => res(proxy.address().port)));

async function urlAllowed(raw) {
  let u; try { u = new URL(raw); } catch { return false; }
  if (u.protocol === "data:" || u.protocol === "blob:") return true;          // no network
  if (u.protocol === "file:") return !!A["allow-file"];
  if (u.protocol !== "https:" && u.protocol !== "wss:") return false;
  if (u.port && u.port !== "443") return false;
  return (await vettedAddress(u.hostname)) !== null;
}
if (url.protocol === "https:" && !(await urlAllowed(url.href))) die("URL host is not a public address", 5);

const profile = mkdtempSync(join(tmpdir(), "rs-cap-"));
const chrome = spawn(A.chrome, [
  "--headless", "--remote-debugging-port=0", `--user-data-dir=${profile}`, "--no-first-run",
  "--no-default-browser-check", "--disable-extensions", "--mute-audio", "--hide-scrollbars",
  "--disable-features=Translate,MediaRouter", "--disable-quic", "--disable-background-networking",
  `--proxy-server=http://127.0.0.1:${proxyPort}`, "--proxy-bypass-list=<-loopback>",
  "--host-resolver-rules=MAP * ~NOTFOUND , EXCLUDE 127.0.0.1",   // Chrome resolves nothing itself
  "about:blank",
], { stdio: ["ignore", "ignore", "pipe"] });
let cleaned = false;
const cleanup = () => { if (cleaned) return; cleaned = true; try { chrome.kill("SIGKILL"); } catch {} try { proxy.close(); } catch {} try { rmSync(profile, { recursive: true, force: true }); } catch {} };
process.on("exit", cleanup);
const hard = setTimeout(() => { cleanup(); die("hard timeout", 4); }, TIMEOUT + SECONDS * FPS * 1500 + 30000);

const wsUrl = await new Promise((res, rej) => {
  let buf = "";
  const t = setTimeout(() => rej(new Error("chrome did not start")), 20000);
  chrome.stderr.on("data", (d) => {
    buf += d; const m = /DevTools listening on (ws:\/\/\S+)/.exec(buf);
    if (m) { clearTimeout(t); res(m[1]); }
  });
  chrome.on("exit", () => rej(new Error("chrome exited")));
}).catch((e) => die(e.message, 4));

const port = new URL(wsUrl).port;
const targets = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
const page = targets.find((t) => t.type === "page");
if (!page) die("no page target", 4);
const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise((r, j) => { ws.onopen = r; ws.onerror = () => j(new Error("ws")); }).catch(() => die("cannot attach", 4));
let seq = 0; const pending = new Map(); const listeners = [];
ws.onmessage = (ev) => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) { const p = pending.get(m.id); pending.delete(m.id); m.error ? p.rej(new Error(m.error.message)) : p.res(m.result); }
  else if (m.method) listeners.forEach((f) => f(m));
};
const send = (method, params = {}) => new Promise((res, rej) => { const id = ++seq; pending.set(id, { res, rej }); ws.send(JSON.stringify({ id, method, params })); });
const evalJs = async (expr) => (await send("Runtime.evaluate", { expression: expr, returnByValue: true, awaitPromise: true })).result?.value;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

await send("Page.enable"); await send("Runtime.enable");
let mainFrameId = null, mainBlocked = null;
listeners.push(async (m) => {
  if (m.method !== "Fetch.requestPaused") return;
  const { requestId, request, resourceType, frameId } = m.params;
  if (await urlAllowed(request.url)) { send("Fetch.continueRequest", { requestId }).catch(() => {}); return; }
  block(request.url);
  if (resourceType === "Document" && (!mainFrameId || frameId === mainFrameId)) mainBlocked = request.url;
  send("Fetch.failRequest", { requestId, errorReason: "BlockedByClient" }).catch(() => {});
});
await send("Fetch.enable", { patterns: [{ urlPattern: "*", requestStage: "Request" }] });
mainFrameId = (await send("Page.getFrameTree")).frameTree.frame.id;
await send("Browser.setDownloadBehavior", { behavior: "deny" }).catch(() => {});
await send("Emulation.setDeviceMetricsOverride", { width: W, height: H, deviceScaleFactor: DPR, mobile: !A.desktop });
await send("Emulation.setUserAgentOverride", { userAgent: A.desktop ? DESKTOP_UA : MOBILE_UA, acceptLanguage: "ru-RU,kk-KZ;q=0.9,en;q=0.8" });
await send("Page.setLifecycleEventsEnabled", { enabled: true }).catch(() => {});
// close pop-ups; never follow window.open
listeners.push((m) => { if (m.method === "Page.windowOpen") { /* ignored: we never act on it */ } });
await send("Page.addScriptToEvaluateOnNewDocument", { source: "window.open = () => null; window.alert = () => {}; window.confirm = () => false; window.prompt = () => null;" });

let loaded = false;
listeners.push((m) => { if (m.method === "Page.loadEventFired") loaded = true; });
await send("Page.navigate", { url: url.href });
const t0 = Date.now();
while (!loaded && Date.now() - t0 < TIMEOUT) await sleep(200);
await sleep(1800);                                   // late layout, web fonts, lazy hero images

if (mainBlocked) { cleanup(); die(`navigation to a non-public/non-https URL blocked: ${String(mainBlocked).slice(0, 80)}`, 5); }
const finalUrl = await evalJs("location.href");
const finalHost = (() => { try { return new URL(finalUrl).host; } catch { return ""; } })();
// the page must stay on the same host for the whole capture (no JS navigation away mid-scroll)
async function stillHere() {
  if (mainBlocked) return false;
  const now = await evalJs("location.href").catch(() => "");
  try { const u = new URL(now); return u.host === finalHost && (await urlAllowed(u.href)); } catch { return false; }
}
try {
  const fu = new URL(finalUrl);
  if (!(fu.protocol === "https:" || (A["allow-file"] && fu.protocol === "file:"))) throw new Error("scheme");
  if (fu.protocol === "https:" && !(await urlAllowed(fu.href))) throw new Error("non-public host");
} catch (e) { cleanup(); die(`final URL rejected (${e.message}): ${String(finalUrl).slice(0, 80)}`, 5); }

// 1) trivial cookie / consent banner → one click on an obvious accept button, nothing else
const dismissed = await evalJs(`(() => {
  const ok = /^(accept( all)?|allow( all)?|agree|i agree|ok|okay|got it|понятно|принять( все)?|согласен|согласна|хорошо|ок|қабылдау|келісемін|жақсы)$/i;
  const box = /cookie|consent|gdpr|куки|cookies|согласие/i;
  for (const b of document.querySelectorAll('button, [role=button], a[role=button], input[type=button]')) {
    const t = (b.innerText || b.value || '').trim();
    if (!ok.test(t) || b.closest('form[action]') ) continue;
    let p = b, hit = false;
    for (let i = 0; i < 6 && p; i++, p = p.parentElement) { if (box.test((p.id || '') + ' ' + (p.className || '') + ' ' + (p.innerText || '').slice(0, 400))) { hit = true; break; } }
    if (hit && !b.href) { b.click(); return t; }
  }
  return null;
})()`).catch(() => null);
if (dismissed) await sleep(600);

// 2) blur personal data (phones, e-mails) in visible text — re-run during the scroll for lazy content
const BLUR = `(() => {
  const re = /(\\+?\\d[\\d\\s()\\-]{8,}\\d)|([\\w.+-]+@[\\w-]+\\.[\\w.]+)/g;
  let n = 0; const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const hits = []; let node;
  while ((node = walk.nextNode())) {
    if (!node.nodeValue || node.parentElement?.dataset?.rsBlur) continue;
    const tag = node.parentElement?.tagName; if (tag === 'SCRIPT' || tag === 'STYLE') continue;
    re.lastIndex = 0; if (re.test(node.nodeValue)) hits.push(node);
  }
  for (const t of hits) {
    const frag = document.createDocumentFragment(); let last = 0; const s = t.nodeValue; re.lastIndex = 0; let m;
    while ((m = re.exec(s))) {
      const digits = (m[1] || '').replace(/\\D/g, '');
      // phones only: "+…" with 10–15 digits, or a 10–11-digit number starting 7/8 (KZ/RU/UZ); prices, years, ids stay readable
      if (m[1] && !(m[1].trim().startsWith('+') ? digits.length >= 10 && digits.length <= 15 : /^[78]\\d{9,10}$/.test(digits))) continue;
      frag.append(s.slice(last, m.index));
      const sp = document.createElement('span'); sp.dataset.rsBlur = '1'; sp.textContent = m[0];
      sp.style.cssText = 'filter:blur(7px);-webkit-filter:blur(7px)'; frag.append(sp); last = m.index + m[0].length; n++;
    }
    if (last) { frag.append(s.slice(last)); t.replaceWith(frag); }
  }
  for (const a of document.querySelectorAll('a[href^="tel:"], a[href^="mailto:"]')) { a.style.filter = 'blur(7px)'; n++; }
  return n;
})()`;
let blurred = (await evalJs(BLUR).catch(() => 0)) || 0;

if (A.shot) {
  if (!(await stillHere())) { cleanup(); die("page navigated away from the approved host", 5); }
  const r = await send("Page.captureScreenshot", { format: "png", captureBeyondViewport: true });
  writeFileSync(A.shot, Buffer.from(r.data, "base64"));
  clearTimeout(hard); cleanup(); process.exit(0);
}

const pageH = (await evalJs("Math.max(document.documentElement.scrollHeight, document.body ? document.body.scrollHeight : 0)")) || H;
const title = (await evalJs("document.title")) || "";
const maxScroll = Math.max(0, pageH - H);
const dist = Math.min(maxScroll, SPEED * SECONDS);
const N = Math.round(SECONDS * FPS);
mkdirSync(A.out, { recursive: true });
for (let i = 0; i < N; i++) {
  const p = N > 1 ? i / (N - 1) : 0;
  const y = Math.round(dist * (0.5 - 0.5 * Math.cos(Math.PI * p)) * 4) / 4;  // sine ease in-out, quarter-px steps
  await evalJs(`window.scrollTo(0, ${y})`);
  if (i % 20 === 10) blurred += (await evalJs(BLUR).catch(() => 0)) || 0;
  if (i === 0) await sleep(300);
  if (!(await stillHere())) { cleanup(); die("page navigated away from the approved host during capture", 5); }
  const r = await send("Page.captureScreenshot", { format: "jpeg", quality: 90, fromSurface: true });
  writeFileSync(join(A.out, `f_${String(i).padStart(5, "0")}.jpg`), Buffer.from(r.data, "base64"));
}
writeFileSync(join(A.out, "meta.json"), JSON.stringify({ final_url: finalUrl, title, frames: N, fps: FPS, scroll_px: dist, page_height: pageH, viewport: [W, H, DPR], dismissed, blurred, blocked_requests: blockedCount, blocked: blockedList }, null, 1));
clearTimeout(hard);
cleanup();
process.exit(0);
