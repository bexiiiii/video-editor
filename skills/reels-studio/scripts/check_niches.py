#!/usr/bin/env python3
"""Validate assets/niches.json: JSON shape, known technique/layout/style ids, hooks per language,
BPM ranges and palette contrast.  Usage: check_niches.py <path to skills/reels-studio>"""
import json, re, sys, pathlib
S = pathlib.Path(sys.argv[1])
d = json.load(open(S/"assets/niches.json"))
tech = set(re.findall(r"^\| `([a-z_]+)` \|", (S/"references/techniques.md").read_text(), re.M))
lay = set(re.findall(r"^\| `([a-z-]+)` \|", (S/"references/layouts.md").read_text(), re.M))
def lum(h):
    c=[int(h[i:i+2],16)/255 for i in (1,3,5)]
    c=[x/12.92 if x<=0.03928 else ((x+0.055)/1.055)**2.4 for x in c]
    return 0.2126*c[0]+0.7152*c[1]+0.0722*c[2]
def cr(a,b):
    la,lb=sorted([lum(a),lum(b)],reverse=True); return (la+0.05)/(lb+0.05)
errs=[]; req=["label","match","styles","palette","art_direction","music","techniques","layouts","materials","copy","compliance"]
for k,n in d["niches"].items():
    for r in req:
        if r not in n: errs.append(f"{k}: missing {r}")
    for t in n["techniques"]["favor"]+n["techniques"]["avoid"]:
        if t not in tech: errs.append(f"{k}: unknown technique {t}")
    if set(n["techniques"]["favor"])&set(n["techniques"]["avoid"]): errs.append(f"{k}: technique both favor/avoid")
    for l in n["layouts"]["favor"]:
        if l not in lay: errs.append(f"{k}: unknown layout {l}")
    ids=[s["id"] for s in n["styles"]["recommended"]+n["styles"]["avoid"]]
    if any(i not in "ABCDEFG" for i in ids) or len(ids)!=len(set(ids)): errs.append(f"{k}: bad style ids {ids}")
    for lg in ("ru","uz","kk"):
        if len(n["copy"]["hooks"][lg])!=3: errs.append(f"{k}: hooks {lg} != 3")
        if lg not in n["label"] or lg not in n["copy"]["cta_verbs"] or lg not in n["copy"]["avoid_words"]: errs.append(f"{k}: missing {lg}")
    p=n["palette"]; a,a2=p["accent"],p["accent2"]
    cl,cd,ci=cr(a,"#FBFDFD"),cr(a,"#0B0D0D"),cr(a2,"#101011")
    flag="" if cl>=3 and cd>=3 and ci>=4.5 else "  <-- FAIL"
    print(f"{k:16} accent {a} light {cl:.2f} dark {cd:.2f} | accent2 {a2} vs ink {ci:.2f}{flag}")
    if flag: errs.append(f"{k}: palette contrast")
    lo,hi=n["music"]["bpm"]
    if not (95<=lo<hi<=117): errs.append(f"{k}: bpm {lo}-{hi}")
print(f"techniques known: {len(tech)}, layouts known: {len(lay)}")
print("ERRORS:" if errs else "OK", *errs, sep="\n")
