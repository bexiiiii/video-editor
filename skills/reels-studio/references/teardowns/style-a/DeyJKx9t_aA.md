# DeyJKx9t_aA: style teardown (zaytsevtech, "Как оплатить иностранные сервисы из России?")

How this was measured: 1080x1920, 60 fps, 74.47 s. Values come from pixel sampling of full-res frames, 30 fps strips (`tr_*.jpg`), RMS audio windows and `transcript.json`. px values are at 1080 width.

The design system is the same as Der0UBDNBmZ (see `../Der0UBDNBmZ/style.md`). This report records the same structure plus what is specific to this tutorial or integration format.

---

## 1. Format and structure

- **Faceless motion graphics with voice-over**, in a how-to or tutorial format. It contains a native sponsor segment (the "FLY" virtual card in Telegram) presented as "option 2".
- No talking head. Real UI screenshots are placed in iPhone mockups or as floating screenshot cards.
- **Density.** 22 scenes in 74.5 s, about 3.4 s average. New elements appear about every 0.7–1 s.
- **Voice.** 175 wpm, faster than Der0 (160 wpm). Speech ratio 0.89.
- Detected "cuts" at 14.25, 15.48, 16.85 and 19.45 s are fast whips or blur moves, not true hard cuts. There are **no hard cuts** in this video.

