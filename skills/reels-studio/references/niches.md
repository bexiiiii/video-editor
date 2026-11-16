# Niche presets

Data: `assets/niches.json` (this file is the readable version — the JSON is the source of truth).
16 niches + `default`. Each preset gives the orchestrator and workers **priors**, never overrides of the style specs, `layouts.md` variety rules, `audio-policy.md` or the client's brand.

## How the orchestrator uses it
1. **Ask the niche right after the language** (step 0 of SKILL.md, before the style). Detect it first: lowercase the client's message/topic and count hits from each niche's `match` (ru/uz/kk/en, substring match); the top niche with ≥ 1 hit is the suggestion. Ask to confirm in the client's language, e.g. «Похоже, это **стоматология** — верно? Или другая сфера?» / «Bu **stomatologiya** sohasiga oʻxshaydi — toʻgʻrimi?» / «Бұл **стоматология** саласы сияқты — дұрыс па?». No hit or the client declines → offer the list of `label`s; nothing fits → `default`. Write `brief.niche` (slug).
2. **Load the preset** `niches[brief.niche]`.
3. **Style previews:** show `styles.recommended` first, in order, each with its one-line `why`, then the remaining styles; mention an `avoid` style only with its reason if the client picks it (the client may still choose it). Style D still needs footage.
4. **Palette:** use `palette.accent` / `accent2` **only if `brief.brand` has no colours**. Brand colours always win (from the brand-colour layer / `brief.brand.accent`, `accent2`). `accent` = text, strokes, active dots, number highlights (≥ 3:1 on both `#FBFDFD` and `#0B0D0D`); `accent2` = fills/pills/highlights with ink `#101011` on top (≥ 4.5:1). Never set body text in `accent2` on a light page.
5. **Art direction:** append `art_direction.append` to **every** asset prompt in `plan/scenes.json` (after the style base prompt from `director.md` §4) so one video has one look; choose hero objects from `art_direction.props`; never put anything from `art_direction.avoid` in a prompt (the global "no people/faces" rule stays).
6. **Music → sound worker:** `music.mood` + `music.bpm` go into the sound brief, only for styles with music (B, C, E) and only where `audio-policy.md` allows a bed (B/C not under the hook or footage; E a low pad). A and D stay voice-only. If the script hits `music.voice_only_when`, drop the bed for that section or the whole reel.
7. **Director priors:** `techniques.favor` are the first candidates when a trigger matches; `techniques.avoid` are skipped unless the client asks. `layouts.favor` biases the layout mix. `techniques.md` and `layouts.md` rules (2–4 techniques, history avoidance, no layout twice in a row, ≥ 4 layouts …) still apply.
8. **Materials:** start the materials request (`materials.md`) from `materials.ask`, keeping only what the plan uses (≤ 6 items); add `materials.notes` as the privacy/consent line.
9. **Script drafting:** follow `copy.tone`; the hooks are **patterns** — fill them with the client's real numbers/names or drop the number; use `cta_verbs` for the CTA in `brief.lang`; never use `avoid_words`.
10. **QA:** add `compliance` items to the QA pass (`qa-checklist.md`) — e.g. missing disclaimer, guarantee wording, unconsented faces, invented metrics → fail and route to the owner.

Global exclusions (all niches): alcohol, tobacco/vapes/hookah, gambling/betting, weapons; no fake reviews, ratings or metrics; no AI-made people, faces or before/after. Legal notes are guidance, not legal advice — for medicine, pharmacy and finance ask the client to confirm the disclaimer text required in their country (RU 38-ФЗ «О рекламе», KZ «О рекламе», UZ «О рекламе»).

## Schema
| key | content |
|---|---|
| `label` | {ru, uz, kk} name shown to the client |
| `match` | {ru, uz, kk, en} keyword lists for detection |
| `styles` | `recommended` [{id, why}] ranked · `avoid` [{id, why}] |
| `palette` | `accent`, `accent2`, `mood`, `contrast` note |
| `art_direction` | `append` (prompt suffix), `props` (hero candidates), `avoid` |
| `music` | `mood`, `bpm` [lo, hi] (inside 95–117), `voice_only_when` |
| `techniques` | `favor`, `avoid` — ids from `techniques.md` |
| `layouts` | `favor` — ids from `layouts.md` |
| `materials` | `ask` list, `notes` (privacy/regulation) |
| `copy` | `tone`, `hooks` {ru, uz, kk} ×3, `cta_verbs`, `avoid_words` |
| `compliance` | short QA notes |

## Presets at a glance

| slug | niche | styles (ranked) | avoid | accent / accent2 | music |
|---|---|---|---|---|---|
| `education` | Образование и подготовка к экзаменам | E › B › D › G | C | `#1D5FD1` / `#F2B705` | 100–110 |
| `online_school` | Онлайн-школы и курсы | B › C › D | E | `#0F7B83` / `#FFC857` | 104–114 |
| `food_cafe` | Кафе, рестораны и доставка еды | B › D › C | A, E | `#C8452A` / `#F2C14E` | 96–108 |
| `bakery` | Кондитерские и пекарни | B › D › C | A, E | `#A0522D` / `#F3D9B1` | 96–106 |
| `beauty` | Салоны красоты и косметология | D › B › C | E, A | `#B2456E` / `#E9C9B8` | 98–108 |
| `medicine_dental` | Медицина и стоматология | D › B › E | C | `#0B7A75` / `#9ED8DB` | 95–104 |
| `pharmacy` | Аптеки | B › E › A | C | `#138A52` / `#CDEFD9` | 95–104 |
| `fitness` | Фитнес и спорт | D › C › B | E | `#E4572E` / `#C6F432` | 108–117 |
| `real_estate` | Недвижимость и строительство | C › E › B | A | `#2E6F8E` / `#D9B26F` | 96–108 |
| `auto` | Авто: продажа и сервис | C › D › B | E | `#D62828` / `#C9CED6` | 104–117 |
| `it_saas` | IT, SaaS и HR-tech | C › B › A | — | `#2563EB` / `#7CF0C0` | 100–114 |
| `finance` | Финансы, банки и финтех | E › B › A | C | `#0F6E5A` / `#E6C068` | 95–106 |
| `ecommerce` | E-commerce и продавцы маркетплейсов | C › B › A | — | `#E8540F` / `#FFD43B` | 104–116 |
| `personal_brand` | Личный бренд, эксперт, коуч | D › B › C › F › G | A | `#0A7CFF` / `#FFD60A` | 99–112 |
| `travel` | Туризм и путешествия | B › C › D | A | `#0077B6` / `#F4A261` | 98–112 |
| `kids_family` | Дети и семья | B › D › C | E | `#2A8C82` / `#FFB703` | 98–110 |
| `religion_spirituality` | Религия, духовность, нравственность | G › F › E | A, C | `#2E8B6E` / `#E9D58A` | 96–104 |
| `default` | Другое / общий бизнес | B › A › D | — | `#0A7CFF` / `#FFD60A` | 99–110 |

### `education` — Образование и подготовка к экзаменам · Taʼlim va imtihonga tayyorlov · Білім беру және емтиханға дайындық
**Styles:** **E** — Scores, deadlines and rule changes are news + numbers — E's cover/data cards and literal captions are made for it; **B** — Step-by-step study tips and lists read clearly as iOS cards with literal words; **D** — A teacher on camera builds trust; keyword headlines keep the key rule on screen; **G** — A teacher's calm selfie explanation with the key term as an editorial stack — cheap to film, reads like a study note.  
**Avoid:** **C** — Whips and 3D spectacle compete with dense study content; spend the budget on real score screenshots instead.  
**Palette (no brand colours only):** `#1D5FD1` / `#F2B705` — notebook ink blue + school-pencil yellow; blue reads on light and dark; yellow only as highlighter fill under ink text.  
**Art direction:** matte paper and soft-touch plastic materials, clean desk-scale objects, soft daylight from upper left, gentle shadow, palette of ink blue, warm white and pencil yellow, calm and orderly, no text on objects. Props: stack of notebooks with a bookmark, sharpened pencil, answer sheet with bubbles (blank), hourglass, graduation cap, desk lamp, open book, stopwatch.  
**Music (B/C/E):** focused, light pulse, warm sub-bass, 100–110 BPM. Voice only: style A/D; announcing results or admission rules (exact words matter); sensitive topics like failed exams.  
**Techniques:** favour `number_roll`, `paper_section`, `section_number`, `strike_fix`, `selection_highlight`, `dark_checks`, `save_pill`; avoid `glitch_cta`, `curtain_reveal`, `mute_gag`. **Layouts:** `list`, `number`, `compare`, `media`, `stack`.  
**Materials:** real student score screenshots or certificates (with the student's written consent; names/IDs blurred); class or centre photos/B-roll (no children's faces without parental consent); schedule and price list; official source link/screenshot for any exam-rule news; licence for educational activity if the country requires it; logo.  
_Pass rates and 'average +N points' only from real records the client can show. Never promise admission._  
**Copy:** calm teacher: precise, encouraging, concrete; one rule per scene.  

