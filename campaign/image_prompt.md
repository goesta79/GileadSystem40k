# Midjourney V8.1 – Arbeitsanweisung & Image Prompts (Gilead-Kampagne)

Stand: V8.1 ist seit **11.06.2026** Midjourneys Default-Modell. Dieser Leitfaden fasst die Community-Best-Practices für **fotorealistische** Bilder zusammen und liefert weiter unten fertige Prompts, jeweils mit Bezug auf **Abenteuer** und **NPC-Namen**.

---

## TEIL 1 – Arbeitsanweisung (so baust du jeden Prompt)

### Das Grundrezept (Reihenfolge)
Beschreibe den Prompt wie ein **Foto-Briefing an einen Kameramann**, in dieser Reihenfolge:

1. **Bildtyp/Medium:** `cinematic film still, photorealistic portrait` (verankert Fotorealismus statt Illustration).
2. **Subjekt klar benennen:** Spezies, Geschlecht, Alter, Rolle (je konkreter, desto stabiler).
3. **Aussehen & Material-Details:** Rüstung/Kleidung mit *taktilen* Begriffen – „oxidized copper with verdigris patina", „worn leather showing decades of use", Hautdetails („visible pores, subtle skin texture, fine scars").
4. **Handlung & Umgebung:** wo, was tut die Figur, Atmosphäre.
5. **Licht – spezifisch, nie „dramatic":** „golden hour casting long shadows", „Rembrandt lighting with soft fill from camera left", „cold blue rim light vs warm candle glow".
6. **Kamera & Optik:** Modell + Brennweite + Blende: „shot on Hasselblad X2D, 90mm f/2.0", „RED Komodo, 35mm f/2.8".
7. **Stimmung/Stil-Anker:** `grimdark Warhammer 40k atmosphere, muted desaturated palette`.
8. **Parameter** (siehe Cheat-Sheet).

### Parameter-Cheat-Sheet (V8.1)
| Parameter | Wert/Range | Wofür |
|---|---|---|
| `--v 8.1` | – | Modell explizit setzen (ist Default) |
| `--style raw` / `--raw` | Flag | **Wichtigster Fotoreal-Schalter** – nimmt MJs „Auto-Hübsch" raus |
| `--s` / `--stylize` | 0–1000 (Default 100) | **Fotoreal: 0–100 niedrig halten.** Hoch = künstlicher |
| `--hd` | Flag (1.33 GPU-Min) | Native 2048px. **Für diese Kampagne weggelassen** (Druck ~5×5 cm – HD kostet nur Rechenzeit). |
| `--sd` | Flag (<1 GPU-Min) | günstige Variante zum Testen |
| `--draft` / ⚡ | Flag | 24 günstige Test-Bilder, gute dann via *Vary* hochziehen |
| `--ar` | **Kampagnen-Default `1:1`** | Seitenverhältnis |
| `--no` | Liste | Negativ-Prompt (s.u.) |
| `--chaos` | 0–100 | Streuung der 4 Ergebnisse |
| `--weird` | 0–3000 | unkonventionelle Ästhetik (sparsam) |
| `--exp` | 0–100 (mix max ~25) | extra Detail/Tonemapping |
| `--sref` | Code/URL | **Stil-Konsistenz** über mehrere Bilder |
| `--sw` | 0–1000 (Default 100) | Stärke des `--sref` |
| `--seed` | Zahl | Reproduzierbarkeit |

### Standard-Negativ-Prompt (Fotorealismus)
`--no anime, cartoon, illustration, painting, drawing, sketch, cgi, 3d render, plastic skin, smooth airbrushed skin, extra fingers, deformed hands`

### ⚠️ V8.1-Stolperfallen (verifiziert)
- **`--cref` und `--oref`/`--ow` funktionieren NICHT auf V8.1** (nur V7). Für **Charakter-Konsistenz** eines wiederkehrenden NPCs daher: (a) **identische Text-Beschreibung** + gleicher **`--seed`**, (b) ein **`--sref`-Stilcode** über die ganze Serie, oder (c) ein **`--p` Personalisierungs-Profil/Moodboard**. Wenn echte Gesichts-Konsistenz kritisch ist, das Referenzbild ausnahmsweise auf **V7 mit `--oref`** erzeugen.
- **Kein `--q` (Quality)**, keine **Multi-Prompts (`::`)**, kein **Niji**, kein **Turbo** auf V8.1.
- **Kein separater Upscaler** – stattdessen direkt `--hd`.

### Konsistenz-Tipp für DIESE Kampagne
Erzeuge zuerst **ein** Bild, dessen Grimdark-Look dir gefällt, kopiere dessen **`--sref`-Code** und hänge ihn an alle weiteren Prompts (`--sref <code> --sw 100`). So bekommt die ganze NPC-Galerie denselben „Movie-Still-40k"-Look. Lege den Code hier ab:

> **Kampagnen-Stil-Code:** `--sref __________` *(nach erstem guten Bild eintragen)*

### Wiederverwendbare Suffixe (zum Anhängen)
*Kampagnen-Default: immer `--ar 1:1`, **kein** `--hd` (Bilder werden nur ~5×5 cm gedruckt).*
- **Porträt:** `--ar 1:1 --style raw --s 60 --v 8.1 --no anime, cartoon, illustration, painting, cgi, 3d render, plastic skin, smooth airbrushed skin, deformed hands`
- **Szene/Ort:** `--ar 1:1 --style raw --s 80 --v 8.1 --no anime, cartoon, illustration, painting, cgi, 3d render`

---

## TEIL 2 – Vorgeschlagene Prompts

*Englische Prompt-Strings (MJ versteht Englisch am besten); Überschrift nennt Abenteuer + NPC. Suffix ist schon angehängt – Copy & Paste. `<STIL>` ggf. durch deinen `--sref`-Code ersetzen.*

### A) Abenteuer 5 – Hauptszenen-NPCs & Orte

**Abenteuer 5 — Custodes Hadriannus** *(uralter Custodes, Verkünder der geheimen Wahrheit)*
> cinematic film still, photorealistic portrait of an ancient Adeptus Custodes demigod, towering warrior in ornate gold auramite power armour, long unbound grey hair, weathered noble face with the fine scars of ten thousand years, solemn unblinking eyes, standing in a candle-lit gothic vault, drifting dust motes, shot on Hasselblad X2D, 90mm f/2.0, Rembrandt lighting deep shadows, muted gold and black palette, grimdark Warhammer 40k atmosphere --ar 1:1 --style raw --s 60 --v 8.1 --no anime, cartoon, illustration, painting, cgi, 3d render, plastic skin, smooth airbrushed skin, deformed hands

**Abenteuer 5 — Seraphaena (Contemptor-Galatus Dreadnought)** *(erwachend, kerzenübersät)*
> cinematic film still, a colossal ancient golden Contemptor Galatus dreadnought walker with a sarcophagus chest, covered in thousands of melted candle stubs and centuries of yellowed prayer scrolls, faint green eye-lenses flickering awake in the dark, kneeling in a forgotten under-makropolis crypt beside a glowing eldar webway portal, volumetric god-rays through dust, shot on RED Komodo, 35mm f/2.8, cold blue rim light against warm candle glow, awe and decay, grimdark Warhammer 40k --ar 1:1 --style raw --s 80 --v 8.1 --no anime, cartoon, illustration, painting, cgi, 3d render

**Abenteuer 5 — Freigräfin Myrissaine Myravel** *(Drukhari-Matriarchin, silberne Haifischzähne)*
> cinematic film still, photorealistic portrait of an ageless pale Drukhari matriarch, aristocratic cruel beauty, faint cruel smile revealing a row of polished silver shark teeth, intricate dark baroque armour-gown with blood-red accents, seated regally at a candle-lit tea table in an impossible manor salon, shot on Hasselblad X2D, 80mm f/1.8, soft warm key with deep shadow, opulent and unsettling, grimdark Warhammer 40k --ar 1:1 --style raw --s 60 --v 8.1 --no anime, cartoon, illustration, painting, cgi, 3d render, plastic skin, smooth airbrushed skin, deformed hands

**Abenteuer 5 — Olveranna Myravel** *(Meistermime der Eistränen, büßende Harlequin)*
> cinematic film still, photorealistic portrait of a female Aeldari harlequin master mime, shifting iridescent diamond-pattern bodysuit in cold blues and silver, an ornate domino mask that seems to weep and smile at once, lower face veiled, melancholic graceful poise mid-gesture, standing on a void stage lit like falling snow and roses, shot on Canon R5, 85mm f/1.4, ethereal rim light, sorrowful elegance, grimdark Warhammer 40k --ar 1:1 --style raw --s 70 --v 8.1 --no anime, cartoon, illustration, painting, cgi, 3d render, plastic skin

**Abenteuer 5 — Lady Vaelissyra Myravel** *(Unterhändlerin, Webway-Führerin)*
> cinematic film still, photorealistic portrait of an elegant reserved Drukhari noblewoman, sleek dark segmented armour with subtle bladed edges, sharp composed features, faint silver teeth, leading the way through a crystalline living-glass webway corridor, impossible angles glowing behind her, shot on Sony A1, 50mm f/2.0, cool prismatic light, tense and graceful, grimdark Warhammer 40k --ar 1:1 --style raw --s 65 --v 8.1 --no anime, cartoon, illustration, painting, cgi, 3d render, plastic skin, deformed hands

**Abenteuer 5 — Die Eistränen (Harlequin-Truppe)** *(Vorführung über den Fall der Myravel)*
> cinematic film still, a troupe of Aeldari harlequins mid-performance, flowing holographic diamond costumes whose colours shift when not looked at directly, weeping-and-smiling masks, frozen in an acrobatic tableau telling a tragic story, swirling petals and snow, a vast dark void-stage, shot on RED Komodo, 28mm f/2.8, theatrical volumetric spotlights, uncanny beauty and dread, grimdark Warhammer 40k --ar 1:1 --style raw --s 85 --v 8.1 --no anime, cartoon, illustration, painting, cgi, 3d render

**Abenteuer 5 — Ort: Die Villa der Myravel** *(extradimensionaler Sitz)*
> cinematic film still, an impossible extradimensional manor in eternal autumn afternoon, golden light over gentle hills that curve upward into the sky like the inside of a sphere, a second identical manor hanging upside down at the zenith, three suns casting four shadows, falling leaves frozen a beat too long, dark gothic stone house with warm glowing windows, shot on Hasselblad X2D, 24mm f/8, dreamlike and wrong, grimdark Warhammer 40k --ar 1:1 --style raw --s 90 --v 8.1 --no anime, cartoon, illustration, painting, cgi, 3d render

**Abenteuer 5 — Ort: Der Webway-Eingang** *(Szene A1)*
> cinematic film still, a vast corridor of living crystal inside the eldar webway, breathtakingly beautiful, impossible escher-like angles, faint music made visible as light, here and there scarred wounds in the crystal seeping thin oily warp-mist, tiny figures walking deeper, shot on RED Komodo, 18mm f/4, prismatic glow with creeping shadow, sublime and ominous, grimdark Warhammer 40k --ar 1:1 --style raw --s 90 --v 8.1 --no anime, cartoon, illustration, painting, cgi, 3d render

---

### B) Abenteuer 5 – Webway-Basar: diverse NPCs

*Bunte Speziesvielfalt für „Multi-Kulti-Dark-Goth-Reizüberflutung". Mische bei Bedarf in jeden Prompt deinen `--sref`-Code für einheitlichen Look. Namen mit ★ sind neue Vorschläge (in den Fluff-Vignetten noch nicht benannt).*

**Abenteuer 5 / Basar — Ort-Establisher**
> cinematic film still, a teeming multi-species bazaar built inside a torn-open wound in the eldar webway, crystalline arches overgrown with stalls and banners, lanterns of impossible colours, crowds of aliens and hooded humans, dark-goth-ethno overload, smoke and prismatic haze, shot on RED Komodo, 24mm f/2.8, layered volumetric light, dense and uncanny, grimdark Warhammer 40k --ar 1:1 --style raw --s 85 --v 8.1 --no anime, cartoon, illustration, painting, cgi, 3d render

**Abenteuer 5 / Basar — Mutter Sahl** *(Asche-Händlerin, menschliche Greisin)*
> cinematic film still, photorealistic portrait of a hunched ancient human crone in layered grey rags, deeply lined weathered face, milky eyes, ladling grey "memory ash" from a stone basin into tiny glass phials, faint glowing dust rising, dim stall in a webway bazaar, shot on Canon R5, 50mm f/2.0, soft lantern glow, haunted and intimate, grimdark Warhammer 40k --ar 1:1 --style raw --s 60 --v 8.1 --no anime, cartoon, illustration, painting, cgi, 3d render, plastic skin, smooth airbrushed skin

**Abenteuer 5 / Basar — Vael der Knochensänger** *(Aeldari-Exilant, Wraithbone-Künstler)*
> cinematic film still, photorealistic portrait of a melancholic exiled Aeldari craftsman, pale fine features, silent tears on his cheeks, long slender fingers shaping a small glowing wraithbone figurine that seems faintly alive, runes on his worn robe, dim stall, shot on Sony A1, 85mm f/1.8, soft side light, ancient grief, grimdark Warhammer 40k --ar 1:1 --style raw --s 65 --v 8.1 --no anime, cartoon, illustration, painting, cgi, 3d render, plastic skin

**Abenteuer 5 / Basar — Großmutter Ix** *(uralte Voidborn-Hausiererin, Fixerin)*
> cinematic film still, photorealistic portrait of a tiny extremely old voidborn human woman, pale never-seen-sunlight skin, sharp clever eyes, swaddled in patched many-pocketed coat hung with trinkets, perched on a crate in a cramped bazaar nook, shot on Canon R5, 35mm f/2.0, warm lantern light, sly and warm, grimdark Warhammer 40k --ar 1:1 --style raw --s 60 --v 8.1 --no anime, cartoon, illustration, painting, cgi, 3d render, plastic skin, smooth airbrushed skin

**Abenteuer 5 / Basar — Der Lehrling des Schmerzes** *(junger Drukhari, Haemonculus-Lehrling)*
> cinematic film still, photorealistic portrait of a young Drukhari surgeon-apprentice, pale gaunt face with an oddly shy polite smile, blood-crusted leather apron, delicate cruel instruments and softly glowing vials at his stall, sharp eyes, dim red-lit corner, shot on Sony A1, 50mm f/1.8, low red key light, quietly horrifying, grimdark Warhammer 40k --ar 1:1 --style raw --s 60 --v 8.1 --no anime, cartoon, illustration, painting, cgi, 3d render, plastic skin

**Abenteuer 5 / Basar — Die Maskenlose** *(Harlequin ohne Maske)*
> cinematic film still, photorealistic portrait of an Aeldari harlequin who has removed her mask, beautiful blank serene face like an unwritten page, faint iridescent diamond costume, unsettling stillness amid a blurred bustling bazaar, shot on Canon R5, 85mm f/1.4, cool soft light, eerie and gorgeous, grimdark Warhammer 40k --ar 1:1 --style raw --s 70 --v 8.1 --no anime, cartoon, illustration, painting, cgi, 3d render, plastic skin

**Abenteuer 5 / Basar — Der Kroot-Shaper „Langes Gedächtnis"** *(Kroot-Garküchen-Händler)*
> cinematic film still, photorealistic portrait of a lean Kroot shaper, avian reptilian alien with quills and beaked face, leathery skin, cooking strange meat over green flame at a cramped food stall, hungry knowing eyes, smoke and embers, shot on RED Komodo, 50mm f/2.0, green fire underlight, exotic and ominous, grimdark Warhammer 40k --ar 1:1 --style raw --s 65 --v 8.1 --no anime, cartoon, illustration, painting, cgi, 3d render

**★ Abenteuer 5 / Basar — Yssara die Blinde** *(exilierte Navigatorin, liest Pfade statt Sterne)*
> cinematic film still, photorealistic portrait of an exiled human Navigator woman, a closed bound third eye on her forehead leaking faint warp-light, real eyes milky and blind, ornate high-collared faded house-robe, fingertips reading a floating web of glowing threads, dim stall, shot on Hasselblad X2D, 80mm f/2.0, cold ethereal glow, mysterious and aristocratic, grimdark Warhammer 40k --ar 1:1 --style raw --s 60 --v 8.1 --no anime, cartoon, illustration, painting, cgi, 3d render, plastic skin

**★ Abenteuer 5 / Basar — Grobb der Träger** *(abhumaner Lastträger/Rausschmeißer)*
> cinematic film still, photorealistic portrait of a hulking abhuman ogryn-like brute, slab-muscled, low brow, gentle confused eyes, scarred grey skin, crude harness and stacked crates on his back, looming protectively over a small stall in a crowded bazaar, shot on Canon R5, 35mm f/2.8, hard top light, imposing yet oddly kind, grimdark Warhammer 40k --ar 1:1 --style raw --s 60 --v 8.1 --no anime, cartoon, illustration, painting, cgi, 3d render, plastic skin

**★ Abenteuer 5 / Basar — Bruder Cassikan** *(menschlicher Pilger-Reliquienhändler, Gasmaske)*
> cinematic film still, photorealistic portrait of a hooded human relic-pedlar in faded purple robes, cracked leather gas-mask with one glass lens, gloved hands offering fake saint-bones and vials on dark velvet, fervent posture, smoky bazaar light, shot on Sony A1, 50mm f/2.0, moody lantern glow, zealous and shabby, grimdark Warhammer 40k --ar 1:1 --style raw --s 60 --v 8.1 --no anime, cartoon, illustration, painting, cgi, 3d render, plastic skin

**★ Abenteuer 5 / Basar — Thael/ Vyre, die Zwillingsmimen** *(Exoditen-Reisende mit kleinem Reittier)*
> cinematic film still, photorealistic portrait of two lithe Exodite Aeldari traders in primitive-elegant beast-leather and bone ornaments, sun-weathered tattooed skin, a small scaled saurian mount beside them, alert wary eyes, exotic wares of horn and hide, dim bazaar, shot on RED Komodo, 50mm f/2.0, warm rim light, feral and graceful, grimdark Warhammer 40k --ar 1:1 --style raw --s 70 --v 8.1 --no anime, cartoon, illustration, painting, cgi, 3d render

---

## TEIL 3 – Workflow-Empfehlung
1. **Stil festnageln:** einen Establisher (z.B. den Basar-Ort) erzeugen, besten Look behalten, dessen `--sref`-Code oben eintragen.
2. **NPC-Serie:** jeden NPC-Prompt mit demselben `--sref`-Code laufen lassen → einheitliche Galerie.
3. **Erst `--draft`/`--sd`** zum Finden der Komposition, dann beste Variante final rendern (kein `--hd` nötig – kleine Drucke).
4. Fertige Bilder im `images/`-Ordner ablegen; im `images/image_catalog.md` taucht jedes Bild ohnehin auf (Katalog neu bauen via `python images/_catalog_batches/build_catalog.py`).
