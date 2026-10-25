# Technique library — signature moves to vary every reel

Styles define the base look; **techniques** are extra moves the director adds when the content calls for them, so no two reels look the same.
Most come from the talking-head reels in the reference set (Umar, teardowns `teardowns/style-b/Dd1b9kEA-KL.md`, `Dd3Uz4Mgbn-.md`, `De1roE4t7Lf.md`, `DelZA2dtAE6.md`, `DeZREMAtvBf.md`).
Where they're implemented:
- `RSB.*`: style B library.
- `RSX.*`: technique pack `assets/techniques/head-umar.{js,css}`, loaded for every style.
- `RSA.*`: style A library.

## How the director uses it
1. After the beat plan, pick **2–4 techniques** whose *trigger* matches the script (table below), compatible with the chosen style.
2. Read `~/.reels-studio/history.json` (`scripts/run history.py --show`) and **avoid techniques used in the last 3 reels of the same client/brand** unless the client asked for them. Prefer ones never used for this brand.
3. Write them into `plan/scenes.json` → `scenes[].techniques: [{"id": "portal", "at": 6.4, "props": {}}]` and list them in the scene table shown to the user.
4. After delivery: `scripts/run history.py --record --work work/<slug>` (style, layouts, techniques, components, brand).

## Catalogue
| id | what it looks like | trigger in the script / footage | styles | implementation | sound |
|---|---|---|---|---|---|
| `portal` | travelling light orb grows into a white-out, then the new world | switch between talking head and motion | B, C, D | `RSB.tx.portal` | `boom_sub` |
| `glitch_cta` | 6–9-frame pixel/datamosh glitch | jump into the CTA or a "plot twist" | all | `RSB.tx.datamosh`, `RSX.pixelGlitch` | `glitch` |
| `rgb_ghost` | RGB-split ghost frames at the loop point | the end of a reel that should loop | all | `RSB.tx.rgbGhost` | — |
| `jump_zoom` | hard 2.4× punch on the speaker | punchline, "вот главное", a surprising number | head modes | `RSX.jumpZoom` | none or `bass_hit` |
| `pull_out_phone` | full-frame footage shrinks into an iPhone frame | "смотрите, как это выглядит" / moving to a demo | head modes | `RSX.pullOutPhone` + `RSB.iphone` | `swoosh_down` |
| `sticker_title` | uppercase white sticker title + emoji over the speaker | hook in the first 2 s of a talking head | head modes | `RSB.sticker` | `pop` |
| `karaoke_caption` | one-line caption, words light up grey → full colour as spoken | talking head where literal words matter (B, C; not A/D) | B, C | `RSX.karaoke` / `RSB.caption` | — |
| `chest_widget` | iOS widget pops beside/below the face in the chest band, morphs dot→icon→widget | mentioning an app, a notification, a metric while on camera | head modes | `RSX.chestWidget` | `click` |
| `iphone_proof` | real screen recording inside a deep-purple titanium iPhone | proof, case study, tutorial step | all | `RSB.iphone` (needs `input/` recording) | `tap` |
| `glove_tap` | white glove cursor taps a real UI element | "нажимаете сюда", any button in a demo | B, C, D | `RSB.cursor({kind:'glove'})` | `tap` |
| `paper_section` | warm paper page, embossed grid, giant pale numeral 01/02/03 | numbered list of tips ("3 ошибки…") | B, C | `RSX.paperSection` | `whoosh_short` |
| `section_number` | bold condensed number with motion blur slams in | each item of a numbered list | B, C, D | `RSX.sectionNumber` | `bass_hit` |
| `hero_word` | one thin condensed word, huge, between two small lines | the one key term of the reel ("CHEATCODE", "ФОРМУЛА") | B, C | `RSX.heroWord` | `riser_1s` before |
| `dark_checks` | dark grain section, green checks fill in, the result word changes | checklist, before → after result | B, C | `RSX.darkChecks` | `tick` per check |
| `lens_blur` | strong lens edge blur on the speaker shot | cinematic talking head, premium feel | head modes | `RSX.lensBlur` | — |
| `mute_gag` | voice muffled −11 dB with low-pass while "без звука" is said | the script mentions watching on mute | head modes | mix cue `muffle` in `audio` | — |
| `ig_profile_cta` | IG profile card, follower count ticks up, follow tap | follow CTA (real numbers from the client only) | B, C, D | `RSB.igProfile` | `tap`, `success` |
| `avatar_pill_cta` | avatar pops → unrolls to a pill → name types → button press → dark chip | subscribe CTA | B, C, D | `RSB.ctaFollow` | `click` |
| `save_pill` | "Saqlash" → "Saqlandi" pill flips blue | save CTA | B, C | `RSB.savePill` | `success` |
| `selection_highlight` | iOS text selection sweeps over a key word with handles | the one word to remember | all | `RSB.selection`, `RSA.selection` | — |
| `open_loop_ring` | ring stops ~80 % closed, closes at the payoff | a teaser that pays off later in the reel | B, C | `RSB.ring` | `tick` / `success` |
| `typing_dots` | "•••" bubble as if someone is typing, then the message | client questions, objections, DMs | B, C | `RSB.typing` + `RSB.bubble` | `typing_loop` |
| `strike_fix` | wrong word struck through, correct one appears | myths vs facts, corrections | all | `RSB.strike` | — |
| `curtain_reveal` | red pleated curtain with a gold light leak behind the hook | dramatic hook (A, C, D) | A, C, D | `RSA.background({theme:'curtain'})` | — |
| `number_roll` | slot-machine digits roll to the spoken number | any spoken number / price / % | all | `RSA.numberRoll`, `RSB.counter` | `tick` |

## Rules
- Max 4 techniques per 60 s; never two "loud" ones back to back (portal, glitch_cta, jump_zoom, hero_word).
- Head-mode techniques need real footage. Proof techniques need real material from the client (`materials.md`).
- Style A keeps its audio policy (no SFX) even when it borrows a technique: the sound column then doesn't apply.