- ru: hooks «3 ошибки, из-за которых теряют баллы на тесте» · «До экзамена 2 месяца: с чего начать» · «Почему зубрёжка не работает — 1 пример» · CTA: Запишитесь на пробный урок, Сохраните, Напишите в директ · avoid: гарантируем поступление, 100% сдача, лучший центр, без усилий
- uz: hooks «Testda ball yoʻqotadigan 3 ta xato» · «Imtihonga 2 oy qoldi: nimadan boshlash kerak» · «Yodlash nega ishlamaydi — 1 ta misol» · CTA: Sinov darsiga yoziling, Saqlab qoʻying, Direktga yozing · avoid: kafolatli qabul, 100% topshirasiz, eng zoʻr markaz, qiynalmasdan
- kk: hooks «ҰБТ-да балл жоғалтатын 3 қате» · «Емтиханға 2 ай қалды: неден бастау керек» · «Жаттау неге көмектеспейді — 1 мысал» · CTA: Сынақ сабаққа жазылыңыз, Сақтап қойыңыз, Директке жазыңыз · avoid: түсуге кепілдік, 100% тапсырасыз, ең үздік орталық, еш күшсіз

**Compliance:** No guarantees of admission, scores or grants. Results/testimonials must be real; student data shown only with consent (minors: parent consent). RU/KZ/UZ: comparative claims ('лучший', '№1') need proof; RU online ads need 'Реклама' marking + erid when paid. Exam-rule news must cite the official source on screen.  

### `online_school` — Онлайн-школы и курсы · Onlayn maktablar va kurslar · Онлайн мектептер мен курстар
**Styles:** **B** — Lesson UI, modules and progress are literally app screens — B's iOS cards and iPhone proof show the product honestly; **C** — For course launches: 3D hero moments for the promise, UI scenes for the real platform; **D** — The author's face sells the course; 3D keywords keep the structure visible.  
**Avoid:** **E** — News framing reads as reporting, not an offer — use it only for a real cohort-results report.  
**Palette (no brand colours only):** `#0F7B83` / `#FFC857` — deep teal + warm marigold, studious but friendly; teal reads on light and dark; marigold is a fill/pill colour under ink.  
**Art direction:** soft-touch matte plastic and frosted glass, laptop-and-desk scale objects, soft studio light with a teal rim light, palette of deep teal, warm white and marigold, tidy and modern, no text on objects. Props: laptop with a blank glowing screen, play button tile, progress ring, certificate scroll (blank), headphones, calendar tile, checklist board.  
**Music (B/C/E):** modern, motivated, clean sub-bass groove, 104–114 BPM. Voice only: style A/D; refund/terms explanations; student stories.  
**Techniques:** favour `iphone_proof`, `pull_out_phone`, `glove_tap`, `open_loop_ring`, `typing_dots`, `chest_widget`, `avatar_pill_cta`; avoid `curtain_reveal`, `mute_gag`. **Layouts:** `media`, `list`, `stack`, `head-side`, `compare`.  
**Materials:** screen recording of a real lesson/platform flow (5–15 s, no personal data); screenshots of modules/program; real student reviews as screenshots (with permission, names blurred if asked); author talking-head footage (for D / head modes); price & start date; logo.  
_No invented student counts, incomes or 'graduates earn X'. Income promises are the #1 ad-law risk for info products._  
**Copy:** practical mentor: show the product, the path and the result type — not lifestyle.  

- ru: hooks «Как выглядит урок у нас — покажу за 30 секунд» · «Почему бросают онлайн-курсы: 3 причины» · «Домашку проверяем за 24 часа — вот как» · CTA: Запишитесь, Заберите пробный урок, Напишите «курс» в директ · avoid: заработаете, гарантированный доход, пассивный доход, успей, последний шанс
- uz: hooks «Bizda dars qanday oʻtadi — 30 soniyada koʻrsataman» · «Onlayn kursni nega tashlab ketishadi: 3 sabab» · «Uy vazifasini 24 soatda tekshiramiz — mana qanday» · CTA: Yoziling, Sinov darsini oling, Direktga «kurs» deb yozing · avoid: pul topasiz, kafolatlangan daromad, passiv daromad, ulgurib qoling, oxirgi imkoniyat
- kk: hooks «Біздегі сабақ қалай өтеді — 30 секундта көрсетемін» · «Онлайн курсты неге тастап кетеді: 3 себеп» · «Үй тапсырмасын 24 сағатта тексереміз — міне, қалай» · CTA: Жазылыңыз, Сынақ сабақты алыңыз, Директке «курс» деп жазыңыз · avoid: табыс табасыз, кепілді табыс, пассивті табыс, үлгеріп қалыңыз, соңғы мүмкіндік

**Compliance:** No income or employment guarantees. Reviews must be real and attributable; no staged 'student' testimonials. Fake urgency (false countdowns, 'last seats' when untrue) is misleading advertising. RU: paid placements need 'Реклама' marking + erid; licence mention if the client issues state-standard certificates.  

### `food_cafe` — Кафе, рестораны и доставка еды · Kafe, restoran va taom yetkazib berish · Кафе, мейрамхана және тамақ жеткізу
**Styles:** **B** — Menu cards, prices and real food photos in media layouts with a warm bed — appetite needs real images; **D** — The chef or owner on camera adds warmth and authenticity; keywords carry the dish name; **C** — For openings and new-menu launches: one 3D ingredient moment + UI price/menu cards.  
**Avoid:** **A** — Voice-only faceless 3D can't make food look edible; generated dishes look fake; **E** — A cold white news page kills appetite.  
**Palette (no brand colours only):** `#C8452A` / `#F2C14E` — paprika + saffron, warm and appetising; paprika reads on light and dark; saffron is a fill under ink (price pills, highlights).  
**Art direction:** matte glazed ceramic, natural linen and warm wood surfaces, soft warm window light from the left, gentle steam, appetising warm palette of paprika, saffron and cream, single ingredient or utensil, no text. Props: cast-iron kazan, ceramic bowl with lid, single tomato and herbs, wooden spoon, teapot and piala, takeaway paper bag (unbranded), spice pinch bowls, bread tandyr-style loaf.  
**Music (B/C/E):** warm, cosy lo-fi pulse, round sub-bass, 96–108 BPM. Voice only: style A/D; owner/chef story moments with real kitchen sound you want to keep.  
**Techniques:** favour `number_roll`, `iphone_proof`, `pull_out_phone`, `sticker_title`, `chest_widget`, `save_pill`, `lens_blur`; avoid `glitch_cta`, `curtain_reveal`, `dark_checks`. **Layouts:** `media`, `visual-top`, `list`, `number`, `head-side`.  
**Materials:** real dish photos or 5–10 s B-roll (vertical, daylight, steam); menu / price list (current); interior & exterior shots, address/map screenshot; delivery-app screenshot only if the client wants to show their own listing; chef/owner talking-head footage (D / head modes); logo.  
_Every dish shown must be on the real menu at the stated price. Generated images only for ingredients/props, never as the dish._  
**Copy:** warm host: sensory but concrete (time, ingredient, price), no superlatives.  

- ru: hooks «Наш плов готовится 4 часа. Вот почему» · «Новое в меню: показываем, из чего это» · «Бизнес-ланч до 15:00 — что входит» · CTA: Забронируйте стол, Закажите доставку, Приходите · avoid: самый вкусный в городе, лучший, натуральный 100%, остатки
- uz: hooks «Oshimiz 4 soat tayyorlanadi. Mana nega» · «Menyuda yangi taom: nimadan tayyorlanishini koʻrsatamiz» · «Biznes-lanch 15:00 gacha — ichida nima bor» · CTA: Stol band qiling, Yetkazib berishga buyurtma bering, Keling · avoid: shahardagi eng mazali, eng zoʻr, 100% tabiiy, qoldiq
- kk: hooks «Біздің палау 4 сағат дайындалады. Себебі мынада» · «Мәзірде жаңа тағам: неден жасалатынын көрсетеміз» · «Бизнес-ланч 15:00-ге дейін — ішінде не бар» · CTA: Үстел брондаңыз, Жеткізуге тапсырыс беріңіз, Келіңіз · avoid: қаладағы ең дәмді, ең үздік, 100% табиғи, қалдық

