# Cartoon Short - analysis of the references

Study of three reference videos. Measured values come from ffmpeg runs on the three reference files;
values marked **(est.)** were read off frames or strips by eye, with the method named. Sizes are px at 1080 x 1920 (all three
references are 9:16). The reference files stay in `refs/`; only this file is meant to travel.

The style takes the LOOK of the references, never their content: the jar, the dragons, the pink cell, the cars, the
characters' faces and the on-screen words belong to those videos and are not to be reproduced.

---

## Sources

| Tag | File | What it is | Length | Size | Used |
|---|---|---|---|---|---|
| v1 | `The Ancient Jar That Warned an Empire.mp4` | story short, ancient empire, medieval-fantasy set, a giant jar with gold dragons and frogs | 64.90 s | 32.8 MB | all |
| v2 | `The Pink Prison Cell Experiment.mp4` | story short, a prison and one painted cell, wardens and prisoners | 65.29 s | 30.7 MB | all |
| v3 | `Why Drivers Started Filming The Road.mp4` | story short, car crashes, insurance fraud, dashcams, ends on a dashcam HUD | 62.30 s | 30.7 MB | all |

Container, identical in all three: MP4, H.264 High, yuv420p, bt709, **1080 x 1920 (9:16), 30 fps constant**, about
3.8 - 4.0 Mbit/s video (format total 3.76 / 4.05 / 3.94 Mbit/s), AAC 44.1 kHz stereo. No embedded subtitles: the captions
are burned into the picture, so there is no transcript with word times (see Pacing, "skipped").

Together: 3 videos, **192.5 s**, one format, one frame rate, one loudness. They are one channel format: the same caption,
the same character kind, the same editing grammar, three different worlds.

## Source setup

Not a conversion. The references are finished videos, not a build folder. Nothing is known about the tools that made them.
What the pictures themselves show: a **real-time 3D look** (soft shadow maps, bloom, depth of field, volumetric light
shafts, screen-space reflections on cars and wet roads) with a **hand-drawn character layer** on top (flat white heads with
inked outlines, noodle limbs). Those two layers are what any reproduction has to recreate.

---

## 1. The idea in one paragraph

A short where a 3D toon world is the stage and a flat, MS-Paint-style character is the actor. The world is lit and rendered
like a modern game (rich colour, long soft shadows, glowing windows, fog, rain) and changes in time of day with the story.
The character is deliberately *not* rendered: a white egg head, two dot or line eyes, thin dark limbs, a flat-coloured
torso, drawn with a uniform ink outline. One bold white caption with a black outline, 1 - 3 words at a time, runs at
about 160 chunks a minute through the lower third. The camera never stands still and a new picture arrives about every
1.3 s. Voice is dense and continuous at -14 LUFS.

---

## 2. Shot types and share of time

Method: 32 frames per video, one every 2.0 s, each classified by hand (`sheets/v*_overview.jpg`); the share is the share of
those 32 samples (+-3 points per class). Median shot length in the next section applies to all classes: the editor does not
hold a class longer than another by more than about 1 s.

| Class | What is in frame | v1 | v2 | v3 | Mean |
|---|---|---|---|---|---|
| **Character, medium (full body or knees up)** | 1 - 3 characters in a set, camera 2 - 4 m away | 25 % | 53 % | 38 % | **39 %** |
| **Wide / establishing** | whole room, hall, yard, castle gate, aerial of fields or army, no readable face | 38 % | 25 % | 25 % | **29 %** |
| **Prop or mechanism macro** | one object fills the frame: dragon head, rod mechanism from above, paint can, poster, ground texture | 28 % | 9 % | 6 % | **14 %** |
| **POV / vehicle** | windshield view, dashboard, cars on a road, a dashcam HUD | 0 % | 0 % | 31 % | **10 %** |
| **Character, close-up (head and shoulders)** | face with a clear expression, often with speed lines or a sweat drop | 9 % | 13 % | 0 % | **7 %** |

Reading: the picture is never "a person talking". Even in character shots the set carries as much of the frame as the
person does (the head is 160 - 200 px wide in a medium shot, about 330 px in a close-up, i.e. 15 - 30 % of the frame
width). Close-ups of expression are rare (7 %) and short; the long-lived shots are wides with slow camera motion.

