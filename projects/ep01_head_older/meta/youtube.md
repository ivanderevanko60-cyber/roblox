# EP01 — publishing kit

## Title options (test in this order)

1. **Your Head Is Older Than Your Feet — 4 Experiments That Broke Time**
2. **They Gave Atomic Clocks a Plane Ticket — 4 Experiments That Broke Time**
3. **Time Runs Faster Above Your Head. Four Experiments Proved It.**
4. **The 4 Experiments That Proved Time Isn't the Same Anywhere**
5. **Scientists Measured Time Bending Across 1 Millimeter**

Keep under ~60 characters visible on mobile; #1 and #2 lead with the surprise, not the topic.

## Thumbnails

Cinematic route: one beautiful photograph, a dark gradient only where the type sits, one typeface (Anton) across the whole set, one accent word in warm gold. Checked at 280 px wide -
the size they are actually seen at in the feed.

| File | Photo | Headline |
|---|---|---|
| `meta/thumb_A_startrails.jpg` | Star trails over a mountain camp, 8256x4644 (Pexels, Alexey Chudin) | TIME RUNS **FASTER** UP HERE |
| `meta/thumb_B_milkyway.jpg` | Milky Way over the Andes, 7856x5980 (Pexels, Photo Tours Peru) | YOUR HEAD IS **OLDER** THAN YOUR FEET |
| `meta/thumb_C_wing.jpg` | Sunrise from an airliner window, 7360x4912 (Pexels, Stefan Stefancik) | THEY FLEW **CLOCKS** AROUND THE WORLD |

One typeface across the set (Anton), two lines, one accent word, no small print.

Star trails are literally a photograph of time passing, which is why A is my pick for the launch.
Built with `tools/thumb_beauty.py`; fonts in `assets/fonts` (Anton, Bebas Neue, Playfair Display, Inter - all OFL).

Run all three through YouTube's Test & Compare after upload.

## Description

```
Your head is older than your feet. Not by much — over a lifetime the difference is less than a tenth of a millionth of a second. But it has been measured, four times, each experiment smaller than the last: a mountain, a pair of commercial flights, one stair step, and finally a cloud of atoms a millimetre tall.

00:00  Your head is older than your feet
00:40  I. The Mountain - muons at Mount Washington (Frisch & Smith, 1963)
02:41  II. The Airplanes - Hafele & Keating fly atomic clocks around the world (1971)
04:38  III. Two Stair Steps - NIST aluminium-ion clocks, 33 cm apart (2010)
06:06  IV. One Millimetre - JILA strontium clock resolves the redshift in a millimetre (2022)
07:42  There is no single time

SOURCES
• Frisch & Smith, "Measurement of the Relativistic Time Dilation Using μ-Mesons", Am. J. Phys. 31, 342 (1963) — https://pubs.aip.org/aapt/ajp/article/31/5/342/1046834
• Mount Washington Observatory on the experiment — https://mountwashington.org/special-relativity-and-mount-washington/
• Hafele & Keating, "Around-the-World Atomic Clocks", Science 177, 166 (1972) — https://www.science.org/doi/10.1126/science.177.4044.166
• Chou et al., "Optical Clocks and Relativity", Science 329, 1630 (2010); NIST release — https://www.nist.gov/news-events/news/2010/09/nist-clock-experiment-demonstrates-your-head-older-your-feet
• Bothwell et al., "Resolving the gravitational redshift across a millimetre-scale atomic sample", Nature 602, 420 (2022) — https://www.nature.com/articles/s41586-021-04349-7
• JILA/NIST release — https://www.nist.gov/news-events/news/2022/02/jila-atomic-clocks-measure-einsteins-general-relativity-millimeter-scale

FOOTAGE & IMAGES
• Earth from orbit: NASA (ISS 4K Earth Views)
• Ion trap photograph and strontium clock photograph: NIST / JILA (public domain, credit NIST)
• Earth textures: NASA Blue Marble and Black Marble
• Stock footage: Pexels contributors
• 3D animation, motion graphics and score: made for this video

Narration is synthesised. Everything stated in this video is sourced above.
```

Timestamps above match the final render (8:26). Regenerate from `cut/timeline.json` if the cut changes.

## Tags

```
time dilation, general relativity, special relativity, atomic clock, optical clock, gravitational redshift, muon experiment, Hafele-Keating, NIST, JILA, strontium clock, physics documentary, space time, einstein, why time bends, science documentary
```

## Pinned comment

```
Four experiments, from a mountain to a millimetre. Every number in this video comes from the original papers — they're linked in the description. Which one surprised you most?
```

## Upload checklist

- Category: Education · Language: English · Captions: upload `meta/subtitles_en.srt`
- "Altered or synthetic content" disclosure: **yes** — the narration is AI-generated (YouTube requires this; the video is not realistic depiction of real people/events, so no on-video label is expected)
- Chapters: paste the timestamps above into the description (first one must be 00:00)
- End screen: last 5 s of the video are held on black for the end card
- Thumbnail A/B: upload all three via Test & Compare