**Compliance:** Alcohol, tobacco, hookah and vapes are excluded from reels — don't show or mention them even if served. Prices and offers must match the real menu; state conditions of promotions. 'Halal' only if the client confirms certification. Superlatives ('самый вкусный') need proof under ad laws — avoid.  

### `bakery` — Кондитерские и пекарни · Qandolatchilik va novvoyxona · Кондитерлік және наубайхана
**Styles:** **B** — Process steps, flavour lists and order cards with real cake photos; soft bed fits the cosy mood; **D** — The baker on camera with flour-on-the-table authenticity; keywords name the flavour or step; **C** — Seasonal launches: one 3D ingredient hero + UI order/price cards.  
**Avoid:** **A** — Faceless 3D can't sell taste; generated cakes look plastic; **E** — Editorial news page is too dry for a treat.  
**Palette (no brand colours only):** `#A0522D` / `#F3D9B1` — cinnamon crust + cream; cinnamon reads on light and dark; cream is a fill under ink.  
**Art direction:** soft matte ceramic and powdered-sugar textures, light wood and parchment surfaces, soft diffused morning light, warm palette of cinnamon, cream and blush, airy and delicate, no text. Props: whisk, rolling pin, flour sack (unbranded), cake stand with dome (empty), single strawberry, piping bag, croissant, cake box with ribbon (unbranded).  
**Music (B/C/E):** soft, sweet, cosy pad with gentle pulse, 96–106 BPM. Voice only: style A/D; ASMR-like process shots where real sound (crust crackle) is the point.  
**Techniques:** favour `paper_section`, `section_number`, `number_roll`, `save_pill`, `selection_highlight`, `lens_blur`, `typing_dots`; avoid `glitch_cta`, `curtain_reveal`, `jump_zoom`. **Layouts:** `media`, `visual-top`, `list`, `compare`, `stack`.  
**Materials:** real product photos / process B-roll (vertical, daylight); price list and ordering terms (lead time, deposit); real order chat screenshots (with permission, names hidden); baker talking-head footage (D / head modes); logo.  
_Portfolio = only the client's real cakes. Allergens (nuts, gluten, lactose) mentioned if a product is featured._  
**Copy:** warm craft: process, ingredients, lead time; sensory but honest.  

- ru: hooks «Торт на заказ: от эскиза до коробки» · «Почему наш хлеб бродит 18 часов» · «3 вкуса, которые чаще берут на день рождения» · CTA: Закажите торт, Напишите дату праздника, Сохраните · avoid: без сахара, полезный торт, самый вкусный, 100% натуральный
- uz: hooks «Buyurtma tort: eskizdan qutigacha» · «Nonimiz nega 18 soat achitiladi» · «Tugʻilgan kunga eng koʻp tanlanadigan 3 taʼm» · CTA: Tort buyurtma qiling, Bayram sanasini yozing, Saqlab qoʻying · avoid: shakarsiz, foydali tort, eng mazali, 100% tabiiy
- kk: hooks «Тапсырыспен торт: эскизден қорапқа дейін» · «Нанымыз неге 18 сағат ашытылады» · «Туған күнге ең жиі таңдалатын 3 дәм» · CTA: Торт тапсырыс беріңіз, Мереке күнін жазыңыз, Сақтап қойыңыз · avoid: қантсыз, пайдалы торт, ең дәмді, 100% табиғи

**Compliance:** 'Без сахара / полезный / ПП' only if literally true and the client confirms; health claims for food are regulated. Alcohol-containing desserts: don't advertise the alcohol. Show allergens when relevant. Prices and lead times must be current.  

### `beauty` — Салоны красоты и косметология · Goʻzallik salonlari va kosmetologiya · Сұлулық салондары және косметология
**Styles:** **D** — The master on camera = trust; keyword headlines name the procedure while the face stays the brand; **B** — Price lists, procedure steps and consented before/after in compare layouts read cleanly as iOS cards; **C** — New-service launches: elegant 3D product moments + UI booking cards.  
**Avoid:** **E** — News/data page is cold for a sensory, personal service; **A** — No faces may be generated, so faceless 3D can't show results; use it only for skincare explainers.  
**Palette (no brand colours only):** `#B2456E` / `#E9C9B8` — berry + nude, refined rather than candy pink; berry reads on light and dark; nude is a fill under ink.  
**Art direction:** satin and frosted-glass cosmetic materials, soft beauty-dish light with a gentle highlight, clean marble or travertine surface, palette of berry, nude and warm ivory, minimal and premium, no text. Props: frosted glass serum bottle (unbranded), nail polish bottle, comb and scissors, cream jar, jade roller, towel roll, flower petal, mirror compact.  
**Music (B/C/E):** smooth, airy, soft sub-bass with light shimmer, 98–108 BPM. Voice only: style A/D; injection/medical-cosmetology topics; client consent/result stories.  
**Techniques:** favour `lens_blur`, `sticker_title`, `chest_widget`, `dark_checks`, `selection_highlight`, `avatar_pill_cta`, `strike_fix`; avoid `glitch_cta`, `curtain_reveal`, `mute_gag`. **Layouts:** `head-side`, `compare`, `media`, `list`, `head`.  
**Materials:** real before/after photos ONLY with the client's written consent (same light/angle, no retouching); salon interior B-roll; price list; certificates/diplomas of masters; medical licence for cosmetology procedures; real reviews as screenshots (with permission); master talking-head footage; logo.  
_Before/after without consent is not usable. Do not retouch results. Injections, peels, laser = medical services in RU/KZ/UZ._  
**Copy:** caring expert: honest about duration, sensation and aftercare; no miracle language.  

- ru: hooks «Окрашивание за 1 визит: что реально, а что нет» · «3 вещи, которые портят маникюр уже на 3-й день» · «Сколько длится процедура и что вы почувствуете» · CTA: Запишитесь, Выберите время, Напишите в директ · avoid: омоложение на 10 лет, навсегда, без боли гарантированно, идеальная кожа
- uz: hooks «Bir tashrifda soch boʻyash: nima real, nima yoʻq» · «Manikyurni 3-kundayoq buzadigan 3 narsa» · «Muolaja qancha davom etadi va nimani his qilasiz» · CTA: Yoziling, Vaqt tanlang, Direktga yozing · avoid: 10 yilga yoshartirish, umrbod, kafolatli ogʻriqsiz, mukammal teri
- kk: hooks «Бір келгенде шаш бояу: не шын, не жоқ» · «Маникюрді 3-күні-ақ бұзатын 3 нәрсе» · «Процедура қанша уақыт алады және не сезесіз» · CTA: Жазылыңыз, Уақыт таңдаңыз, Директке жазыңыз · avoid: 10 жасқа жасарту, мәңгілік, ауыртпайтынына кепілдік, мінсіз тері

**Compliance:** Cosmetology with injections/hardware = medical service: licence + RU warning 'Имеются противопоказания. Необходима консультация специалиста' (see medicine). Before/after only with written consent; no AI-made or retouched results. No permanent-result or age-reversal promises.  