| # | t (s) | BG | Content (on-screen text in quotes) | Entry |
|---|---|---|---|---|
| 1 | 0.00–4.60 | **orange photo blur** (out-of-focus warm photo: #C57C1F top-left, #E2972D left, #984529 centre, deep red #601303 bottom) | Glassy 3D music-player carousel (album cards in perspective plus a frosted control bar, "Spotify" label) at y 12–32%. 3D app icons pop at the 4 corners of the player exactly on their spoken names (see below). Words «карту не принимают» at y 35% (3.5–3.9 s) | Frame 0 is already the full scene, so the motion starts immediately |
| 2 | 4.60–5.65 | white | «Есть 2 варианта» large, at y 42% (the only vertically centred headline). The "2" rolls in last | push left plus luminance crossfade orange→white |
| 3 | 5.65–8.80 | dark | «два маршрута / оплаты» plus pill [card thumb] «оплата» → the camera **pans down** a dashed line → it branches into pills «Apple» (6.3) and «карта FLY» (7.1), with lime text «через баланс» | luminance crossfade, content whips up |
| 4 | 8.80–11.40 | dark | Camera continues down the same vertical canvas. An Apple gift card flies in tilted about −8° and straightens, then branches «карта / подарочная карта» and «аккаунт / регион аккаунта» | continuous camera move |
| 5 | 11.40–14.10 | **orange-to-black gradient** | Gift card (top, y 9–20%), pills «карта» and «аккаунт» with Apple logos, labels «регион карты» / «регион аккаунта», text-selection highlight on «совпадать» | **true horizontal push**: the new panel slides in from the right while the old one moves left (≈250 ms). The gift card is the shared element |
| 6 | 14.10–19.40 | dark | «App Store» → «профиль / официальный экран Apple» → «погасить код». iPhone mockup (App Store account sheet) with a circular magnifier lens on «Redeem Code» | whip left plus crossfade. The phone enters from the right with blur |
| 7 | 19.40–21.10 | dark | Phone slides to the left half (about 280 px wide). Right side: «ввести код / пополнить баланс», caption «пояснение к действию» | layout reflow move |
| 8 | 21.10–25.50 | **navy-black vignette** (#02040D to #090F1B, black right edge) | «iCloud+», huge 3D glossy iCloud cloud (≈504 px), purple Apple app icon, «оплата» with blue highlight chip «через Apple», caption «где доступна оплата через Apple» | whip left |
| 9 | 25.50–27.60 | dark | «Spotify / через / сайт» with the Spotify 3D icon inline after «сайт» (word-by-word). The icon then flies to the top-right corner | blur-in |
| 10 | 27.60–29.40 | dark | «сайт Spotify», Spotify 3D icon (224 px), real Premium pricing screenshot, «пример страницы Premium» | shared icon move |
| 11 | 29.40–32.00 | **black with cyan edge glow plus star particles** (#00293A to #002033 at the corners) | «второй / вариант», 3D purple FLY virtual card «$1,00 •••• 1809», «для оплаты на сайтах» | crossfade plus blur-in |
| 12 | 32.00–35.90 | dark | «FLY в Telegram», «Сингапур», iPhone with the FLY mini-app | the card shrinks into the phone screen (shared element) |
| 13 | 35.90–39.90 | dark | «Мои карты / на экране уже выпущенная карта». Screenshot without a phone frame (≈410 px card). Highlight outline boxes move between UI items | whip with heavy blur |
| 14 | 39.90–42.90 | dark | «реквизиты / данные для оплаты после выпуска», highlight on the «Реквизиты» button | same layout, swap |
| 15 | 42.90–45.20 | dark | «через СБП / пример на скриншоте», top-up screen with the СБП row outlined | whip |
| 16 | 45.20–47.90 | dark | **«0%»** rolling counter, «комиссия за пополнение / по условиям FLY». The screenshot zooms out to about 75% | whip down then a scale-down re-entry |
| 17 | 47.90–51.40 | dark | «курс и сумма / пример на скриншоте», rate row outlined | whip |
| 18 | 51.40–53.50 | dark | «как обычной картой», FLY card above the ChatGPT pricing table, label «ChatGPT» | whip |
| 19 | 53.50–55.00 | dark | «сайт ChatGPT», pricing screenshot, «chatgpt.com · реальные тарифы» | blur zoom |
| 20 | 55.00–58.30 | dark | «выбрать Plus» (crop of the Plus column), then right column «ввести реквизиты» / «подтвердить платёж», caption «дальнейшие действия» | reflow: the column moves left |
| 21 | 58.30–61.30 | orange gradient | «зарубежные подписки / и онлайн-покупки», FLY card, 3 icons (ChatGPT, Spotify, Discord) popping with a 70 ms stagger | **quick dissolve, about 100 ms** |
| 22 | 61.30–68.80 | dark | 3D red folder «памятки», 2 glass checklist cards «перед выпуском» (Поддержка сервиса / Регион аккаунта) and «перед списанием» (Дата / Нужная сумма), filled line by line | whip left |
| 23 | 68.80–74.47 | white | «одна карта / несколько сервисов [card chip]», the FLY card inside a glass ring with 6 orbiting 3D icons (ChatGPT, Claude, Spotify, iCloud, Steam, Discord), caption «поддержку сервиса и регион / проверить заранее» with keywords in bold | luminance crossfade dark→white plus push |

**Hook (0–4.6 s).**
- It opens on a rich, warm, photographic frame (unlike the flat dark of the other videos).
- **3D app icons pop on the brand names.** Each pops about 0.05–0.1 s after its word starts:

| Icon | Position | Pop time | Spoken |
|---|---|---|---|
| ChatGPT | TL (x≈90, y≈480) | 0.60 | «ChatGPT» 0.50 |
| Claude | TR | 1.40 | «Claude» 1.36 |
| Spotify | BL (y≈1300) | 1.80 | «Spotify» 1.80 |
| iCloud | BR | 2.40 | «iCloud» 2.38 |

- The 4 icons frame the central player, so the question "как оплатить X, Y, Z…" is visualised as a ring of services.
- Then «карту не принимают» blur-reveals word by word as the problem statement.
- There is no title card. The question is the hook.

**Ending.**
- A summary visual: all services orbiting one card, plus a practical "check in advance" caption.
- No CTA, no logo. It ends 0.4 s after the last word.

---

## 2. Backgrounds

| Theme | Value | Use |
|---|---|---|
| Dark base | **#0B0D0D** plus a 36 px dot grid (same as Der0) | about 65% of the runtime |
| Light | **#FBFDFD** plus a 24 px dot grid | scenes 2 and 23 |
| Orange photo blur | Heavily defocused warm photo (about 80 px blur), oranges #C57C1F / #E2972D, reds #984529 → #601303 at the bottom | hook only |
| Orange-to-black gradient | Hot spot at the top-right: #C84A00 at (800,300), #C24800 at the top-right corner, #8F2D00 at the top-left. It falls to #130200 by 50%H and is **pure #000000** in the bottom half (a radial glow from the top-right, about 900 px radius) | scenes 5 and 21 (Apple and "summary" moments) |
| Navy vignette | #02040D to #090F1B with a faint blue glow on the left, black on the right | iCloud scene |
| Cyan-edge night | Black #000000 with cyan glows #00293A in the top-left and bottom-right corners and sparse star dots | FLY "second option" reveal |

Background changes use the same **≈250 ms luminance crossfade**, or a panel push (scene 5), or a 100 ms dissolve (scene 21).

---

## 3. Typography

Same family: **Google Sans / Google Sans Flex, weight 500, sentence case, centred.**

| Role | Size | Position | Colour |
|---|---|---|---|
| Headline («App Store», «сайт Spotify», «FLY в Telegram») | ≈78 px (glyph box cap→descender 73 px). Line-height about 1.15 | **y 18–20%** (higher than Der0's 24%, to leave room for big mockups) | **#FBFDFD**, with a **dark halo**: the background darkens from 11 to about 4–5 (out of 255) within about 40 px of the glyphs, i.e. a text-shadow of 0 0 40px rgba(0,0,0,.6) |
| Statement («Есть 2 варианта») | ≈112 px (glyph box 104 px), 1 line, 790 px wide | y 42% | #0B0D0D on white |
| Sub-headline under the headline («Сингапур», «официальный экран Apple», «пример на скриншоте») | ≈34–40 px, 400–500 | about 70 px under the headline (y 23–25%) | #FBFDFD at about 85% |
| Hero number «0%» | ≈108 px (cap 77) | y 14% | white |
| Caption | ≈40 px (glyph box 34–35 px) | y 69–78% | white or #EDEDED. On white it is #444 with bold keywords |
| Side labels (beside the phone) | ≈44 px, 500, 2 lines | x≈820, centred column | white |
| Lime accent («через баланс») | ≈44 px, 500 | under the pill | **#C0EA4E** |
| Pill label («Apple», «карта FLY», «аккаунт») | ≈44–56 px, 500 | | white on a near-black pill |

Text is at most about 24 chars per line, 1–2 lines, 2–6 words at once.

---

## 4. Text animation

- **Word blur-in.** opacity 0→1, blur about 16 px→0, y +20 px→0, ≈400 ms, expo.out, 80–120 ms between words. Examples: «App» then «Store» about 0.1 s apart; «зарубежные» then «подписки».
- **Inline icon.** In «Spotify / через / сайт [icon]» the icon is the last "word". It pops with scale, then the line can hand that icon off to the next scene.
- **Rolling counter.** «0%» and the "2" in «Есть 2 варианта»: vertical digit roll with blur, about 350 ms.
- **Selection highlight** on «совпадать», same as Der0: dark-blue fill with blue handles, swept left→right in about 300 ms.
- **Blue chip highlight** on «через Apple»: #2478F6 rounded rect, radius 10. It wipes in behind the existing words.
- **Exit.** Text leaves only with the scene (whip or crossfade blur).

---

## 5. Graphics and objects

- **3D app icons** are the signature here.
  - Glossy, inflated "clay-plastic" renders of brand logos: ChatGPT knot in teal #19C3B1, Claude starburst in coral, Spotify in green #1ED760 with a darker rim, iCloud cloud in blue #0490F9 with soft specular highlights, Discord in blurple, Steam in navy.
  - Size about 110–160 px in groups, about 224 px solo, about 500 px when the icon is the hero (iCloud).
  - No outline. A soft contact shadow on white and none on dark.
- **Icon pop.** Scale 0 → 1.12 → 1.0 over about 300 ms (back.out(2)), with a slight rotation of about −10°→0 and opacity 0→1 in the first 80 ms. Groups stagger by 70 ms. Idle is a gentle float of ±6 px.
- **iPhone mockup.**
  - iPhone 15 Pro, silver frame, about 512 x 1057 px (47% W), centred at y 27–82%.
  - Soft outer shadow about 0 30px 80px rgba(0,0,0,.6).
  - The screen is a real screenshot. A white circular "magnifier" lens (about 170 px, 4 px white ring, slight drop shadow) sits on the tap target («Redeem Code»).
- **Floating screenshot cards** (no frame): radius about 24, about 410–440 px wide. Behind them a darkened duplicate is offset, blurred and dimmed, so the card has depth. Highlight boxes are 3 px #FFFFFF outlines at radius 12 that jump between UI rows (≈250 ms, expo.out).
- **Glass pills.** Height about 72–90 px, radius full. Fill **#050808** (darker than the background). The border is a 2–3 px gradient rim #686B6B → #2C2E2E (light at the top-left). Icon at the left. 44–56 px white label.
- **Glass checklist cards** (scene 22): about 330 x 300 px, radius 20, the same rim plus inner glow as Der0. A header row in its own inner glass pill, then rows with a white doc icon and 30 px grey text. The cards fill row by row.
- **FLY virtual card.** 3D purple gradient (#1E126C → #8A7ED2) with a glossy rendered folder/headphones motif, radius about 28, about 640 x 370 px. It is treated like a hero product shot.
- **Flow tree.** Dashed connectors (2 px, 12/10 dash, #5A5D5D) branching with a "Y" split. The **camera pans down the tree** (a vertical canvas scroll of about 900 px over about 3 s, ease in-out between nodes) so the steps read as a journey.
- **Orbit ring** (finale): a thin light-grey circle (≈340 px, 2 px, with a white glass inner fill) holding the card. 6 icons sit around it at about 260 px radius and drift slowly.

---

## 6. Transitions

| Type | Timing | Count |
|---|---|---|
| Horizontal whip (old content exits left with horizontal blur, new content enters from the right) | about 150 ms exit plus 350–450 ms expo settle | about 9 (main transition here) |
| Vertical whip (up or down) | same timing | about 5 |
| Luminance crossfade plus move | 250 ms colour tween | 4 (4.6, 5.65, 68.8, plus the iCloud navy) |
| True panel push (both scenes visible, sliding) | about 250 ms | 1 (11.4) |
| Quick dissolve | about 100 ms | 1 (58.4) |
| Camera pan along a canvas (no transition, continuous) | 2–3 s | 1 long sequence (5.7–11.4) |
| Shared-element hand-offs (gift card, Spotify icon, FLY card into phone, screenshot zoom-out) | 400–500 ms | about 5 |

- All transitions sit in the inter-sentence pauses (RMS −44 to −50 dB at every boundary measured).
- The new scene lands on the next sentence onset.

---

## 7. Sync with voice

- **Keyword captions, not subtitles.** Headlines are 1–3 word labels of the current step («погасить код», «курс и сумма»).
- Brand icons, «0%», «Сингапур» and pills hit within about 0.1 s of the spoken word. Icons: +0.1, +0.04, 0.0 and +0.02 s.
- Headlines appear at the sentence start.
- For tutorial steps, the UI highlight box moves when the instruction verb is spoken («Открывайте…», «Выбирайте…»).

---

## 8. Audio

- **Voice only. No music, no SFX.**
- Same mastering as Der0: **−14.1 LUFS integrated, LRA 1.7 LU**, pauses at the −46 dB floor, about 0.3–0.4 s gaps.
- Faster, energetic read (175 wpm), imperative mood.

---

## 9. Secret sauce (specific to this video, on top of the shared ones in Der0)

1. **Brand recognition through 3D glossy app icons** that pop on the syllable of the brand name. It is the strongest hook device.
2. **Real UI in premium framing.** Screenshots are never shown flat. They go in a mockup, or float with a blurred shadow duplicate, plus a lens or outline highlight that moves with the narration.
3. **Warm photographic hook → cool tinted-dark body → orange glow for "payoff" scenes.** The colour carries the story beats: problem (warm), steps (dark), solution or summary (orange, white).
4. **Camera-on-canvas.** The dashed flow tree is scrolled like a Figma board, turning "two options with sub-steps" into one continuous shot.
5. **Dark halo behind white headlines,** so text stays crisp over glows and screenshots.
6. **Pills darker than the background with a lit rim.** They read as physical glass buttons.
7. **Sponsor integration styled exactly like editorial content** (same type and motion), so it does not feel like an ad break.

**What a naive recreation gets wrong:**
- flat 2D brand logos instead of 3D renders;
- raw screenshots without depth or highlights;
- music under a tutorial;
- slow slide transitions;
- headlines placed at the centre instead of at y about 19% when a mockup is present;
- missing the dark text halo;
- icons appearing all at once instead of on their words.

---

## 10. Reproducible spec (the 5 most common elements here)

```css
.h1{font:500 78px/1.15 "Google Sans Flex","Onest",sans-serif;color:#FBFDFD;text-align:center;
    position:absolute;left:90px;right:90px;top:19%;text-shadow:0 0 40px rgba(0,0,0,.65);}
.sub{font:500 38px/1.2 "Google Sans Flex";color:rgba(251,253,253,.85);top:calc(19% + 100px);}
.gpill{height:84px;padding:0 28px;border-radius:999px;background:#050808;color:#FBFDFD;font:500 50px/84px "Google Sans Flex";
       border:2.5px solid transparent;background-clip:padding-box;box-shadow:0 0 0 2.5px #3a3d3d, inset 0 1px 0 rgba(255,255,255,.35);}
.phone{width:512px;height:1057px;border-radius:84px;box-shadow:0 30px 80px rgba(0,0,0,.6);} /* silver frame PNG over the screenshot */
.lens{width:170px;height:170px;border-radius:50%;border:4px solid #fff;box-shadow:0 10px 30px rgba(0,0,0,.35);backdrop-filter:none;} /* scale the underlying crop 1.3x inside */
.hl{outline:3px solid #fff;border-radius:12px;}
.orange{background:radial-gradient(120% 60% at 85% 12%,#C84A00 0%,#8F2D00 35%,#230500 55%,#000 70%);}
```

```js
// 1) 3D icon pop on the brand word (wordT from the transcript)
tl.fromTo(icon,{scale:0,rotate:-10,opacity:0},{scale:1,rotate:0,opacity:1,duration:.32,ease:"back.out(2.2)"},wordT+.05);
//    idle: y = sin((t-wordT)*2.1)*6  (seek-safe keyframes)

// 2) Horizontal whip transition (the most frequent)
tl.to(old,{x:-360,opacity:0,filter:"blur(10px)",duration:.15,ease:"power2.in"},T)
  .fromTo(next,{x:300,filter:"blur(14px)",opacity:.4},{x:0,filter:"blur(0px)",opacity:1,duration:.45,ease:"expo.out"},T+.15);

// 3) Headline word blur-in
tl.from(words,{opacity:0,y:20,filter:"blur(16px)",duration:.4,ease:"expo.out",stagger:.1},T+.2);

// 4) Camera pan down the flow tree (one tall canvas)
tl.to(canvas,{y:-900,duration:2.6,ease:"power2.inOut"},5.9);
tl.fromTo(dashPath,{strokeDashoffset:len},{strokeDashoffset:0,duration:.5,ease:"power2.out"},6.0);
tl.from(pills,{scale:.6,opacity:0,filter:"blur(8px)",duration:.35,ease:"back.out(1.6)",stagger:.8},6.3);

// 5) Screenshot step highlight that follows the narration
tl.to(hlBox,{top:rowY,height:rowH,duration:.28,ease:"expo.out"},verbT);
tl.fromTo(lens,{scale:.4,opacity:0},{scale:1,opacity:1,duration:.3,ease:"back.out(1.8)"},verbT);

// Gift card drop: from {y:-200, rotate:-8, filter:"blur(10px)"} to {y:0, rotate:0}, .5s, "expo.out".
// Counter "0%": digit column yPercent -900 -> 0, .38s, power3.out.
```