Recurring beats seen in more than one video:
- **Cold open on the object**: the first 0.8 s is a prop macro or a character already mid-action (v1 0.0 - 0.7 s the
  jar-owner, then a dragon macro; v2 a guard slumped against a wall; v3 a driver in a cockpit).
- **Reaction two-shot**: 2 - 3 characters side by side with different expressions on one frame (neutral / laughing /
  shocked).
- **Insert of a text-bearing object**: a notice, a swatch, a clock, a dashcam HUD. The text is part of the 3D world, small
  (8 - 20 px lettering on a 400 px poster), and the caption carries the meaning.
- **"Time passes" wide**: an aerial or a ground texture sweeping by (v2 ground texture at about 36 s, aerial fields at about
  38 s; v1 sunset or burning palace at about 28 s and 58 s).

---

## 3. Pacing

All numbers measured. Cut detector: ffmpeg scene scores with a hard threshold of 0.3 found only 4 - 7 "shots" per video
because these shots are **camera-in-motion scenes separated by 2 - 4 frame cross-dissolves**, which stay below 0.3 on
thumbnails. Detection was rerun on a 36 x 64 thumbnail, caption band excluded, summed over a 6-frame window, peak >= 0.12
(script `scripts/win.mjs`, validated frame by frame on the first 8 s of v1, strip `v1_0-8s.jpg`: every cut listed lines up with a
visible change).

| | v1 | v2 | v3 | All |
|---|---|---|---|---|
| Duration | 64.90 s | 65.29 s | 62.30 s | 192.49 s |
| Shots (cuts + 1) | 45 | 38 | 42 | 125 |
| **Cuts per minute** | **40.7** | **34.0** | **39.5** | **38.1** |
| Shot length, median | 1.27 s | 1.30 s | 1.33 s | **1.30 s** |
| Shot length, p10 | 0.77 s | 0.63 s | 0.61 s | 0.67 s |
| Shot length, p90 | 2.31 s | 3.12 s | 2.60 s | 2.68 s |
| Shot length, mean | 1.44 s | 1.72 s | 1.48 s | 1.55 s |

Caution on these cut counts: motion inside a shot (a car crash, a rod spinning, a camera whip) also peaks this detector, so
treat 34 - 41 cuts/min as an **upper bound**; the true number sits between 25 and 40 (a hand count of the first 8 s of v1
from the 5 fps strip gives 7 cuts in 8 s = 52 /min in that opening burst, 28 /min across the 32-sample overview). It is
the usual range for game-capture style shorts (24 - 30 cuts a minute, 1.5 - 2.5 s a shot).

**Cut kinds** (read from the 12 fps strips `m1`, `m2`, `m3`; each strip frame = 0.083 s):
- **Hard cut**, the default. Zero transition frames. About 60 % (est.).
- **Cross-dissolve**, 2 - 3 frames = **0.07 - 0.10 s**, seen on scene changes (v1 at 7.4 s "see,"; v2 at 22.0 s
  "a stopwatch."). Shows both frames at about 50 % for one frame. About 30 % (est.).
- **Camera move through the cut** ("match" cut: a push or whip, then the next scene is already moving): v3 about 30 s, v1 at 2.9 s.
  About 10 % (est.).
No wipes, no iris, no glitch, no flash frames, no black frames between shots. 0 fades to black in 192 s.

**Caption rhythm** (measured on the caption band, a mask of pure-white pixels, changes counted per frame difference; the
band is contaminated by bright scenery, so counts carry about +-10 %):

| | v1 | v2 | v3 |
|---|---|---|---|
| Caption chunk changes | 170 | 152 | 182 |
| Per minute | 157 | 140 | 175 |
| Median gap between changes | 0.40 s | 0.34 s | 0.33 s |
| p10 / p90 gap | 0.20 / 0.57 s | 0.14 / 0.67 s | 0.16 / 0.53 s |

The 5 fps strip of v1's first 8 s: 21 chunks and 28 words, so about **1.3 words per chunk** and **about 210 words a
minute (est.)**, a fast narrator. Chunks are 1 - 3 words, never more than 4, usually ending on a content word ("a dragon's",
"the whole court", "burst", "out", "laughing.").