### `medicine_dental` — Медицина и стоматология · Tibbiyot va stomatologiya · Медицина және стоматология
**Styles:** **D** — A real doctor on camera is the strongest trust signal; keyword headlines anchor the medical term; **B** — Calm iOS cards for steps, myths vs facts and price-list transparency; **E** — Health statistics and 'what changed' explainers with sources on screen.  
**Avoid:** **C** — Whips, glitches and glossy spectacle read as hype for health — trust drops.  
**Palette (no brand colours only):** `#0B7A75` / `#9ED8DB` — clinical teal + soft aqua; calm, not hospital-cold; teal reads on light and dark; aqua is a fill under ink. No red-cross red (protected emblem).  
**Art direction:** clean ceramic-white and soft frosted-glass materials, stylised non-anatomical forms, soft even clinical daylight, palette of teal, aqua and warm white, calm and hygienic, no text. Props: stylised ceramic tooth model, toothbrush, dental mirror, clipboard (blank), stethoscope, calendar tile, shield icon, water glass.  
**Music (B/C/E):** calm, steady, very soft pad, 95–104 BPM. Voice only: style A/D; diagnoses, pain, children's treatment, any patient story — default to voice-only when in doubt.  
**Techniques:** favour `strike_fix`, `selection_highlight`, `paper_section`, `section_number`, `chest_widget`, `number_roll`, `dark_checks`; avoid `glitch_cta`, `curtain_reveal`, `jump_zoom`, `mute_gag`, `hero_word`. **Layouts:** `head-side`, `list`, `compare`, `stack`, `media`.  
**Materials:** doctor talking-head footage; clinic licence (number) and doctor's credentials; price list; clinic interior/equipment B-roll (no patients identifiable); before/after or X-ray images ONLY with the patient's written consent and anonymised; logo.  
_No patient faces/data without written consent. Equipment claims ('новейший') only if documented._  
**Copy:** doctor explaining to a friend: calm, precise, no fear-mongering, no promises.  

- ru: hooks «Больно ли ставить имплант? Отвечает врач» · «3 признака, что пора к стоматологу, даже если не болит» · «Чем отличается чистка от отбеливания» · CTA: Запишитесь на консультацию, Позвоните, Сохраните · avoid: вылечим, гарантия результата, без боли 100%, навсегда, чудо
- uz: hooks «Implant qoʻydirish ogʻriqlimi? Shifokor javob beradi» · «Ogʻrimasa ham stomatologga borish kerakligining 3 belgisi» · «Tish tozalash oqartirishdan nimasi bilan farq qiladi» · CTA: Konsultatsiyaga yoziling, Qoʻngʻiroq qiling, Saqlab qoʻying · avoid: davolaymiz kafolat, natija kafolati, 100% ogʻriqsiz, umrbod, moʻjiza
- kk: hooks «Имплант қойғызу ауырта ма? Дәрігер жауап береді» · «Ауырмаса да стоматологқа бару керек 3 белгі» · «Тіс тазалау мен ағартудың айырмашылығы неде» · CTA: Кеңеске жазылыңыз, Қоңырау шалыңыз, Сақтап қойыңыз · avoid: емдеуге кепілдік, нәтиже кепілдігі, 100% ауыртпайды, мәңгілік, ғажайып

**Compliance:** No guarantees of cure/result; no fear appeals. RU (38-ФЗ ст.24): medical services ads carry 'ИМЕЮТСЯ ПРОТИВОПОКАЗАНИЯ. НЕОБХОДИМО ПРОКОНСУЛЬТИРОВАТЬСЯ СО СПЕЦИАЛИСТОМ' — in video ≥ 5 s and ≥ 7 % of frame area; KZ/UZ have similar medical-ad rules — confirm with the client. Show licence number/legal name where required. Patient testimonials and before/after only with written consent; never AI-generated. No red-cross emblem.  

### `pharmacy` — Аптеки · Dorixonalar · Дәріханалар
**Styles:** **B** — Service info (hours, delivery, app ordering) as clean iOS cards and real app screens; **E** — Seasonal health info and storage rules as sourced, sober data cards; **A** — Faceless, calm voice-only explainers (how to store medicines, first-aid kit) without showing products.  
**Avoid:** **C** — Hype energy around medicines is inappropriate and risky.  
**Palette (no brand colours only):** `#138A52` / `#CDEFD9` — pharmacy green + mint; familiar in the region without copying a chain; green reads on light and dark; mint is a fill under ink.  
**Art direction:** clean matte white plastic and frosted glass, generic unbranded packaging, soft even daylight, palette of pharmacy green, mint and warm white, orderly and reassuring, no text. Props: first-aid kit box (unbranded), generic blister pack (no labels), thermometer, measuring spoon, pill organiser, delivery bag (unbranded), thermometer for fridge, water glass.  
**Music (B/C/E):** calm, light pad, 95–104 BPM. Voice only: style A/D; any mention of a specific medicine or symptoms.  
**Techniques:** favour `paper_section`, `section_number`, `dark_checks`, `iphone_proof`, `pull_out_phone`, `save_pill`, `strike_fix`; avoid `glitch_cta`, `curtain_reveal`, `jump_zoom`, `hero_word`, `mute_gag`. **Layouts:** `list`, `stack`, `media`, `number`, `compare`.  
**Materials:** pharmacy licence number / legal name; store photos (no customers identifiable); app/website ordering screen recording; addresses & hours; pharmacist talking-head footage (optional, for D); logo.  
_Talk about service, not medicines. Never name or picture a prescription drug; OTC/BAД ads have special warnings._  
**Copy:** reliable neighbour: practical rules, service facts, zero medical advice.  

- ru: hooks «Как хранить лекарства летом: 3 правила» · «Что положить в аптечку в дорогу — список» · «Заказ онлайн, забрать через час: как это работает» · CTA: Закажите онлайн, Сохраните список, Найдите ближайшую аптеку · avoid: вылечит, лучшее средство, безопасно для всех, без рецепта любое
- uz: hooks «Yozda dorilarni qanday saqlash kerak: 3 qoida» · «Safarga dori qutisiga nima solish kerak — roʻyxat» · «Onlayn buyurtma, bir soatda olib ketish: qanday ishlaydi» · CTA: Onlayn buyurtma bering, Roʻyxatni saqlang, Eng yaqin dorixonani toping · avoid: davolaydi, eng yaxshi vosita, hammaga xavfsiz, retseptsiz har qanday
- kk: hooks «Жазда дәріні қалай сақтау керек: 3 ереже» · «Сапарға дәрі қобдишасына не салу керек — тізім» · «Онлайн тапсырыс, бір сағатта алып кету: қалай жұмыс істейді» · CTA: Онлайн тапсырыс беріңіз, Тізімді сақтаңыз, Ең жақын дәріхананы табыңыз · avoid: емдейді, ең жақсы құрал, бәріне қауіпсіз, рецептсіз кез келген

**Compliance:** No prescription-drug advertising; no specific medicines or dosages in reels. RU: OTC ads need the contraindications warning (≥ 5 s, ≥ 7 % frame in video); BAД ads need 'НЕ ЯВЛЯЕТСЯ ЛЕКАРСТВЕННЫМ СРЕДСТВОМ'. KZ/UZ: similar restrictions — confirm with the client. No treatment claims or medical advice; refer to a doctor/pharmacist. No red-cross emblem.  

### `fitness` — Фитнес и спорт · Fitnes va sport · Фитнес және спорт
**Styles:** **D** — The coach on camera brings energy and credibility; keyword headlines name the exercise or rule; **C** — Most energetic style: whips, 3D equipment heroes and UI counters for programs; **B** — Program lists, schedules and counters as clean UI cards.  
**Avoid:** **E** — A static white news page lacks the energy the niche expects.  
**Palette (no brand colours only):** `#E4572E` / `#C6F432` — sport orange + volt lime; orange reads on light and dark; lime is a fill under ink only (never lime text on white).  
**Art direction:** rubberised matte and brushed-steel materials, hard key light with a crisp rim light, dark gym-floor or concrete surface, palette of sport orange, graphite and volt lime, dynamic three-quarter angle, no text. Props: kettlebell, dumbbell pair, jump rope, boxing glove, yoga mat roll, stopwatch, water bottle (unbranded), resistance band.  
**Music (B/C/E):** driving, punchy sub-bass groove, 108–117 BPM. Voice only: style A/D; technique breakdowns where the coach's cues must be heard; health/injury topics.  
**Techniques:** favour `jump_zoom`, `section_number`, `number_roll`, `sticker_title`, `hero_word`, `dark_checks`, `open_loop_ring`; avoid `paper_section`, `mute_gag`, `curtain_reveal`. **Layouts:** `head`, `head-side`, `number`, `list`, `visual-top`.  
**Materials:** coach/gym talking-head and training B-roll (vertical, consent from anyone visible); schedule and membership prices; coach certificates; real client progress only with written consent (no body shaming); gym interior photos; logo.  
_No transformation promises with timelines. Body before/after only with consent; prefer performance metrics (reps, time) over weight._  
**Copy:** energetic coach: direct, short commands, specific numbers (sets, reps, minutes).  

