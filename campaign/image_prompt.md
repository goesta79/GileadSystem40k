# Midjourney V8.1 – Arbeitsanweisung & Image Prompts (Gilead-Kampagne)

Stand: V8.1 ist seit **11.06.2026** Midjourneys Default-Modell. Dieser Leitfaden fasst die Community-Best-Practices für **fotorealistische** Bilder zusammen und liefert weiter unten fertige Prompts, jeweils mit Bezug auf **Abenteuer** und **NPC-Namen**.

**Dein Setup (Defaults):** quadratisch (`--ar 1:1`), kein `--hd` (Druck ~5×5 cm), Stylize **`--s 85`**, **kein `--no`** (gut trainiertes globales **`--p`-Profil** steuert Qualität/Stil). Einheitliches Suffix:

> **`--ar 1:1 --style raw --s 85 --v 8.1`**

einheitliches Präfix, alle Prompts beginnen mit: movie still in the style of grimdark 40k

---

## TEIL 1 – Arbeitsanweisung (so baust du jeden Prompt)

### Das Grundrezept (Reihenfolge)
Beschreibe den Prompt wie ein **Foto-Briefing an einen Kameramann**, in dieser Reihenfolge:

1. **Bildtyp/Medium:** `movie still in the style of grimdark 40k, photorealistic portrait` (verankert Fotorealismus statt Illustration).
2. **Subjekt klar benennen:** Spezies, Geschlecht, Alter, Rolle (je konkreter, desto stabiler).
3. **Aussehen & Material-Details:** Rüstung/Kleidung mit *taktilen* Begriffen – „oxidized copper with verdigris patina", „worn leather showing decades of use", Hautdetails („visible pores, subtle skin texture, fine scars").
4. **Handlung & Umgebung:** wo, was tut die Figur, Atmosphäre.
5. **Licht – spezifisch, nie „dramatic":** „golden hour casting long shadows", „Rembrandt lighting with soft fill from camera left", „cold blue rim light vs warm candle glow".
6. **Kamera & Optik:** Modell + Brennweite + Blende: „shot on Hasselblad X2D, 90mm f/2.0", „RED Komodo, 35mm f/2.8".
7. **Stimmung/Stil-Anker:** `muted desaturated palette`.
8. **Suffix anhängen** (siehe oben).

### Parameter-Cheat-Sheet (V8.1)
| Parameter | Wert/Range | Wofür |
|---|---|---|
| `--v 8.1` | – | Modell explizit setzen (ist Default) |
| `--style raw` / `--raw` | Flag | **Wichtigster Fotoreal-Schalter** – nimmt MJs „Auto-Hübsch" raus |
| `--s` / `--stylize` | 0–1000 (Default 100) | **Dein Standard: `85`.** Fotoreal mag niedrig (0–150) |
| `--ar` | **Kampagnen-Default `1:1`** | Seitenverhältnis |
| `--p` | Profil-ID | **Dein globales Profil** – steuert Look/Qualität, **ersetzt `--no`** |
| `--hd` | Flag (1.33 GPU-Min) | Native 2048px. **Weggelassen** (Druck ~5×5 cm) |
| `--sd` / `--draft` | Flag | günstige Test-Renders |
| `--sref` / `--sw` | Code/URL · 0–1000 | **Stil-Konsistenz** über mehrere Bilder |
| `--seed` | Zahl | Reproduzierbarkeit |
| `--chaos` / `--weird` / `--exp` | 0–100 / 0–3000 / 0–100 | Streuung / Schräglage / extra Detail (sparsam) |

### Kein Negativ-Prompt nötig
Du arbeitest mit einem gut trainierten globalen **`--p`-Profil**, das Qualität und Stil ohnehin steuert – daher **kein langer `--no`-Block** in den Prompts.

### ⚠️ V8.1-Stolperfallen (verifiziert)
- **`--cref` und `--oref`/`--ow` funktionieren NICHT auf V8.1** (nur V7). Für **Charakter-Konsistenz** eines wiederkehrenden NPCs daher: (a) **identische Text-Beschreibung** + gleicher **`--seed`**, (b) ein **`--sref`-Stilcode** über die ganze Serie, oder (c) dein **`--p`-Profil**. Wenn echte Gesichts-Konsistenz kritisch ist, das Referenzbild ausnahmsweise auf **V7 mit `--oref`** erzeugen.
- **Kein `--q` (Quality)**, keine **Multi-Prompts (`::`)**, kein **Niji**, kein **Turbo** auf V8.1.
- **Kein separater Upscaler** – falls doch mal groß gebraucht: `--hd`.

### Konsistenz-Tipp für DIESE Kampagne
Erzeuge zuerst **ein** Bild, dessen Grimdark-Look dir gefällt, kopiere dessen **`--sref`-Code** und hänge ihn an alle weiteren Prompts (`--sref <code> --sw 100`). So bekommt die ganze NPC-Galerie denselben „Movie-Still-40k"-Look. Lege den Code hier ab:

> **Kampagnen-Stil-Code:** `--sref __________` *(nach erstem guten Bild eintragen)*

---

## TEIL 2 – Vorgeschlagene Prompts

*Englische Prompt-Strings (MJ versteht Englisch am besten); Überschrift nennt Abenteuer + NPC. Suffix ist schon angehängt – Copy & Paste. Optional deinen `--sref`-Code anhängen.*

### A) Abenteuer 5 – Hauptszenen-NPCs & Orte

**Abenteuer 5 — Die Eistränen (Harlequin-Truppe)** *(Vorführung über den Fall der Myravel)*
> movie still in the style of grimdark 40k, a troupe of Aeldari harlequins mid-performance, flowing holographic diamond costumes whose colours shift when not looked at directly, weeping-and-smiling masks, frozen in an acrobatic tableau telling a tragic story, swirling petals and snow, a vast dark void-stage, shot on RED Komodo, 28mm f/2.8, theatrical volumetric spotlights, uncanny beauty and dread --ar 1:1 --style raw --s 85 --v 8.1

**Abenteuer 5 — Ort: Die Villa der Myravel** *(extradimensionaler Sitz)*
> movie still in the style of grimdark 40k, an impossible extradimensional manor in eternal autumn afternoon, golden light over gentle hills that curve upward into the sky like the inside of a sphere, a second identical manor hanging upside down at the zenith, three suns casting four shadows, falling leaves frozen a beat too long, dark gothic stone house with warm glowing windows, shot on Hasselblad X2D, 24mm f/8, dreamlike and wrong --ar 1:1 --style raw --s 85 --v 8.1

**Abenteuer 5 — Ort: Der Webway-Eingang** *(Szene A1)*
> movie still in the style of grimdark 40k, a vast corridor of living crystal inside the eldar webway, breathtakingly beautiful, impossible escher-like angles, faint music made visible as light, here and there scarred wounds in the crystal seeping thin oily warp-mist, tiny figures walking deeper, shot on RED Komodo, 18mm f/4, prismatic glow with creeping shadow, sublime and ominous --ar 1:1 --style raw --s 85 --v 8.1

---

### B) Abenteuer 5 – Webway-Basar: diverse NPCs

*Bunte Speziesvielfalt für „Multi-Kulti-Dark-Goth-Reizüberflutung". Bei Bedarf deinen `--sref`-Code anhängen. Namen mit ★ sind neue Vorschläge (in den Fluff-Vignetten noch nicht benannt).*

**Abenteuer 5 / Basar — Ort-Establisher**
> movie still in the style of grimdark 40k, a teeming multi-species bazaar built inside a torn-open wound in the eldar webway, crystalline arches overgrown with stalls and banners, lanterns of impossible colours, crowds of aliens and hooded humans, dark-goth-ethno overload, smoke and prismatic haze, shot on RED Komodo, 24mm f/2.8, layered volumetric light, dense and uncanny --ar 1:1 --style raw --s 85 --v 8.1

**Abenteuer 5 / Basar — Mutter Sahl** *(Asche-Händlerin, menschliche Greisin)*
> movie still in the style of grimdark 40k, photorealistic portrait of a hunched ancient human crone in layered grey rags, deeply lined weathered face, milky eyes, ladling grey "memory ash" from a stone basin into tiny glass phials, faint glowing dust rising, dim stall in a webway bazaar, shot on Canon R5, 50mm f/2.0, soft lantern glow, haunted and intimate --ar 1:1 --style raw --s 85 --v 8.1

**Abenteuer 5 / Basar — Vael der Knochensänger** *(Aeldari-Exilant, Wraithbone-Künstler)*
> movie still in the style of grimdark 40k, photorealistic portrait of a melancholic exiled Aeldari craftsman, pale fine features, silent tears on his cheeks, long slender fingers shaping a small glowing wraithbone figurine that seems faintly alive, runes on his worn robe, dim stall, shot on Sony A1, 85mm f/1.8, soft side light, ancient grief --ar 1:1 --style raw --s 85 --v 8.1

**Abenteuer 5 / Basar — Großmutter Ix** *(uralte Voidborn-Hausiererin, Fixerin)*
> movie still in the style of grimdark 40k, photorealistic portrait of a tiny extremely old voidborn human woman, pale never-seen-sunlight skin, sharp clever eyes, swaddled in patched many-pocketed coat hung with trinkets, perched on a crate in a cramped bazaar nook, shot on Canon R5, 35mm f/2.0, warm lantern light, sly and warm --ar 1:1 --style raw --s 85 --v 8.1

**Abenteuer 5 / Basar — Der Lehrling des Schmerzes** *(junger Drukhari, Haemonculus-Lehrling)*
> movie still in the style of grimdark 40k, photorealistic portrait of a young Drukhari surgeon-apprentice, pale gaunt face with an oddly shy polite smile, blood-crusted leather apron, delicate cruel instruments and softly glowing vials at his stall, sharp eyes, dim red-lit corner, shot on Sony A1, 50mm f/1.8, low red key light, quietly horrifying --ar 1:1 --style raw --s 85 --v 8.1

**Abenteuer 5 / Basar — Die Maskenlose** *(Harlequin ohne Maske)*
> movie still in the style of grimdark 40k, photorealistic portrait of an Aeldari harlequin who has removed her mask, beautiful blank serene face like an unwritten page, faint iridescent diamond costume, unsettling stillness amid a blurred bustling bazaar, shot on Canon R5, 85mm f/1.4, cool soft light, eerie and gorgeous --ar 1:1 --style raw --s 85 --v 8.1

**Abenteuer 5 / Basar — Der Kroot-Shaper „Langes Gedächtnis"** *(Kroot-Garküchen-Händler)*
> movie still in the style of grimdark 40k, photorealistic portrait of a lean Kroot shaper, avian reptilian alien with quills and beaked face, leathery skin, cooking strange meat over green flame at a cramped food stall, hungry knowing eyes, smoke and embers, shot on RED Komodo, 50mm f/2.0, green fire underlight, exotic and ominous --ar 1:1 --style raw --s 85 --v 8.1

**★ Abenteuer 5 / Basar — Yssara die Blinde** *(exilierte Navigatorin, liest Pfade statt Sterne)*
> movie still in the style of grimdark 40k, photorealistic portrait of an exiled human Navigator woman, a closed bound third eye on her forehead leaking faint warp-light, real eyes milky and blind, ornate high-collared faded house-robe, fingertips reading a floating web of glowing threads, dim stall, shot on Hasselblad X2D, 80mm f/2.0, cold ethereal glow, mysterious and aristocratic --ar 1:1 --style raw --s 85 --v 8.1

**★ Abenteuer 5 / Basar — Grobb der Träger** *(abhumaner Lastträger/Rausschmeißer)*
> movie still in the style of grimdark 40k, photorealistic portrait of a hulking abhuman ogryn-like brute, slab-muscled, low brow, gentle confused eyes, scarred grey skin, crude harness and stacked crates on his back, looming protectively over a small stall in a crowded bazaar, shot on Canon R5, 35mm f/2.8, hard top light, imposing yet oddly kind --ar 1:1 --style raw --s 85 --v 8.1

**★ Abenteuer 5 / Basar — Bruder Cassikan** *(menschlicher Pilger-Reliquienhändler, Gasmaske)*
> movie still in the style of grimdark 40k, photorealistic portrait of a hooded human relic-pedlar in faded purple robes, cracked leather gas-mask with one glass lens, gloved hands offering fake saint-bones and vials on dark velvet, fervent posture, smoky bazaar light, shot on Sony A1, 50mm f/2.0, moody lantern glow, zealous and shabby --ar 1:1 --style raw --s 85 --v 8.1

**★ Abenteuer 5 / Basar — Thael & Vyre, die Zwillingsmimen** *(Exoditen-Reisende mit kleinem Reittier)*
> movie still in the style of grimdark 40k, photorealistic portrait of two lithe Exodite Aeldari traders in primitive-elegant beast-leather and bone ornaments, sun-weathered tattooed skin, a small scaled saurian mount beside them, alert wary eyes, exotic wares of horn and hide, dim bazaar, shot on RED Komodo, 50mm f/2.0, warm rim light, feral and graceful --ar 1:1 --style raw --s 85 --v 8.1

---

### C) Abenteuer 6 – Der Imperator beschützt

*Wappen des Ordens vom Geheiligten Schild (Quelle: Illustration `Forsaken System` S. 40): **dunkel nachtblauer Wappenschild** (Heater-Form) mit blass goldenem/beinfarbenem Rand, der Rand mit kleinen Fleur-de-Lis besetzt; mittig eine große **Fleur-de-Lis in blassem Gold/Bein**, darauf ein **Totenschädel mit einem „I" auf der Stirn im Lorbeerkranz**; hinter dem Schild diagonal ein **Schwert**; darum eine **rote gedrehte Kordel**, ein **rotes Wachssiegel** mit Pergamentstreifen und ein weißes Spruchband. (Der Text nennt zusätzlich „von Flammen umgeben" und „Fleur-de-Lis auf der Stirn" – das Bild zeigt beides nicht; das Bild ist hier die Referenz.) Rüstungsfarben sind im Kanon nicht definiert – Eigenfestlegung passend zum Wappen: knochenweiße Rüstung, nachtblaue Roben, Verzierungen in blassem Gold, Kordeln/Siegel in Rot. Wiedererkennungsmerkmal Katharina: **Narbe durch die linke Augenbraue** (identisch bei Mutter Sahl und auf dem Siegel-Relief) – in allen Katharina-Prompts wortgleich lassen.*

**Abenteuer 6 — Katharina Sahl als Seraphim (Porträt)** *(junge Jahre, vor ihrer Zeit als Oberin)*
> movie still in the style of grimdark 40k, photorealistic portrait of a young female Adepta Sororitas Seraphim battle sister in her late twenties, stern devout face, short-cropped platinum white bob haircut, a thin old scar cutting through her left eyebrow, steel-grey eyes, visible pores and fine skin texture, ornate bone-white ceramite power armour with chipped edges and soot, deep midnight-blue tabard and sleeves with pale-gold trim, pale-gold fleur-de-lis on the chestplate, red braided cords, left shoulder pauldron painted midnight blue bearing a large pale-gold fleur-de-lis with a laurel-wreathed skull at its centre, a bulky twin-turbine jump pack with angelic wing vanes rising behind her shoulders, a bolt pistol held in each gauntlet crossed over her chest, red wax purity seals with parchment strips, standing in a candle-lit gothic cathedral nave with incense haze, warm candle glow from below against cold blue window light as rim, shot on Hasselblad X2D, 90mm f/2.0, solemn and resolute, muted desaturated palette --ar 1:1 --style raw --s 85 --v 8.1

**Abenteuer 6 — Katharina Sahl als Seraphim (Action)** *(im Sprung, für Rückblende/Heiligenbild)*
> movie still in the style of grimdark 40k, a female Adepta Sororitas Seraphim battle sister descending from the air on a roaring twin-turbine jump pack with angelic wing vanes, short-cropped platinum white bob haircut, a thin old scar cutting through her left eyebrow, fierce devout expression, battle-worn bone-white ceramite power armour, deep midnight-blue tabard with pale-gold trim whipping in the jet wash, pale-gold fleur-de-lis on the chestplate, red braided cords, left shoulder pauldron painted midnight blue bearing a large pale-gold fleur-de-lis with a laurel-wreathed skull at its centre, firing a bolt pistol from each hand with bright muzzle flashes, spent casings tumbling, purity seals and parchment streaming behind her, smoke-filled ruined shrine with shattered stained glass, shafts of golden light breaking through the smoke from above like a halo, shot on RED Komodo, 35mm f/2.8, fast shutter frozen motion with slight heat shimmer from the turbines, wrathful and angelic, muted desaturated palette --ar 1:1 --style raw --s 85 --v 8.1

**Abenteuer 6 — Wappen des Ordens vom Geheiligten Schild** *(für Handouts/Siegel)*
> movie still in the style of grimdark 40k, photorealistic still life of a gothic heraldic heater shield, dark midnight-blue enamelled field with worn scratches, pale-gold bone-coloured metal rim studded with small fleur-de-lis ornaments, a large sculpted pale-gold fleur-de-lis in the centre, a human skull with the roman numeral I engraved on its forehead set within a silver laurel wreath at the heart of the fleur-de-lis, a straight sword mounted diagonally behind the shield, a red braided cord looped around it, a red wax purity seal with aged parchment strips hanging from the lower left, a white ribbon banner, lying on a weathered stone altar, soft overcast window light from upper right, shot on Hasselblad X2D, 80mm f/5.6, reverent and austere, muted desaturated palette --ar 1:1 --style raw --s 85 --v 8.1

#### Kompakt-Prompts – Basar-NPCs für Abenteuer 6

*Kurzfassungen (ein Subjekt, ein Licht, eine Kamera) – weniger Text lässt dem `--p`-Profil mehr Raum. Die ausführlichen Varianten der Basar-NPCs stehen in Abschnitt B.*

**Abenteuer 6 — Die Maskenlose** *(Harlekin ohne Maske, Sprachrohr des Wirts)*
> movie still in the style of grimdark 40k, unretouched close-up portrait of a tall slender Aeldari woman with a completely bare freshly washed face, natural skin with visible pores, faint freckles, fine peach fuzz, soft natural flush on cheeks and nose tip, pale unpainted lips, plain eyebrows, pointed ears, hair pulled tightly back, calm empty expression, from the neck down a high-collared acrobat's bodysuit of iridescent diamond-patterned fabric, a smooth featureless mask held lowered in her gloved hand, blurred bazaar crowd behind, soft overcast daylight quality, 85mm f/1.4, eerie stillness --ar 1:1 --style raw --s 85 --v 8.1

*Technik gegen das Bodypainting: (1) das Wort **„harlequin" komplett vermeiden** – es zieht Rauten-Schminke und Weißgesicht nach; (2) Gesicht **zuerst** und **positiv** beschreiben (`bare freshly washed face`, `pores`, `freckles`, `natural flush`) statt „no makeup" – Verneinungen liest MJ oft als Stichwort; (3) das Kostüm mit **`from the neck down`** räumlich vom Gesicht trennen; (4) keine Metaphern wie „blank face like an unwritten page" (→ weiße Farbe). Notfall-Fallback, falls trotzdem Farbe kommt: ausnahmsweise `--no face paint, makeup, tattoos` anhängen und/oder `--s 50`.*

**Abenteuer 6 — Der Reliquienhändler** *(abgesetzter Ministorum-Ablasshändler)*
> movie still in the style of grimdark 40k, portrait of a defrocked middle-aged Ecclesiarchy preacher turned relic pedlar, faded threadbare purple robes, sweaty nervous charming smile, holding up a saint's finger bone, fake relics on dark velvet, warm lantern light, 50mm f/2.0, shabby and fervent --ar 1:1 --style raw --s 85 --v 8.1

**Abenteuer 6 — Großmutter Ix** *(uralte Voidborn-Hausiererin)*
> movie still in the style of grimdark 40k, portrait of a tiny ancient voidborn woman, paper-pale skin that never saw a sun, sharp sly eyes, patched many-pocketed coat hung with trinkets, perched on a crate in a bazaar nook, warm lantern light, 35mm f/2.0, cunning and kind --ar 1:1 --style raw --s 85 --v 8.1

**Abenteuer 6 — Der Lehrling des Schmerzes** *(junger Drukhari, Vhols Lehrling)*
> movie still in the style of grimdark 40k, portrait of a young Drukhari flesh-surgeon apprentice, pale gaunt face, shy polite smile, blood-crusted leather apron, fine cruel scalpels and glowing vials, a heavy curtain behind him, low red key light, 50mm f/1.8, quietly horrifying --ar 1:1 --style raw --s 85 --v 8.1

**Abenteuer 6 — Meister Skethryx Vhol, „der Veredler"** *(Haemonculus, Temurs Schöpfer)*
> movie still in the style of grimdark 40k, portrait of an ancient Drukhari haemonculus, emaciated elongated body, parchment skin stretched over a skull-like face, exposed extended spine with syringe vials, extra grafted surgical arms, stitched black leather robes, connoisseur's thin smile, dim flesh-workshop, cold green underlight, 50mm f/2.0, refined and monstrous --ar 1:1 --style raw --s 85 --v 8.1

---

## TEIL 3 – Workflow-Empfehlung
1. **Stil festnageln:** einen Establisher (z.B. den Basar-Ort) erzeugen, besten Look behalten, dessen `--sref`-Code oben eintragen.
2. **NPC-Serie:** jeden NPC-Prompt mit demselben `--sref`-Code laufen lassen → einheitliche Galerie.
3. **Erst `--draft`/`--sd`** zum Finden der Komposition, dann beste Variante final rendern.
4. Fertige Bilder im `images/`-Ordner ablegen; im `images/image_catalog.md` taucht jedes Bild ohnehin auf (Katalog neu bauen via `python images/_catalog_batches/build_catalog.py`).
