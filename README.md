# Helix Native Factory Preset Reference

A comprehensive, community-sourced reference document for all **384 factory presets** shipped with **Line 6 Helix Native v3.82** — the guitar amp/effects modeling plugin.

Line 6 has never published official documentation for its factory presets beyond the preset names themselves, which are deliberately obfuscated to avoid trademark issues (e.g., "Cowboys from DFW" instead of "Pantera," "Smoke on the H2O" instead of "Deep Purple"). This project parses the raw preset data, decodes every name, maps every model to its real-world hardware equivalent, and generates a fully navigable PDF reference.

## What's in the PDF

The generated document (142 pages) covers three complete setlists:

- **Factory 1** — 128 presets: amp showcases, bass presets, artist/song-inspired tones, artist signature presets, genre/creative presets, and sound effects
- **Factory 2** — 91 active presets (37 empty slots): song-inspired, genre-spanning, and bass presets
- **Templates** — 42 active presets: routing templates, DAW remote controls, MIDI utilities, and multi-instrument mixing configurations

For each preset, the document provides:

- **Decoded name** — the actual artist, song, or tonal reference behind each cryptic factory name
- **Tonal description** — what the preset sounds like and what it's designed for
- **Recommended pickup** — humbucker, single coil, or either, with position (bridge/neck/middle) and rationale based on the canonical artist or genre pairing
- **Tempo** — BPM value, shown when it deviates from the 120 BPM default (song-matched presets use the original recording's tempo for synced delay/modulation)
- **Complete signal chain table** — every block in the preset listed with its Helix name, real-world hardware equivalent, and on/off status. Disabled blocks are shown in gray.

Four appendix indices provide cross-reference navigation with clickable hyperlinks back to each preset:

- **Appendix A: Index by Amp Make & Model** — 75+ unique amp models grouped by manufacturer (Fender, Marshall, Vox, MESA/Boogie, etc.)
- **Appendix B: Index by Artist** — 65 unique artists across 80 tagged presets
- **Appendix C: Index by Genre** — 73 genre categories across 177 tagged presets
- **Appendix D: Index by Recommended Pickup Configuration** — presets grouped by pickup type and position

## Repository Contents

| File | Description |
|------|-------------|
| `Helix Native Presets.pdf` | The generated 142-page reference document (ready to use) |
| `Helix Native Presets.tex` | LaTeX source for the PDF |
| `generate_latex.py` | LaTeX document generator — parses `.hls` setlists and produces the `.tex` file |
| `helix_parser.py` | Core parser library — decodes `.hls` files, maps 342 model IDs to real hardware, exports to Excel/CSV |
| `FACTORY 1.hls` | Factory 1 setlist exported from Helix Native v3.82 |
| `FACTORY 2.hls` | Factory 2 setlist exported from Helix Native v3.82 |
| `TEMPLATES.hls` | Templates setlist exported from Helix Native v3.82 |

## How It Works

### The `.hls` Setlist Format

Helix Native stores setlists as JSON files with a `.hls` extension. The structure is:

```json
{
  "encoded_data": "<base64-encoded string>",
  ...
}
```

The `encoded_data` field contains a **Base64-encoded, zlib-compressed** JSON payload. When decoded, it yields an array of 128 preset objects. Each preset contains:

- `meta.name` — the preset's display name
- `tone.dsp0` / `tone.dsp1` — the two DSP paths, each containing numbered blocks (`block0`–`block7`), cabs (`cab0`, `cab1`), inputs, outputs, split, and join routing
- `tone.global` — global parameters including `@tempo`
- `tone.controller` — footswitch/expression pedal assignments
- `tone.snapshot0`–`snapshot7` — snapshot parameter states

Each block has a `@model` field containing the internal model identifier (e.g., `HD2_AmpBritPlexi`), which `helix_parser.py` maps to a human-readable name and real-world hardware equivalent via its `MODEL_DB` dictionary (342 entries across 16 categories).

### The Model Database

The `MODEL_DB` in `helix_parser.py` maps every Helix model ID to a `(category, helix_name, real_hardware)` tuple:

| Category | Count | Examples |
|----------|-------|---------|
| Amp | 93 | Fender Twin, Marshall Plexi, Vox AC-30, MESA Rectifier |
| Cab | 69 | Matched speaker cabinets for each amp |
| Drive | 38 | Klon Centaur, Tube Screamer, ProCo RAT, Fuzz Face |
| Delay | 23 | Tape delays, digital delays, harmony delays |
| Mod | 25 | Chorus, flanger, phaser, rotary, tremolo |
| Reverb | 22 | Room, hall, plate, spring, shimmer |
| Comp | 7 | LA-2A, 1176, Ross Compressor |
| Preamp | 10 | Preamp-only versions of select amp models |
| Pitch | 10 | Pitch shifters, Whammy, polyphonic detune |
| Wah | 9 | Cry Baby, Vox, Fasel |
| Synth | 8 | Oscillator generators, poly synth |
| EQ | 6 | Parametric, graphic, simple |
| Filter | 5 | Autofilter, Mu-Tron, FM4 Voice Box |
| Utility | 6 | Volume pedal, gain block, looper |
| Gate | 3 | Noise gates |
| Routing | 8 | Split, join, and I/O blocks |

Model identifications were cross-referenced with the Helix Native Owner's Manual and the [Line 6 community forum thread](https://line6.com/support/topic/18804-lets-put-the-real-name-to-the-presets/) that collectively decoded the factory preset names.

## Exporting `.hls` Files from Helix Native

To export the factory setlists from your own installation:

1. Open **Helix Native** as a plugin in your DAW (or use HX Edit for hardware Helix units)
2. In the preset browser, navigate to the **Setlists** level
3. Right-click on a setlist name (e.g., "FACTORY 1")
4. Select **Export** and save as an `.hls` file
5. Repeat for each setlist you want to document

The `.hls` files in this repository were exported from **Helix Native v3.82**. If Line 6 updates the factory presets in a future firmware version, you can re-export and regenerate the document.

## Regenerating the PDF

### Prerequisites

- Python 3.8+
- A LaTeX distribution with `pdflatex` (e.g., TeX Live, MiKTeX)
- Required LaTeX packages: `geometry`, `booktabs`, `longtable`, `hyperref`, `xcolor`, `titlesec` (all included in standard TeX Live)
- Python standard library only — no pip dependencies

### Build

```bash
# Generate the .tex file from all three setlists
python3 generate_latex.py "FACTORY 1.hls" "FACTORY 2.hls" TEMPLATES.hls \
    -o "Helix Native Presets.tex"

# Compile to PDF (three passes for stable table of contents and hyperlinks)
pdflatex -interaction=nonstopmode "Helix Native Presets.tex"
pdflatex -interaction=nonstopmode "Helix Native Presets.tex"
pdflatex -interaction=nonstopmode "Helix Native Presets.tex"
```

The generator auto-detects setlist type (Factory 1, Factory 2, or Templates) from the filename and applies the appropriate section grouping.

### Using `helix_parser.py` Standalone

The parser can also be used independently to inspect presets or export to Excel:

```python
import helix_parser as hp

# Parse a setlist
presets = hp.parse_hls("FACTORY 1.hls")

# Inspect a single preset
preset = presets[0]
print(preset['meta']['name'])  # "US Double Nrm"

# Extract blocks with real hardware names
blocks = hp.extract_blocks(preset)
for b in blocks:
    print(f"{b['category']:8s} {b['l6_name']:25s} → {b['real_name']}")

# Look up any model ID
info = hp.MODEL_DB.get("HD2_AmpBritPlexi")
# ('Amp', 'Brit Plexi Brt', 'Marshall Super Lead 100 (Bright)')
```

## Extending the Document

### Adding Presets to the Decoded Name Database

The `PRESET_INFO` dictionary in `generate_latex.py` maps each preset name to a `(decoded_name, description)` tuple. To add or update a preset's decoded name:

```python
PRESET_INFO = {
    ...
    "Your Preset Name": ("Decoded Real Name", "Description of what this preset sounds like."),
}
```

### Adding Artist, Genre, or Pickup Tags

Three additional dictionaries control the index appendices:

```python
PRESET_ARTISTS = {
    "Preset Name": ["Artist Name (Guitarist)"],
}

PRESET_GENRES = {
    "Preset Name": ["Genre1", "Genre2"],
}

PRESET_PICKUPS = {
    "Preset Name": ("Humbucker", "Bridge", "Rationale for this recommendation."),
}
```

### Adding New Model IDs

If a future firmware update introduces new models, add them to `MODEL_DB` in `helix_parser.py`:

```python
MODEL_DB = {
    ...
    "HD2_AmpNewModel": ("Amp", "Helix Display Name", "Real Hardware Equivalent"),
}
```

## Methodology Notes

- **Preset name decoding** is based on community consensus from the Line 6 forum, cross-referenced with the signal chain contents (amp models, effects, tempo) to verify attributions. Some attributions are speculative where the community hasn't reached consensus.
- **Pickup recommendations** are inferred from the canonical guitar/amp pairings associated with each preset's target tone, referenced artist, or genre. They represent the most authentic starting point, not the only option.
- **Genre tags** reflect the primary musical context for each preset. Many presets span multiple genres and appear under each applicable heading.
- **"Either" pickup recommendations** indicate presets where the tone is defined more by the amp/effects than the pickup type, or where the original artist used varying guitars.

## AI Disclosure

This project was developed with the assistance of **Anthropic's Claude Opus 4.6** large language model, operating under the supervision of the human author. The LLM was used for:

- **Preset name decoding** — inferring artist, song, and tonal references from cryptic preset names by cross-referencing signal chain contents, amp models, tempo values, and community forum sources
- **Tonal descriptions** — writing the preset descriptions based on the decoded references and signal chain analysis
- **Pickup recommendations** — inferring canonical guitar/pickup pairings from the identified artist, genre, and amp context for each preset
- **Genre and artist tagging** — classifying presets into musical genres and associating them with artists based on the decoded names and signal chains
- **Code generation** — writing the Python parser (`helix_parser.py`), LaTeX generator (`generate_latex.py`), and this README
- **Model identification** — building the 342-entry `MODEL_DB` by cross-referencing internal Helix model IDs with the Owner's Manual and community sources

All AI-generated content was reviewed, verified, and where necessary corrected by the human author. The raw preset data (`.hls` files) and the structural decisions about document organization were provided by the human author.

## Disclaimer

The Python scripts and LaTeX source in this repository are provided primarily for explanatory purposes — to document the methodology used to compile the reference document. They are offered as-is, with no guarantee of support or ongoing maintenance.

If you find errors or omissions in the reference document itself (incorrect artist attributions, missing presets, wrong hardware identifications, etc.), you are welcome to [open a GitHub issue](https://github.com/Tonalize/HelixNativePresets/issues) and we will do our best to address them.

## License

The `.hls` setlist files contain factory preset data that is the intellectual property of Line 6 / Yamaha Guitar Group. They are included here for reference and interoperability purposes. The Python scripts and LaTeX source are provided as-is for personal and community use.

## Acknowledgments

- The [Line 6 community forum](https://line6.com/support/topic/18804-lets-put-the-real-name-to-the-presets/) contributors who collectively decoded the factory preset names
- Line 6 / Yamaha Guitar Group for creating the Helix platform