- ru: hooks «3 упражнения, которые делают неправильно в каждом зале» · «Сколько раз в неделю тренироваться новичку» · «Первая тренировка у нас: что будет по минутам» · CTA: Приходите на пробную, Запишитесь, Сохраните тренировку · avoid: минус 10 кг за неделю, без диет и усилий, жиросжигатель, гарантия
- uz: hooks «Har bir zalda notoʻgʻri bajariladigan 3 ta mashq» · «Yangi boshlovchi haftasiga necha marta shugʻullanishi kerak» · «Bizdagi birinchi mashgʻulot: daqiqama-daqiqa» · CTA: Sinov mashgʻulotiga keling, Yoziling, Mashqni saqlang · avoid: bir haftada minus 10 kg, parhezsiz va harakatsiz, yogʻ yoqar, kafolat
- kk: hooks «Әр залда қате жасалатын 3 жаттығу» · «Жаңадан бастаған адам аптасына неше рет жаттығуы керек» · «Біздегі алғашқы жаттығу: минут сайын не болады» · CTA: Сынақ жаттығуға келіңіз, Жазылыңыз, Жаттығуды сақтаңыз · avoid: бір аптада минус 10 кг, диетасыз әрі күшсіз, май жаққыш, кепілдік

**Compliance:** No weight-loss guarantees or timelines. Sports nutrition/BAД: not advertised in these reels (RU BAД warning otherwise). Consent from every identifiable person in footage. No dangerous technique shown as recommended.  

### `real_estate` — Недвижимость и строительство · Koʻchmas mulk va qurilish · Жылжымайтын мүлік және құрылыс
**Styles:** **C** — 3D architectural objects for the vision + UI cards for prices, layouts and mortgage terms; **E** — Price per m², market data and 'what changed' explainers with sources; **B** — Checklists (what to ask the developer), layouts and payment plans as iOS cards.  
**Avoid:** **A** — Voice-only 3D can't show the real building or floor plan; fine only for abstract mortgage explainers.  
**Palette (no brand colours only):** `#2E6F8E` / `#D9B26F` — slate blue + brass/sand, solid and premium; slate blue reads on light and dark; brass is a fill under ink.  
**Art direction:** architectural-model materials: matte white plaster, light oak, brushed brass and clear glass, soft late-afternoon sunlight with long shadows, palette of slate blue, sand and warm white, calm premium mood, no text. Props: white architectural model of a residential block, house keys on a ring, floor-plan blueprint roll, measuring tape, door with brass handle, window frame, hard hat, calculator.  
**Music (B/C/E):** confident, spacious, slow sub-bass, 96–108 BPM. Voice only: style A/D; legal/contract explanations; price and mortgage terms (exact words matter).  
**Techniques:** favour `number_roll`, `iphone_proof`, `pull_out_phone`, `dark_checks`, `strike_fix`, `glove_tap`, `open_loop_ring`; avoid `glitch_cta`, `mute_gag`. **Layouts:** `media`, `number`, `compare`, `list`, `visual-top`.  
**Materials:** official renders / real photos / construction-progress B-roll; floor plans; price list and payment/mortgage terms with the bank's name; permits / project declaration link (RU: наш.дом.рф), developer legal name; agent/manager talking-head footage; logo.  
_Renders must be labelled as visualisation. Price 'от' must be real; mortgage rates only with the bank and conditions._  
**Copy:** trustworthy advisor: numbers, terms, dates; no hype about price growth.  

- ru: hooks «Сколько стоит м² в нашем районе сейчас — цифры» · «3 вопроса застройщику до подписания договора» · «Планировка 2+1: где теряются метры» · CTA: Запишитесь на просмотр, Получите планировки, Позвоните · avoid: цены вырастут на, выгодная инвестиция гарантирована, последние квартиры, элитный
- uz: hooks «Hozir tumanimizda 1 m² qancha turadi — raqamlar» · «Shartnomani imzolashdan oldin quruvchiga 3 savol» · «2+1 planirovka: metrlar qayerda yoʻqoladi» · CTA: Koʻrishga yoziling, Planirovkalarni oling, Qoʻngʻiroq qiling · avoid: narx albatta oshadi, kafolatli investitsiya, oxirgi kvartiralar, elita
- kk: hooks «Қазір ауданымызда 1 м² қанша тұрады — сандар» · «Келісімшартқа қол қоймас бұрын құрылыс салушыға 3 сұрақ» · «2+1 жоспар: метрлер қайда жоғалады» · CTA: Көруге жазылыңыз, Жоспарларды алыңыз, Қоңырау шалыңыз · avoid: баға міндетті түрде өседі, кепілді инвестиция, соңғы пәтерлер, элиталық

**Compliance:** No promises of price growth or investment return. Mortgage/installment terms follow finance rules: lender name, rate conditions, all cost-affecting terms. RU shared construction: developer name + project declaration site required in ads. Renders labelled as visualisation; 'last flats' only if true.  

### `auto` — Авто: продажа и сервис · Avto: savdo va servis · Авто: сату және сервис
**Styles:** **C** — Energetic 3D car-part heroes + UI price/spec cards; whips suit the niche; **D** — A mechanic or dealer on camera explains with authority; keywords name the part or price; **B** — Checklists (what to inspect), service prices and booking steps.  
**Avoid:** **E** — Static news page undersells motion; only for market-price news with sources.  
**Palette (no brand colours only):** `#D62828` / `#C9CED6` — racing red + brushed steel; red reads on light and dark; steel is a fill under ink.  
**Art direction:** glossy automotive paint, brushed aluminium and rubber materials, studio car-photography lighting with long softbox reflections, dark graphite floor, palette of racing red, steel and graphite, low three-quarter angle, no text. Props: alloy wheel with tyre, brake disc and caliper, car key fob (unbranded), spark plug, engine oil can (unbranded), wrench, headlight unit, turbocharger.  
**Music (B/C/E):** tight, driving, deep sub-bass, 104–117 BPM. Voice only: style A/D; diagnostic explanations where engine sound is part of the proof.  
**Techniques:** favour `number_roll`, `jump_zoom`, `dark_checks`, `section_number`, `strike_fix`, `pull_out_phone`, `curtain_reveal`; avoid `paper_section`, `mute_gag`, `save_pill`. **Layouts:** `media`, `number`, `visual-top`, `compare`, `list`.  
**Materials:** real car photos/B-roll (stock on site, service bay process); price list / car price with conditions; credit/lease partner name and terms (if mentioned); mechanic/dealer talking-head footage; real review screenshots (with permission); logo.  
_Car brands/models only when the client really sells/services them. Blur number plates and customers._  
**Copy:** straight-talking mechanic: practical, numbers, no macho hype.  

- ru: hooks «Что проверить в б/у авто за 10 минут» · «Замена масла: когда на самом деле пора» · «Почему стучит подвеска — 3 частые причины» · CTA: Запишитесь на сервис, Приезжайте на тест-драйв, Напишите в директ · avoid: самые низкие цены, кредит без отказа, гонка, лучший сервис
- uz: hooks «Ishlatilgan mashinada 10 daqiqada nimani tekshirish kerak» · «Moy almashtirish: aslida qachon vaqti keladi» · «Podveska nega taqillaydi — 3 ta koʻp uchraydigan sabab» · CTA: Servisga yoziling, Test-drayvga keling, Direktga yozing · avoid: eng past narxlar, rad etilmaydigan kredit, poyga, eng zoʻr servis
- kk: hooks «Қолданылған көлікте 10 минутта нені тексеру керек» · «Май ауыстыру: шын мәнінде қашан уақыты келеді» · «Аспа неге тарсылдайды — 3 жиі себеп» · CTA: Сервиске жазылыңыз, Тест-драйвқа келіңіз, Директке жазыңыз · avoid: ең төмен бағалар, бас тартусыз несие, жарыс, ең үздік сервис

**Compliance:** Never depict or encourage dangerous driving. Car-loan/lease offers follow finance rules (lender, all cost conditions); 'кредит без отказа' is misleading. Price 'от' with conditions; no 'lowest price' without proof. Third-party car brands only when the client is authorised/really sells them.  