**Words per minute from a transcript, pauses, share of cuts within 0.15 s of a word start: skipped: no transcript with
word times.** (The captions could be OCR'd; not done, because nothing here may be guessed.) By eye, the cuts line up with
caption changes in the 40-frame opening strip of v1 (cuts at 0.73, 2.00, 2.93, 3.90 s; the matching chunk changes are at
0.67 "ball in", 2.0 "the emperor,", 2.9 "The whole court", 3.9 "see,").

**Rules for the sample:**
- Cut on the first word of a clause, not in the middle of one; a cut lands 0 - 0.10 s before the caption chunk changes.
- A shot lasts one clause (2 - 6 words). 1.3 s median, nothing longer than 4 s unless the camera is travelling (p90 of shot length is 2.3 - 3.1 s).
- Never two shots in a row with the same framing; alternate wide - medium - macro.

---

## 4. Palette

Measured: one frame per second per video (65 + 65 + 62 frames), 48 px wide, k-means k = 8, seed 7 (palette.mjs). The three
palettes are different because the scenes are different; the **grammar** (value structure, saturation of the accent, white
heads) is the same.

### v1 (warm, "ancient"), mean luma 110 / 255, dark share (luma < 40) 6.1 %, bright share (> 215) 3.8 %

| Hex | Share | Where |
|---|---|---|
| `#352c3f` | 19.8 % | night sky, shadow of the stone hall, deep purple-brown ground |
| `#665866` | 15.6 % | stone walls and columns in shade |
| `#a07557` | 15.0 % | lit wood, sand, skin of props |
| `#e4ae85` | 13.3 % | warm light on stone and the sunset sky |
| `#6d4534` | 11.7 % | dark wood, carpets edge, hair |
| `#988b95` | 9.9 % | grey stone mid |
| `#3c56a6` | 8.7 % | the main character's robe (the saturated accent) |
| `#d9d9d4` | 6.1 % | the jar's lid and head highlights |

Accents (saturated, < 25 %): `#3a56a8` blue 8.3 %, `#a46d46` orange-bronze 7.4 %; gold on the dragons about `#e0b040`
(< 3 %, seen in the frames, below the palette cut-off).

### v2 (cool, "prison"), mean luma 132, dark 3.1 %, bright 7.3 %

| Hex | Share | Where |
|---|---|---|
| `#51677b` | 21.4 % | steel-blue walls, mid |
| `#858f9c` | 17.4 % | concrete floor and lit wall |
| `#30374b` | 13.6 % | shadows, door frames, uniforms |
| `#a9bac2` | 13.3 % | light concrete in sun shafts |
| `#e480b5` | 11.4 % | **the pink cell, lit** (the story's accent) |
| `#c74185` | 11.0 % | the pink cell in shade |
| `#e8e1df` | 9.6 % | character heads, paper, shirt |
| `#a9d656` | 2.3 % | green fields (aerial), the only green |

Accents: `#df5aa1` 11.2 %, `#ad3969` 5.8 %, `#5797b6` cyan wall tiles 3.5 %.

### v3 (blue-hour, "road"), mean luma 103, dark 19.8 %, bright 5.0 %

| Hex | Share | Where |
|---|---|---|
| `#373d51` | 19.9 % | asphalt at dusk, dark blue shadow |
| `#15172a` | 19.5 % | night sky, deepest shadows |
| `#96a6b3` | 16.2 % | wet road, light cloud |
| `#6a757d` | 15.9 % | asphalt, concrete mid |
| `#3782d5` | 9.3 % | clear day sky |
| `#d8dddf` | 9.1 % | white cars, heads, clouds |
| `#728636` | 5.6 % | grass |
| `#bb1a2f` | 4.4 % | the red car (the recurring accent) |

Accents: `#2284c9` 6.9 %, `#6f8b36` 5.4 %, `#6885d6` 5.2 %; the yellow shirt of the main character about `#f2c230` (< 3 %,
seen in frames).

### What is the same in all three
- **Value structure**: a dark base (`#15172a` - `#352c3f`, 20 - 35 % of the frame) + a mid (`#51677b` - `#a07557`, 45 %) +
  1 - 2 % pure highlights. Never flat grey; pure black only in the darkest night shadows (not measured).
- **One saturated accent per scene** that owns 8 - 12 % of the frame: blue robe, pink cell, red car. Everything else in the
  scene is desaturated by 20 - 40 % against it.
- **White heads**: `#e8e1df` to `#ffffff`, never tinted by scene light more than about 8 % (est.; they stay "paper").
- **Time of day is the colour script**: day `#3782d5` sky, golden hour `#e4ae85` + `#c74185`, dusk purple `#352c3f`,
  night `#15172a` with warm window lights `#f0c060`. v1 runs day (hall) -> sunset -> moonlit night -> dawn burning city;
  v3 runs day -> dusk -> night -> wet daylight.
- **Caption**: white `#ffffff` on a black `#000000` outline, 21 : 1 (outline vs fill); the outline makes every ground legible,
  worst case measured: caption over `#d8dddf` (white car) still reads at 21 : 1 against its own outline.

### Light and finish numbers
Mean luma 103 - 132 / 255, dark share 3 - 20 %, bright share 4 - 7 %. Not crushed, not blown: the average frame is a
mid-key picture with long shadows. Loudest brightness in v2 (mean 132) because the pink cell and a pale prison are bright;
darkest in v3 (mean 103, 19.8 % dark) because of the night scenes.

---

## 5. Type: the caption (the only type)

Everything below read from full-size frames (`full/v1_9.6.png`, `full/v3_3.5.png`, `full/v2_20.5.png`) and a 3x crop
(`full/cap_zoom.png`).

| Property | Value |
|---|---|
| Face | an ultra-heavy geometric grotesque, single-storey "g", flat terminals, tight even spacing. Nearest free OFL families: **Montserrat Black / ExtraBold**, **Poppins ExtraBold**, **Inter Black**, **Anton** (condensed alternative) |
| Weight | 800 - 900 |
| Case | lower case; sentence-initial capital ("Every prisoner", "The whole court"); punctuation kept (comma, full stop, question mark) |
| Size | x-height about 43 px, ascender height about 55 px, so **font size about 80 px** (est. at 1080 wide); "a giant" is 263 px wide, "he waits" is 320 px |
| Fill | `#ffffff` |
| Outline | `#000000`, **about 4 px**, round joins, fully opaque |
| Shadow | a faint soft shadow, about 3 px down, black at about 40 % |
| Position | horizontally centred (x = 540 +- 5); vertical centre **y about 1350 (70 % of 1920)**, baseline about y 1380, i.e. just below the middle of the lower half; it sits above the platform's bottom UI zone (about 1560 px and down) |
| Line count | **one line, always**; chunks are 1 - 3 words so a chunk is 130 - 480 px wide, never wider than about 70 % of the frame |
| Timing | a chunk is on screen for 0.33 s median (0.14 - 0.67 s); there are no gaps with no caption (caption present in 99.9 - 100 % of frames) |
| Animation | no pop, no scale bounce, no slide detected between chunks: the chunk **replaces** the previous one in place within one frame (the 12 fps strips show a changed chunk at the next frame, nothing between). No highlight of the current word, no colour change, no karaoke fill |
| Emphasis | none: the same white for every word, no coloured keyword |

Everything else that is text is **inside the 3D world**: a notice, a swatch, a clock face, a room sign "C-4", a dashcam HUD
("REC", date, "54 MPH"). Size about 8 - 24 px on a prop that is itself 300 - 600 px. It carries a detail, not the story.

---

## 6. The character (the style's signature element)

Seen in frames `full/v2_20.5.png`, `full/v3_3.5.png` and the 5 fps strips.

| Part | Description | Number |
|---|---|---|
| Head | an off-white **egg / rounded oval**, no neck, flat fill `#e8e1df` - `#ffffff`, no shading, no highlight | 160 - 200 px wide in a medium shot, about 330 px in a close-up |
| Outline | ink line around the head, torso and limbs, dark navy-black `#1a1c2e` (est.), uniform weight | about 6 px at the head, about 10 px on the limbs (est.) |
| Eyes | two **black dots** or two black **bars with a lid line** (tired, smug), small round **glasses** on some; eyebrows are one short line each | eye 14 - 20 px (est.), so eyes are about 8 - 10 % of the head width |
| Mouth | a tiny line, a dot, an open "D" shape for shouting, a wide row of teeth for laughing; never a full smile arc | 20 - 60 px wide |
| Hair | a flat cap of colour: brown `#b0612a` (est.), curly ginger, black bowl cut; sits on top as a single shape | |
| Torso | a **solid rounded rectangle** in the outfit's colour, wider at the shoulders than the hips; details: a tie (brown, with 3 diagonal stripes), a belt, a badge, an "X" collar, a yellow shirt `#f2c230` | the torso is about 1.2 x head height |
| Limbs | **thin noodle lines**, 10 - 14 px, no hands to speak of (a round mitten at most), knees bend like a 2D stick figure | legs are about 2 x torso height in v2 (wardens are tall and thin) |
| Feet | none or tiny black tips | |
| Expression change | the eyes and mouth swap between frames (not tweened); sweat drops, anger veins (red `#d02030` cracks on the wall in v2), speed lines (white strokes radiating from the head, 6 - 10 lines) are added as flat 2D shapes | |
| Casting | recognisable by one colour and one prop per role: blue robe = hero, black cap + badge = warden, yellow shirt = the driver, red cardigan = the second driver, brown tie = the boss. Heads are identical, the **accessories** are the identity | 3 - 6 recurring characters per video |

The character is a **flat 2D billboard standing in the 3D scene**: it casts a shadow on the ground (soft, long, same
direction as the scene's key) but itself has no shading and no rim light; at close range it keeps its outline thickness
constant on screen, so it does not scale like 3D.

Rule for the style: heads never lit, never textured; all shading comes from a ground shadow and the scene's colour on the
torso fill (the torso colour shifts by about 10 % with the scene's light, the head does not).

---

## 7. The 3D world

| Aspect | Observation |
|---|---|
| Level of detail | high: bevelled stone, tiled walls, wet asphalt reflections, a stained-glass window, individual coins and paper money pieces in a pile, car interiors with a dashboard and a gearshift. Props have a **toon outline** about 2 px (a darker version of the surface colour), flat-ish colour with strong value shapes, painted-texture detail on stone and wood |
| Shading | cel-leaning: one key light, a shadow shape with a clear edge, soft ambient occlusion in corners, a coloured bounce (blue on the pink walls' undersides). Not photoreal and not low-poly |
| Light | one warm key (golden-hour `#e4ae85` or candle `#f0c060`), a cool fill (`#51677b`), a rim on edges in some night scenes; **volumetric light shafts** through windows (v2 mess hall, v1 hall), lamps with a halo (street lights, torches), a moon (v1) |
| Post | bloom on lights (radius about 30 px), a gentle vignette (corner luma about 15 % below centre, est.), depth of field on macros (the background 6 - 10 px blur), subtle film grain not visible at this bitrate, a very slight colour fringe on car edges |
| Weather and atmosphere | clear / cloud, rain and wet road in v3 (streaks about 60 px long on windshield, wipers sweeping), smoke and fire in v1, dust motes |
| Set dressing | every set has 3 layers: a hero prop (jar, cell door, a car), mid-ground furniture (tables, banners, lamps), a far background (castle, prison yard, skyline) |
| Palette per set | one dominant hue with its complement as the accent: blue-purple + gold (v1), steel blue + pink (v2), blue + red (v3) |
| Scale | the characters are small against the set (about 1 / 8 - 1 / 5 of the frame height in wides) |
| FX objects | a pile of money that grows (hundreds of green note-blocks, v3), a mini explosion of debris and pink paper (v2), bubbles, sparks |

Props that recur as storytelling devices (not to be copied; the kind matters): one big symbolic object per video (the jar, a
pink door, a dashcam).

---

## 8. Motion and camera

Measured from the 12 fps strips (0.083 s per frame) and the 5 fps strip; distances are screen widths unless stated.

**The camera is never still.** In 100 % of the strips inspected there is a continuous camera move during each shot.
Moves seen, with how often (of 24 shots examined, est.):
| Move | Share | Speed / extent |
|---|---|---|
| Slow **dolly-in** (push) | 40 % | about 8 - 12 % scale over 1.0 s; keeps the subject at the same screen position |
| Slow **dolly-out / pull-back** | 10 % | the same speed, reveals the wide |
| **Pan / track** sideways with a moving character | 20 % | the character stays 25 - 35 % from the edge, the set slides at 120 - 250 px/s |
| **Orbit** around a prop | 10 % | 20 - 40 degrees in 1.0 s |
| **Crane / top-down** over a mechanism | 10 % | a rotating bird's-eye shot (v1 rods) |
| **Whip / fast push on a beat** | 10 % | 0.15 - 0.25 s of motion blur, then a hold |

A slight handheld wobble is not present; the camera is smooth and eased in and out.

**Entrances** (things appearing in a shot):
- Characters **walk or hop in** (about 0.4 - 0.8 s), or are **already in place** when the cut lands. No pop-in scale bounce.
- Props **fall from above** and settle with a squash (v3 car dropping onto the driveway at 0.5 s), or a pile grows by
  **spawning pieces over 0.6 s** (money).
- Expressive beats: **squash and stretch** on the head (about +-12 %), a quick **shake** at a laugh (about 4 px at 12 Hz for
  0.5 s), a **jump** at a shock (the character rises about 0.3 x its height and drops in 0.4 s), **speed lines** that flash
  for 4 - 6 frames (0.15 - 0.20 s) behind a shouted word.
- Doors and hatches open with a **swing** of about 0.4 s with a 10 % overshoot.

**Transitions between shots**: hard cut by default, 0.07 - 0.10 s cross-dissolve when the scene or the time of day changes,
a camera whip when the story jumps place. Never longer than 0.25 s.

**Holds**: nothing is held static; the longest still-camera hold is about 0.5 s (on a "reaction" beat).

**Overlays on the picture**: only the caption. No logos, no progress bar, no frame, no letterbox, no emoji, no sticker, no
"subscribe" text, no stamps: 0 found in 192 s.

---

## 9. Sound

Measured with ffmpeg (ebur128, volumedetect, silencedetect).

| | v1 | v2 | v3 |
|---|---|---|---|
| **Integrated loudness** | -14.1 LUFS | -14.2 LUFS | -14.1 LUFS |
| Loudness range | 2.1 LU | 2.2 LU | 2.2 LU |
| True peak | -2.2 dBFS | -1.9 dBFS | -1.9 dBFS |
| Mean level (volumedetect) | -16.8 dB | -16.9 dB | -16.9 dB |
| Max level | -2.2 dB | -2.0 dB | -2.3 dB |
| Silences >= 0.25 s below -34 dB | 0 | 0 | 0 |
| Silences >= 0.2 s below -24 dB | 0 | 0 | 1 |

- **Loudness**: -14.1 LUFS +-0.1 on all three: a delivered master tuned for short-form platforms; range 2.1 - 2.2 LU = a heavily
  compressed, even level.
- **Stereo**: effectively mono: the side signal (L - R) sits at -44 dB against -17 dB mean, 27 dB below.
- **No silence**: in 192 s there is one pause of 0.2 s above -24 dB; the narration is continuous with no breaths left in, and the
  bed (music or ambience) never goes below -34 dB.
- **Spectrum** (v1, v2, v3 are within 0.3 dB of each other): 0 - 200 Hz at -21.3 dB, 200 Hz - 4 kHz at -19.1 dB, above 6 kHz at
  -30.5 dB. Low-band energy only 2 dB under the voice band suggests a **bass-carrying bed or low impacts** (a hypothesis, not proven);
  voice, music and effects **cannot be separated with ffmpeg**, say so in the style (not measured: how much of it is music).
- Sound effects: the speed lines and the crash in v3 look like they carry a hit; nothing in the file can prove it. Do not invent sound effects without a source you may use.

---

## 10. Narration trigger -> visual

Observed on the three videos (times in the file in brackets). Each is a rule for the sample.

1. **A named object -> cut to a macro of it on the word.** v1 "ball in a dragon's mouth": cut to a gold dragon macro at 0.73 s
   as "ball in" appears, full-frame, held 1.1 s while the camera pushes in about 10 %.
2. **A named person or group -> a two- or three-shot of exactly them**, standing in a row with different faces. v1 "the
   emperor," then the court: three figures on the throne steps (2.0 s).
3. **A shouted or fearful word ("run.") -> speed lines + sweat drops + a head close-up**, within the word (0.0 - 0.1 s after
   its start); the head scales about +25 % in 0.2 s (v1 4.8 - 5.3 s).
4. **Laughter ("laughing.") -> the group shakes, mouths open wide, eyes shut**, 3 faces at once, for the length of the word
   (v1 about 6.1 - 7.3 s).
5. **A change of place or time -> a cross-dissolve or camera move to a wide** of the new place, **with the light script
   changing** (day -> sunset -> night): v1 "outside" (about 27 s) and "Then" (about 28 s) go to a sunset field; v3 changes
   from a day lawn to a dusk highway to a night driveway as the money and the crash escalate.
6. **A quantity or speed word ("fast", "so") -> the thing physically happens**: v3 a pile of money grows from 0 to the frame
   height in 0.6 s while "in so" / "fast," are on screen.
7. **An action verb ("slams", "climbs", "smashes") -> the shot is the action from the nearest viewpoint**: v3 "smashes" a
   car-to-car side-on wide at the instant of impact, "climbs" a POV from the driver's seat.
8. **A measurement or a label -> a prop that shows it**, never a graphic over the picture: v2 "P-618 Baker-Miller pink" is a
   notice on a wall, a paint can, a swatch held up by the hero (three 1.3 s shots in a row); v3 the final dashcam HUD
   shows "54 MPH" then "22 MPH" as the speed word is said.
9. **The last sentence -> a calm, wide or symbolic shot** (v1 a cross-section of the ground; v3 the cockpit with the camera
   looking back at the driver), with the caption still running; the video ends on the last word, not on a card.
10. **The first sentence is a statement, not a title**: no title card in any of the three; the first caption chunk is already a
    word of the story ("He", "jail", "on the"), the hook is the first picture (a macro or a character mid-action).

---

## 11. Structure of a video (all three)

About 62 - 65 s (a 60 s short), one story, told in five blocks. Times are approximate (est., read from the sheets):
| Block | Time | Content |
|---|---|---|
| Hook | 0 - 6 s | an odd object or claim, 6 - 8 cuts, caption already running |
| Set-up | 6 - 20 s | who and where, 10 - 12 cuts, characters introduced with their accessory |
| Escalation | 20 - 45 s | the cause-and-effect chain, 15 cuts, the accent colour peaks (pink cell, money pile, army) |
| Reversal / consequence | 45 - 58 s | the payoff, a wide + a close-up, the lighting shifts (night -> dawn, fire, rain) |
| Close | 58 - 65 s | a calm wide or a symbolic shot, the last clause on the caption, no outro |

---

## 12. What to avoid

What the references never do:
- no title cards, no lower-third labels, no logos or channel marks, no subscribe or like prompts, no emoji, no sound effects
  drawn as text ("BOOM"), no kinetic type other than the caption, 0 of each in 192 s;
- no verdict stamps, no "AI" notice, no red plaques;
- no letterbox, no frame, no progress bar, no zoom-in-and-out "breathing" with no subject;
- no shot longer than 4 s, no static camera, no black frame, no fade to black;
- no photographs, stock footage or real faces: every picture is a rendered 3D set with a flat character;
- no multi-line captions, no caption in the top half, no caption on a coloured box;
- no lit, textured or shaded heads (the character stays flat, see 6);
- no 3D character with a face rendered on it (the world is 3D, the actor is not);
- no gradient backgrounds or abstract shapes standing in for a place: every shot has a real set with 3 layers of depth.

## 13. Deductions: how it was probably made (inferences, not facts)

Nothing in the files names the tools (no useful metadata: the container only says `Lavf60.16.100`, the encoder of the final
export). Everything below is **deduced from the pictures and the sound**; none of it is proven.

| Part | Probable tool | What it is deduced from |
|---|---|---|
| **3D sets** | a real-time engine such as **Unreal Engine** or **Unity**; **Blender (Eevee)** is possible too | soft shadows, light shafts through windows, reflections on a wet road, depth of field on macros, bloom on lamps, and crowds of objects on screen (a pile of banknotes, an army) look like game rendering |
| **Characters** | flat, drawn figures placed in the 3D scene: **2D images** (swapped faces) or **Grease Pencil** objects in Blender | the heads are unlit, outlined, with faces that change between frames instead of being tweened (see 6) |
| **3D models** (cars, buildings, crowds, props) | most likely **commercial or free asset libraries** (Fab, Sketchfab, the Unity Asset Store) | nobody models this much detail for shorts at this pace; the cars, castle and prison look like finished kits |
| **Voice** | most likely a **synthetic voice** (ElevenLabs or similar) | continuous, heavily compressed (loudness range 2.1 - 2.2 LU), no breaths and no pause of 0.2 s in 192 s, effectively mono (see 9); not provable from the file |
| **Captions and edit** | an editing app with automatic captions: **CapCut, Premiere or DaVinci Resolve** | word-by-word white captions with a black outline, 1 - 3 words per chunk, are a standard preset in those tools |

Why it matters for the style:
- The **look has two layers** (a lit 3D world and a flat character), so any reproduction has to keep them separate.
- The **sets depend on bought or downloaded assets**, which is the hardest part to match; the character,
  caption, pacing, palette and sound numbers in sections 2 - 12 do not depend on it.
- If the voice is synthetic, the continuous, un-breathed delivery (about 210 words a minute, no pauses) is a **property of
  the audio source**, not of the edit: a human narration will have pauses the references do not.
- **A 3D engine or 3D software is required** (Unreal, Unity or Blender, or something equivalent). The camera moves through
  lit 3D space in every shot (section 8), with real shadows, light shafts and depth of field. A 2D or slideshow editor cannot
  produce this: a flat picture with a zoom is not the same thing.
- **The work is assembling, not modelling.** The author most likely **picks ready-made assets** (cars, buildings, props,
  crowds, sets) and places, lights and animates them, instead of creating them. For a reproduction, plan the asset search
  first (free, redistributable sources, with credits) and treat modelling from scratch as out of scope.
- **What stays to be created by hand**: the flat character (head, faces, outfits), the lighting and colour script, the camera
  moves, the captions and the edit. Those are the author's real style; the assets are interchangeable.
- **Consequence**: how close a reproduction looks depends mostly on the quality of the assets found, not on the numbers in
  this document; the numbers decide pacing, captions, palette, character and sound.
- These guesses should be checked with the author's own description of the pipeline if it can be found; until then they are
  hypotheses.

---

## 14. Suggested way to rebuild it (a recommendation, not measured)

- **Blender (Eevee, headless, driven by Python scripts)** is the most practical single tool for one person working with
  Claude Code: free, scriptable, renders 1080 x 1920 at 30 fps, has toon shading, bloom, depth of field and volumetric
  light; the flat character can be a textured plane (billboard) or a Grease Pencil object that always faces the camera.
- **Sets and props**: free, redistributable libraries only (Poly Haven, Kenney, Quaternius are CC0); keep a credits file.
- **Voice**: your own recording or a synthetic voice you have the right to use. Run a speech-to-text with word times
  (e.g. Whisper) to get the timing that drives cuts and captions (the references' cut-on-word timing was not measured).
- **Captions**: generate an ASS subtitle file (one chunk per 1 - 3 words, font, outline and position from section 5) and burn
  it in with ffmpeg; this keeps the caption identical in every video.
- **Final mix**: ffmpeg `loudnorm` to -14 LUFS, true peak <= -1.5 dBFS.
- **Order of work**: (1) one still of the character in one set with the caption, compared with `frames/`; (2) a 5 s
  moving shot; (3) a 20 s sample; only then a full video. Expect the sets to be simpler than the references.
- Open questions only the author can answer: topics of the videos, the main character(s), 9:16 only or also 16:9, whether
  the voice is a person or synthetic.

## Appendix: reproducing the numbers

Files next to this document: `scripts/` (`diff.mjs`, `win.mjs`, `caps.mjs`: Node scripts using ffmpeg),
`data/` (per-frame thumbnail differences, caption change times), `sheets/` (overview sheets `v*_overview.jpg`, strips
`m1.jpg` to `m3.jpg`, `v1_0-8s.jpg`), `frames/` (full-size frames). Palette method: one frame per second, 48 px wide,
k-means with k = 8 and a fixed seed, accents = saturated clusters under 25 % share. Scene scores: ffmpeg
`select='gte(scene,0)'`.