### `it_saas` — IT, SaaS и HR-tech · IT, SaaS va HR-tech · IT, SaaS және HR-tech
**Styles:** **C** — Product promos: cinematic 3D for the pain/promise, real UI scenes for the product; **B** — Feature tutorials and objection handling: iPhone proof, glove taps, chat bubbles on real screens; **A** — Faceless tech/AI explainers are A's home turf; strong keywords + 3D metaphors.  
**Palette (no brand colours only):** `#2563EB` / `#7CF0C0` — product blue + signal mint, no purple AI-gradient; blue reads on light and dark; mint is a fill under ink (status pills, highlights).  
**Art direction:** glossy soft-touch plastic and frosted glass with subtle inner glow, clean studio light with a cool rim light, palette of product blue, mint and graphite on neutral, precise and minimal, no text. Props: glass app tile, toggle switch, calendar tile, clock, server block, chat bubble, gear, shield with checkmark, puzzle piece, notification bell.  
**Music (B/C/E):** clean, modern, subtle sub-bass groove, 100–114 BPM. Voice only: style A/D; detailed tutorials where clicks/SFX would distract.  
**Techniques:** favour `iphone_proof`, `pull_out_phone`, `glove_tap`, `chest_widget`, `typing_dots`, `number_roll`, `strike_fix`, `hero_word`; avoid `curtain_reveal`, `mute_gag`. **Layouts:** `media`, `stack`, `compare`, `number`, `list`.  
**Materials:** product screenshots (light theme, demo data); screen recording of the key flow (5–15 s, no notifications); real metrics screenshot if a number is spoken (blur private data); client logos only with permission; founder talking-head footage (D / head modes); logo.  
_Demo accounts with fake-but-neutral data only; never real employee/customer data on screen._  
**Copy:** product person: pain in numbers → the feature on screen → result; no buzzwords.  

- ru: hooks «Табель вручную съедает 6 часов в неделю. Покажем, как иначе» · «Как это выглядит в приложении — 3 нажатия» · «HR-отчёт за 1 клик: что внутри» · CTA: Попробуйте бесплатно, Запишитесь на демо, Напишите «демо» · avoid: инновационное решение, революционный, в современном мире, №1 на рынке
- uz: hooks «Tabelni qoʻlda yuritish haftasiga 6 soat oladi. Boshqa yoʻlini koʻrsatamiz» · «Ilovada qanday koʻrinadi — 3 ta bosish» · «1 bosishda HR-hisobot: ichida nima bor» · CTA: Bepul sinab koʻring, Demoga yoziling, «Demo» deb yozing · avoid: innovatsion yechim, inqilobiy, zamonaviy dunyoda, bozorda №1
- kk: hooks «Табельді қолмен жүргізу аптасына 6 сағат алады. Басқа жолын көрсетеміз» · «Қосымшада қалай көрінеді — 3 басу» · «1 басуда HR-есеп: ішінде не бар» · CTA: Тегін сынап көріңіз, Демоға жазылыңыз, «Демо» деп жазыңыз · avoid: инновациялық шешім, революциялық, қазіргі әлемде, нарықта №1

**Compliance:** '№1'/'лучший'/'первый' claims need documented proof. Customer logos and case numbers only with permission and real data. No personal data in screenshots (labour/HR data is sensitive). 'Free' must state limits (trial length, plan).  

### `finance` — Финансы, банки и финтех · Moliya, banklar va fintech · Қаржы, банктер және финтех
**Styles:** **E** — Rates, inflation and 'what changed' explainers with sources — sober data cards build trust; **B** — Calm iOS cards: calculators, step-by-step app flows, myth vs fact; **A** — Voice-only, faceless concept explainers (what is a deposit, how compound interest works).  
**Avoid:** **C** — Whips, glitches and 3D spectacle read as hype — dangerous for money topics.  
**Palette (no brand colours only):** `#0F6E5A` / `#E6C068` — deep emerald + muted gold; trustworthy, not flashy; emerald reads on light and on dark at large sizes (headline/number scale); gold is a fill under ink. Don't mimic a specific bank's brand colours.  
**Art direction:** matte ceramic and brushed-metal materials, precise soft studio light, neutral stone surface, palette of deep emerald, muted gold and warm grey, calm and trustworthy, no text. Props: bank card (blank, unbranded), piggy bank, stacked coins (neutral, no currency marks), calculator, safe door, shield, line-chart tile (no numbers), wallet.  
**Music (B/C/E):** calm, steady, minimal pad, 95–106 BPM. Voice only: style A/D; any rate, fee or legal condition is being read out; debt/hardship topics.  
**Techniques:** favour `number_roll`, `strike_fix`, `selection_highlight`, `paper_section`, `dark_checks`, `iphone_proof`, `save_pill`; avoid `glitch_cta`, `curtain_reveal`, `jump_zoom`, `hero_word`, `rgb_ghost`, `mute_gag`. **Layouts:** `number`, `list`, `compare`, `stack`, `media`.  
**Materials:** licence number and full legal name (mandatory on the end card); product terms: rate, fees, term, all conditions affecting cost (RU: ПСК; KZ: ГЭСВ/ЖТСМ); app screen recording (demo account); official source for any macro number (central bank, statistics agency); compliance/legal approval contact; logo.  
_Every number on screen comes from the client's official terms or a cited source — no examples presented as offers._  
**Copy:** plain-language explainer: neutral, exact, no FOMO.  

- ru: hooks «Депозит или облигации: разница простыми словами» · «Что такое ПСК и почему смотреть надо на неё» · «3 вопроса, которые стоит задать до кредита» · CTA: Узнайте условия, Рассчитайте в приложении, Сохраните · avoid: гарантированный доход, без рисков, кредит без отказа, быстрые деньги, пассивный доход
- uz: hooks «Depozit yoki obligatsiya: oddiy tilda farqi» · «Kredit olishdan oldin beriladigan 3 savol» · «Yillik foiz va haqiqiy toʻlov: nimaga qarash kerak» · CTA: Shartlarni bilib oling, Ilovada hisoblang, Saqlab qoʻying · avoid: kafolatlangan daromad, xatarsiz, rad etilmaydigan kredit, tez pul, passiv daromad
- kk: hooks «Депозит пе, облигация ма: қарапайым тілмен айырмашылығы» · «Несие алмас бұрын қоятын 3 сұрақ» · «ЖТСМ деген не және неге соған қарау керек» · CTA: Шарттарды біліңіз, Қосымшада есептеңіз, Сақтап қойыңыз · avoid: кепілді табыс, тәуекелсіз, бас тартусыз несие, жылдам ақша, пассивті табыс

**Compliance:** Show licence number + legal name; get the client's legal/compliance approval before publishing. No guaranteed returns, 'no risk', or past performance as a promise; investment content needs a risk disclaimer. Credit ads: state ALL cost-affecting conditions (RU 38-ФЗ ст.28: if one is named, all must be; ПСК). KZ/UZ have equivalent rules — confirm. No crypto/forex/betting promotion; no fabricated rates or screenshots.  

### `ecommerce` — E-commerce и продавцы маркетплейсов · E-commerce va marketpleys sotuvchilari · E-commerce және маркетплейс сатушылары
**Styles:** **C** — The product as a 3D hero + UI cards for price, reviews and listing — strong for product promos; **B** — Seller tips, listing checklists and real stats screenshots as iOS cards; **A** — Faceless explainers of seller tactics with punchy keywords.  
**Palette (no brand colours only):** `#E8540F` / `#FFD43B` — shop orange + price-tag yellow; avoid marketplace brand purples/blues; orange reads on light and dark at headline sizes; yellow is a fill under ink (price tags, pills).  
**Art direction:** glossy product-photography materials, cardboard and tissue-paper packaging, bright clean studio light with soft shadow, palette of shop orange, warm white and tag yellow, crisp and commercial, no text. Props: shipping box (unbranded), price tag, shopping bag (unbranded), star rating tile (no numbers), delivery truck toy-like, barcode tag (blank), phone with blank shop screen, cart.  
**Music (B/C/E):** upbeat, bright, bouncy sub-bass, 104–116 BPM. Voice only: style A/D; detailed analytics walkthroughs.  
**Techniques:** favour `number_roll`, `iphone_proof`, `pull_out_phone`, `glove_tap`, `strike_fix`, `dark_checks`, `save_pill`; avoid `curtain_reveal`, `mute_gag`. **Layouts:** `media`, `compare`, `number`, `list`, `visual-top`.  
**Materials:** real product photos / unboxing B-roll; listing screenshots of the client's own store; real sales/analytics screenshot if a number is spoken (blur private data); real customer reviews as screenshots; price & promo terms; logo.  
_Marketplace UI only as the client's own real screenshots; never fake a listing, rating or sales number._  
**Copy:** practical seller: specific mistakes and fixes, real numbers, no 'easy money'.  

- ru: hooks «Почему карточка товара не продаёт: 3 причины» · «Фото для маркетплейса на телефон — показываем настройки» · «Откуда берутся возвраты и как их снизить» · CTA: Закажите, Сохраните чек-лист, Напишите «аудит» · avoid: лёгкие деньги, миллион за месяц, скидка 90%, оригинал 100%
- uz: hooks «Tovar kartochkasi nega sotmaydi: 3 sabab» · «Marketpleys uchun telefonda surat — sozlamalarni koʻrsatamiz» · «Qaytarishlar qayerdan chiqadi va ularni qanday kamaytirish mumkin» · CTA: Buyurtma bering, Chek-listni saqlang, «Audit» deb yozing · avoid: oson pul, bir oyda million, 90% chegirma, 100% original
- kk: hooks «Тауар карточкасы неге сатпайды: 3 себеп» · «Маркетплейске телефонмен фото — баптауларды көрсетеміз» · «Қайтарулар қайдан шығады және оларды қалай азайтуға болады» · CTA: Тапсырыс беріңіз, Чек-листті сақтаңыз, «Аудит» деп жазыңыз · avoid: оңай ақша, бір айда миллион, 90% жеңілдік, 100% түпнұсқа

**Compliance:** Discounts only from a real previous price; state promo conditions and dates. No fake reviews, ratings or sales numbers. Marketplace names are trademarks: mention factually, no implied partnership. Excluded categories: alcohol, tobacco/vapes, weapons, counterfeit goods.  

### `personal_brand` — Личный бренд, эксперт, коуч · Shaxsiy brend, ekspert, kouch · Жеке бренд, сарапшы, коуч
**Styles:** **D** — The face IS the brand; A keywords and 3D beside the speaker make an expert's talk premium; **B** — The reference look for experts (iOS keynote): literal words, profile-card CTA, chat objections; **C** — Talking head at hook/CTA with cinematic 3D + UI between — for launches and big ideas; **F** — footage with two-framing cuts + kinetic stacks; **G** — values / mindset talks as a phone selfie with meaning-coded editorial stacks.  
**Avoid:** **A** — Faceless hides the person the brand is built on; use only for a side explainer series.  
**Palette (no brand colours only):** `#0A7CFF` / `#FFD60A` — system blue + highlighter yellow — B's native accents, neutral for any expert; blue reads on light and dark; yellow is a selection/highlight fill under ink.  
**Art direction:** glossy soft-touch materials and frosted glass, clean studio light with soft rim, palette of warm neutrals with a single blue accent, minimal and confident, no text. Props: microphone, notebook and pen, coffee cup, lightbulb, chess piece, compass, target with arrow, speech bubble.  
**Music (B/C/E):** confident, warm, minimal sub-bass groove, 99–112 BPM. Voice only: style A/D; personal/vulnerable stories; psychology topics.  
**Techniques:** favour `jump_zoom`, `sticker_title`, `chest_widget`, `typing_dots`, `selection_highlight`, `ig_profile_cta`, `avatar_pill_cta`, `lens_blur`. **Layouts:** `head`, `head-side`, `statement`, `compare`, `media`.  
**Materials:** talking-head footage (several takes, hook first); avatar photo / real follower count for profile CTA; real case screenshots / client results (with permission); credentials (diplomas, certificates) if the topic is professional; B-roll of real work (events, sessions); handle & CTA keyword.  
_Only real numbers (followers, clients, income) — never rounded up. Psychologists: no diagnosis or therapy promises in reels._  
**Copy:** first-person, direct, opinionated, one idea per reel; story > advice.  

- ru: hooks «Я 5 лет делал это неправильно. Вот что изменил» · «3 вопроса, которые мне задают каждую неделю» · «Мой рабочий день — без прикрас» · CTA: Подпишитесь, Напишите слово в директ, Сохраните · avoid: успешный успех, выйди из зоны комфорта, миллион за месяц, секрет, который скрывают
- uz: hooks «Buni 5 yil notoʻgʻri qildim. Mana nimani oʻzgartirdim» · «Har hafta menga beriladigan 3 savol» · «Ish kunim — bezaksiz» · CTA: Obuna boʻling, Direktga soʻz yozing, Saqlab qoʻying · avoid: muvaffaqiyatli muvaffaqiyat, qulaylik zonasidan chiq, bir oyda million, yashiriladigan sir
- kk: hooks «Мұны 5 жыл қате істедім. Міне, не өзгерттім» · «Маған әр апта қойылатын 3 сұрақ» · «Жұмыс күнім — әсірелеусіз» · CTA: Жазылыңыз, Директке сөз жазыңыз, Сақтап қойыңыз · avoid: табысты табыс, жайлылық аймағынан шық, бір айда миллион, жасырылатын құпия

**Compliance:** No income/result guarantees; results must be real and representative. Psychology/health experts: no diagnoses or treatment claims. Paid collaborations: mark as advertising (RU: 'Реклама' + erid). Never reuse names/handles from reference videos.  

### `travel` — Туризм и путешествия · Turizm va sayohat · Туризм және саяхат
**Styles:** **B** — Real destination photos in media layouts + itinerary lists and price cards; soft bed sets the mood; **C** — 3D travel props for the dream + UI cards for what's included and prices; **D** — A guide/agent on camera answers objections and builds trust.  
**Avoid:** **A** — Voice-only, no music, and no real places — travel needs real imagery and mood.  
**Palette (no brand colours only):** `#0077B6` / `#F4A261` — sea blue + sunset sand; sea blue reads on light and dark; sand is a fill under ink.  
**Art direction:** sun-bleached linen, leather and matte painted metal materials, warm golden-hour light with soft haze, palette of sea blue, sand and terracotta, relaxed and airy, no text. Props: vintage suitcase, passport (blank, no emblem), boarding pass (blank), camera, sun hat, compass, map roll, airplane window frame.  
**Music (B/C/E):** warm, breezy, light sub-bass pulse, 98–112 BPM. Voice only: style A/D; Umrah/Hajj and other religious travel (respectful, no beat); visa/legal requirements.  
**Techniques:** favour `iphone_proof`, `number_roll`, `dark_checks`, `section_number`, `pull_out_phone`, `typing_dots`, `save_pill`; avoid `glitch_cta`, `mute_gag`. **Layouts:** `media`, `visual-top`, `list`, `number`, `head-side`.  
**Materials:** real photos/B-roll from the client's tours (rights cleared); tour program and what's included/excluded; prices with dates and all fees; tour-operator registry number / licence; real reviews (screenshots, with permission); logo.  
_Real places only from real photos/footage; generated images only for props. Religious travel content: modest, respectful, no music._  
**Copy:** experienced travel friend: what's included, real price, practical tips.  

- ru: hooks «Стамбул на 4 дня: что входит в тур, а что нет» · «3 документа, которые забывают перед вылетом» · «Сколько реально стоит неделя в Грузии — разбор» · CTA: Забронируйте, Узнайте даты, Напишите направление · avoid: виза гарантирована, всё включено, рай на земле, горящий — успей
- uz: hooks «Istanbulga 4 kun: turga nima kiradi, nima kirmaydi» · «Uchishdan oldin unutiladigan 3 hujjat» · «Gruziyada bir hafta aslida qancha turadi — tahlil» · CTA: Band qiling, Sanalarni bilib oling, Yoʻnalishni yozing · avoid: viza kafolatlangan, hammasi kiritilgan, yerdagi jannat, shoshiling
- kk: hooks «Стамбұлға 4 күн: турға не кіреді, не кірмейді» · «Ұшар алдында ұмытылатын 3 құжат» · «Грузияда бір апта шынында қанша тұрады — талдау» · CTA: Брондаңыз, Күндерін біліңіз, Бағытты жазыңыз · avoid: визаға кепілдік, бәрі қосылған, жердегі жұмақ, асығыңыз

**Compliance:** No visa guarantees. Prices with dates and all mandatory fees; 'всё включено' only if the hotel package really is all-inclusive. RU: tour operator registry number in ads; KZ/UZ: licence where required. Religious travel: respectful framing, no music, no AI images of holy sites.  

### `kids_family` — Дети и семья · Bolalar va oila · Балалар және отбасы
**Styles:** **B** — Friendly UI cards for schedules, activities and parent FAQs; light themes feel safe; **D** — A teacher/specialist on camera answers parents' worries with authority; **C** — Playful 3D toy-like heroes + UI cards for events and enrolment.  
**Avoid:** **E** — Dense news format is too dry for parents' emotional decisions (use only for official enrolment rules).  
**Palette (no brand colours only):** `#2A8C82` / `#FFB703` — calm sea-green + sunny yellow — friendly without rainbow overload; sea-green reads on light and dark; sunny yellow is a fill under ink.  
**Art direction:** soft rounded matte plastic and felt materials, toy-like proportions, soft bright diffused light, palette of sea-green, sunny yellow and warm cream, gentle and safe, no text. Props: wooden building blocks, crayons, backpack (unbranded), alarm clock, spinning top, picture book (blank cover), abacus, balloon.  
**Music (B/C/E):** light, playful, gentle pulse (no childish jingle), 98–110 BPM. Voice only: style A/D; developmental/health concerns (speech delay, special needs).  
**Techniques:** favour `paper_section`, `section_number`, `dark_checks`, `typing_dots`, `sticker_title`, `save_pill`, `chest_widget`; avoid `glitch_cta`, `curtain_reveal`, `jump_zoom`, `mute_gag`. **Layouts:** `list`, `media`, `stack`, `head-side`, `visual-top`.  
**Materials:** photos/B-roll of the space and activities — children only with written parental consent, else backs/hands-free shots; schedule, age groups, prices; specialists' credentials; licence for education/medical services if applicable; real parent reviews (screenshots, with permission); teacher talking-head footage; logo.  
_Children's faces are the strictest privacy item: no consent → no face (blur or shoot from behind)._  
**Copy:** warm specialist talking to parents: reassuring, practical, never shaming.  

- ru: hooks «Как проходит первый день в нашем садике» · «3 занятия, которые развивают речь дома» · «Во сколько лет начинать английский — отвечает педагог» · CTA: Запишитесь на экскурсию, Сохраните, Напишите возраст ребёнка · avoid: ваш ребёнок отстаёт, гений, гарантируем результат, плохие родители
- uz: hooks «Bogʻchamizda birinchi kun qanday oʻtadi» · «Uyda nutqni rivojlantiradigan 3 ta mashgʻulot» · «Ingliz tilini necha yoshdan boshlash kerak — pedagog javob beradi» · CTA: Ekskursiyaga yoziling, Saqlab qoʻying, Bolaning yoshini yozing · avoid: farzandingiz ortda qolmoqda, daho, natija kafolati, yomon ota-ona
- kk: hooks «Балабақшамызда алғашқы күн қалай өтеді» · «Үйде сөйлеуді дамытатын 3 жаттығу» · «Ағылшын тілін неше жастан бастау керек — педагог жауап береді» · CTA: Экскурсияға жазылыңыз, Сақтап қойыңыз, Баланың жасын жазыңыз · avoid: балаңыз қалып жатыр, данышпан, нәтиже кепілдігі, жаман ата-ана

**Compliance:** Children on screen only with written parental consent. Ads must not urge children to persuade parents or exploit trust (RU 38-ФЗ ст.6; similar in KZ/UZ). No developmental/medical promises; speech therapy = specialist consultation framing. Toy safety: no claims without certification.  

### `religion_spirituality` — Религия, духовность, нравственность · Din, maʼnaviyat, axloq · Дін, рухани құндылықтар, адамгершілік
**Styles:** **G** — the reference look for reflective faith talks: calm selfie, editorial stacks with meaning-coded emphasis (pink glow = devotion, serif = remembrance), light-only generated scenes, client calligraphy; **F** — a more direct lecture rhythm without sacred imagery; **E** — announcements (Ramadan schedule, event dates, charity totals).  
**Avoid:** **A** — glossy 3D toys trivialise sacred topics; **C** — whips/portals clash with a reflective tone.  
**Palette (no brand colours only):** `#2E8B6E` / `#E9D58A` — deep green + parchment gold.  
**Art direction:** cinematic, reverent, soft volumetric light, warm amber and deep navy, dust in light beams, symbolic not literal, no text, **no faces**. Props: open book of light, lantern, tasbih, light through a geometric lattice, path of lights, hands releasing light, dawn horizon, date palm silhouette.  
**Music:** calm ambient pads or vocal-only (nasheed), 96–104 BPM — **ask whether instruments are acceptable**; voice-only when the client prefers it or recitation is present.  
**Techniques:** favour `lens_blur`, `hero_word`, `selection_highlight`; avoid `glitch_cta`, `rgb_ghost`, `mute_gag`, `glove_tap`, `jump_zoom`, `sticker_title`, `strike_fix`. **Layouts:** `head`, `head-side`, `statement`, `media`, `hero`.  
**Materials:** talking-head footage; exact honorifics/spellings (с.а.с / ﷺ); calligraphy/ornament files the client owns, verified by the client; sources for quoted hadith/verses; handle & CTA keyword.  
**Copy:** humble, reflective, "мы должны", one value per reel, no fear-mongering. Hooks ru «Один навык, который меняет человека» · uz «Insonni oʻzgartiradigan bitta koʻnikma» · kk «Адамды өзгертетін бір дағды».  
**Compliance (binding):** never depict faces of prophets, companions or holy figures (light / silhouette / empty place only; no human faces in generated scenes); no AI-generated calligraphy or Arabic of holy names/verses — client-supplied, client-verified files only; honorifics and quotes exactly as supplied, with sources; no comic SFX; nothing mocking other faiths; local rules on religious advertising apply; same care for every faith; never reuse reference footage/scenes/handles.  

### `default` — Другое / общий бизнес · Boshqa / umumiy biznes · Басқа / жалпы бизнес
**Styles:** **B** — Safest all-rounder: literal words, clear cards, works for any service with or without footage; **A** — Faceless explainer when there's no footage and the topic is a concept; **D** — If the client has talking-head footage — a face beats any graphic for trust.  
**Palette (no brand colours only):** `#0A7CFF` / `#FFD60A` — neutral system blue + highlighter yellow; blue reads on light and dark; yellow is a fill under ink.  
**Art direction:** clean soft-touch matte materials, soft studio light with gentle rim, neutral warm-grey palette with one accent colour, minimal and consistent, no text. Props: lightbulb, calendar tile, phone with blank screen, checklist board, gift box, location pin, chat bubble, clock.  
**Music (B/C/E):** neutral, soft sub-bass bed, 99–110 BPM. Voice only: style A/D; sensitive topics.  
**Techniques:** favour `number_roll`, `selection_highlight`, `strike_fix`, `iphone_proof`, `section_number`, `save_pill`; avoid `mute_gag`. **Layouts:** `stack`, `media`, `list`, `number`, `compare`.  
**Materials:** real photos/B-roll of the product, place or team; price list / offer terms; screenshots of proof (reviews, stats) — real only; talking-head footage if available; logo.  
_Ask the client which licences or legal disclaimers apply to their business._  
**Copy:** clear, concrete, human; one idea per scene.  

- ru: hooks «3 вещи, которые стоит знать до покупки» · «Как это работает — за 30 секунд» · «Частый вопрос клиентов — отвечаем» · CTA: Напишите в директ, Сохраните, Подпишитесь · avoid: лучший, уникальный, инновационный, в современном мире, гарантия
- uz: hooks «Xariddan oldin bilish kerak boʻlgan 3 narsa» · «Bu qanday ishlaydi — 30 soniyada» · «Mijozlarning koʻp beradigan savoli — javob beramiz» · CTA: Direktga yozing, Saqlab qoʻying, Obuna boʻling · avoid: eng zoʻr, noyob, innovatsion, zamonaviy dunyoda, kafolat
- kk: hooks «Сатып алмас бұрын білу керек 3 нәрсе» · «Бұл қалай жұмыс істейді — 30 секундта» · «Клиенттердің жиі сұрағы — жауап береміз» · CTA: Директке жазыңыз, Сақтап қойыңыз, Жазылыңыз · avoid: ең үздік, бірегей, инновациялық, қазіргі әлемде, кепілдік

**Compliance:** Superlatives and comparatives need proof. No fake reviews/metrics. Alcohol, tobacco/vapes, gambling/betting, weapons: excluded. RU paid ads: 'Реклама' + erid marking.  

