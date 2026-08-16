# OgreTools

A collection of small Python utilities for working with **Inazuma Eleven 3: The Ogre** game resources, with a focus on character names, special-move names, ARC/CTPK extraction, and replacement graphics.

These scripts were developed as part of the reverse-engineering work described in the accompanying project article.

The repository is **not a single turnkey modding application**. Each script handles a specific stage of the workflow, and some of them are experimental or contain project-specific assumptions.

---

## Requirements

### Python

Python 3 is required.

### Python packages

`write_text.py` requires **Pillow**:

```text
pip install Pillow
````

The other scripts use only Python's standard library.

### External tools

The workflow also relies on external tools:

* **Kuriimu2 / Kuriimu2.Cmd** for Level-5 resource extraction
* **ctpktool** for rebuilding CTPK resources

These tools are not included in this repository.

---

# Scripts

## `extract_unitbase.py`

Handles extraction and reinsertion of character names from `unitbase.dat`.

### What it does

`extract_unitbase.py` understands the character-record layout used by the target `unitbase.dat`:

* starting offset: `0x68`
* ending offset: `0x3C6E0`
* record size: `0x68`

Within each record:

* full name: offset `0x00`, length `0x1C`
* nickname: offset `0x1C`, length `0x10`

The script can either extract these fields to CSV or write edited values back into the DAT file.

### Character encoding

Without `--japanese`, the script uses UTF-8 for the name fields.

With `--japanese`, it uses **Shift-JIS**.

The `--japanese` flag affects both extraction and repacking.

### Usage

Extract names:

```text
python extract_unitbase.py --extract --dat unitbase.dat --csv characters.csv
```

Extract Japanese names:

```text
python extract_unitbase.py --extract --dat unitbase.dat --csv characters_jp.csv --japanese
```

Repack:

```text
python extract_unitbase.py --repack --dat unitbase.dat --csv characters.csv
```

Repack Japanese data:

```text
python extract_unitbase.py --repack --dat unitbase.dat --csv characters_jp.csv --japanese
```

### CSV format

The generated CSV contains:

* `global_offset`
* `full_name`
* `nickname`

The `global_offset` value is hexadecimal and identifies the beginning of the corresponding record.

### Important behavior

The script preserves the fixed field lengths.

Names are encoded, truncated to the allocated field size, and padded with null bytes.

The script modifies the existing DAT file in place when using `--repack`.

For that reason, keeping a backup of the original file is strongly recommended.

---

# `command_extract.py`

Extracts and repacks special-move names from `command.STR`.

This is a more specialized parser than `extract_unitbase.py`.

## Extraction

The script scans `command.STR` looking for entries that appear to represent special moves.

The scan starts from:

* `0xCC0` for the normal configuration
* `0x2000` when `JAPANESE = True`

The Japanese configuration is currently enabled in the source.

The data is processed in `0x10`-byte blocks.

### Move detection

The script looks for Japanese elemental markers corresponding to:

* Fire
* Wind
* Mountain
* Forest

These are represented by the byte values stored in `JP_ELEMENTS`.

A block is considered a possible attribute block when the expected markers appear inside square brackets.

Once an attribute block is found, the script searches backwards by:

* `0x20`
* `0x10`
* `0x00`

bytes

for a valid move name.

The extracted name is decoded as Shift-JIS.

### Output

Extraction produces a CSV containing:

```text
offset,name
```

The offset is hexadecimal.

### Usage

Extract special moves:

```text
python command_extract.py --extract-hissatsu --dat command.STR --csv mossejap.csv
```

---

## Repacking

`command_extract.py` can also write names from the CSV back into a DAT/STR-style resource.

Usage:

```text
python command_extract.py --repack-hissatsu --dat command.STR --csv mossejap.csv --out command_modified.STR
```

For every entry, the script:

1. Reads the hexadecimal offset.
2. Clears `0x20` bytes at that location.
3. Encodes the replacement name as Shift-JIS.
4. Writes at most `0x20` bytes.
5. Produces the output resource.

### Important limitation

This script does **not** establish correspondence between Japanese offsets and localized-version offsets.

It simply operates on the offsets contained in the CSV.

If the Japanese and target versions store the same move at different offsets, an additional mapping step is required.

---

# `extract_arcs.py`

Automates extraction of ARC files and their embedded CTPK resources through Kuriimu2.Cmd.

## What it does

The script:

1. Finds every `.arc` file in the supplied directory.
2. Exports each ARC using the configured Level-5 ARC plugin.
3. Looks for the generated `_arc` directory.
4. Finds `.bin` files inside it.
5. Renames those files to `.ctpk`.
6. Exports the CTPK resources with Kuriimu2.

The ARC plugin ID currently used by the script is:

```text
db8c2deb-f11d-43c8-bb9e-e271408fd896
```

### Usage

```text
python extract_arcs.py --kuriimu path/to/Kuriimu2.Cmd.exe --input path/to/arcs
```

or:

```text
python extract_arcs.py -k path/to/Kuriimu2.Cmd.exe -i path/to/arcs
```

### Expected input

The input directory is scanned only for `.arc` files in that directory.

### Expected output

For an input ARC such as:

```text
example.arc
```

Kuriimu2 is expected to create a corresponding directory:

```text
example_arc/
```

The script then processes the `.bin` files found there.

### Failure behavior

If Kuriimu2 returns a non-zero exit code, the script logs the failure and continues with the next ARC.

If Kuriimu2 does not create the expected `_arc` directory, the script exits.

---

# `write_text.py`

Generates PNG images containing move names.

This is the rendering component of the project.

It uses **Pillow** and provides three rendering modes.

## Mode 0

`render_mode0()` creates a:

* `128 × 16` PNG
* grey text
* white outline
* grey shadow

Font:

```text
TCCB____.TTF
```

Font size:

```text
18
```

The generated text is fitted into a region beginning around pixel `6` and extending to pixel `86`.

---

## Mode 1

`render_mode1()` creates another:

* `128 × 16` PNG
* red text
* white outline
* grey shadow

It uses the same font as Mode 0:

```text
TCCB____.TTF
```

The text color is:

```text
(247, 8, 8, 255)
```

---

## Mode 2

`render_mode2()` creates a larger:

* `256 × 32` PNG
* white text
* black outline

Font:

```text
DejaVuSansCondensed-Bold.ttf
```

Font size:

```text
22
```

Unlike Modes 0 and 1, this renderer uses a different font and layout.

---

## Rendering scale

All modes initially render at a scale factor of `4` and then resize back to the final resolution using nearest-neighbor scaling.

This is used to control the appearance of the outlines and preserve a pixel-oriented look.

Long text can be horizontally compressed to fit the target dimensions.

---

## Usage

```text
python write_text.py --text "Example Move" --mode 0 --output mode0.png
```

Mode 1:

```text
python write_text.py --text "Example Move" --mode 1 --output mode1.png
```

Mode 2:

```text
python write_text.py --text "Example Move" --mode 2 --output mode2.png
```

Short options are also available:

```text
python write_text.py -t "Example Move" -m 2 -o mode2.png
```

### Required arguments

`--text` / `-t`

Text to render.

`--mode` / `-m`

Must be one of:

* `0`
* `1`
* `2`

`--output` / `-o`

Destination PNG path.

### Fonts

The required font files are referenced by filename rather than discovered automatically.

Therefore the fonts must be available in the working directory or otherwise resolvable from the paths expected by Pillow.

---

# `make_pngs.py`

A small wrapper around `write_text.py`.

Despite the presence of CSV-loading functions and constants for move databases, the **current version of this script does not yet use those datasets to select the move automatically**.

Instead, its current main workflow renders a fixed test string:

```text
Buona la pizza
```

in all three modes.

## Current behavior

The script calls `write_text.py` three times:

* Mode 0
* Mode 1
* Mode 2

By default it creates:

```text
mode0.png
mode1.png
mode2.png
```

### Usage

```text
python make_pngs.py
```

To specify an output directory:

```text
python make_pngs.py --output generated
```

The script will create the directory if necessary.

### Current output

With:

```text
python make_pngs.py --output generated
```

the resulting files are:

```text
generated/mode0.png
generated/mode1.png
generated/mode2.png
```

---

## CSV-related code

The script contains loaders for:

* `final_moves.csv`
* `mossejap.csv`

and defines the name:

```text
write_text.py
```

as the renderer it invokes.

However, those CSV-loading functions are not currently used by `main()`.

The current implementation should therefore be considered a **test/generator wrapper**, rather than the finished automatic move-to-image pipeline.

---

# `mastermind.py`

The main automation script for processing extracted CTPK resources and putting the rebuilt data back into ARC files.

Its intended purpose is to automate the final resource-replacement stage.

## General workflow

Given a root directory, the script:

1. Finds directories named `00000000_ctpk`.
2. Looks for PNG files inside them.
3. Associates each CTPK directory with its parent `_arc` directory.
4. Finds the corresponding original `.arc`.
5. Rebuilds the CTPK with `ctpktool`.
6. Replaces the CTPK data inside the ARC.
7. Repeats the process for all matching packages.

---

## Locating CTPK packages

The script recursively searches for:

```text
00000000_ctpk
```

directories.

A package is accepted only if at least one PNG exists inside that directory.

When several PNGs are available, the script prefers one whose filename contains:

```text
ie03o
```

Otherwise it uses the first PNG it finds.

---

## Matching ARC files

The parent directory is expected to follow the naming convention:

```text
<name>_arc
```

The script transforms that into the expected ARC filename:

```text
<name>.arc
```

It searches:

1. the root directory recursively
2. the parent directory
3. the root tree again for the exact filename

This allows the extracted ARC directory and original ARC file to be located even when they are not side-by-side.

---

## Rebuilding CTPK

`mastermind.py` calls `ctpktool` using the extracted `00000000.bin` resource and the `00000000_ctpk` directory.

The command is generated internally by the script.

The script expects either:

```text
ctpktool.exe
```

or:

```text
ctpktool
```

to be available on the system PATH.

A custom executable can instead be supplied with `--ctpktool`.

---

## CTPK location inside ARC

The script expects the CTPK magic:

```text
CTPK
```

at offset:

```text
0x80
```

This is represented by the constant `CTPK_OFFSET`.

Before replacing the data, the script checks that the expected magic is present.

If it is not, the package is rejected.

---

## ARC replacement

After rebuilding the CTPK, the resulting binary data is written directly into the original ARC starting at offset `0x80`.

The script does not perform a general ARC rebuild.

It performs a direct binary replacement of the CTPK payload.

This means the replacement operation assumes that the new resource fits into the existing ARC layout.

---

## Usage

Basic:

```text
python mastermind.py --root path/to/extracted/arcs
```

With an explicit `ctpktool` executable:

```text
python mastermind.py --root path/to/extracted/arcs --ctpktool path/to/ctpktool.exe
```

Dry run:

```text
python mastermind.py --root path/to/extracted/arcs --dry-run
```

### Arguments

`--root`

Required.

Root directory containing the extracted ARC/CTPK structure.

`--ctpktool`

Optional path to `ctpktool.exe` or another compatible executable.

`--dry-run`

Prints the operations without actually running `ctpktool` or modifying the ARC files.

---

# Current `mastermind.py` integration

`mastermind.py` also attempts to generate PNGs before processing the extracted packages.

It looks for:

```text
mossejap.csv
```

and invokes:

```text
make_pngs.py
```

for each entry.

However, the current `make_pngs.py` implementation does not yet use the supplied offset to generate the corresponding move image. It currently renders the fixed test text described above.

Therefore this part of `mastermind.py` should currently be regarded as **experimental/incomplete integration**.

The CTPK/ARC replacement stage is separate from that limitation.

---

# Files used by the workflow

The scripts refer to the following project data files:

## `unitbase.dat`

Character database.

Processed by:

```text
extract_unitbase.py
```

---

## `command.STR`

Special-move names and related string data.

Processed by:

```text
command_extract.py
```

---

## `final_moves.csv`

Referenced by:

```text
make_pngs.py
```

The current version defines support for this file, but does not actually load it from `main()`.

---

## `mossejap.csv`

Japanese special-move name data.

Used directly by `mastermind.py` when it attempts to drive the PNG-generation stage.

It is also defined as an input by `make_pngs.py`, although the current `main()` does not yet consume it.

---

## Font files

`write_text.py` expects:

```text
TCCB____.TTF
```

and:

```text
DejaVuSansCondensed-Bold.ttf
```

---

# Recommended workflow

A practical workflow using the current scripts is:

### 1. Extract `unitbase.dat`

Use:

```text
extract_unitbase.py
```

to export character records to CSV.

Repeat with `--japanese` for Japanese data.

### 2. Modify/reinsert character names

Edit the generated CSV and use:

```text
extract_unitbase.py --repack
```

to write the data back into the target DAT.

### 3. Extract Japanese move names

Use:

```text
command_extract.py --extract-hissatsu
```

to create:

```text
mossejap.csv
```

### 4. Extract ARC/CTPK resources

Use:

```text
extract_arcs.py
```

to batch-export the relevant ARC files and their CTPK resources.

### 5. Generate test/output graphics

Use:

```text
write_text.py
```

directly when a specific text and rendering mode are required.

`make_pngs.py` currently provides a convenience wrapper for generating all three modes from one fixed test string.

### 6. Rebuild and replace CTPK resources

Use:

```text
mastermind.py
```

after the desired PNG resources are present in the extracted CTPK directories.

---

# Script relationship

The tools can be viewed as a pipeline:

```text
unitbase.dat
    │
    └── extract_unitbase.py
            │
            └── character CSV
                    │
                    └── extract_unitbase.py --repack

command.STR
    │
    └── command_extract.py
            │
            └── mossejap.csv

ARC files
    │
    └── extract_arcs.py
            │
            └── extracted CTPK resources
                    │
                    ├── write_text.py
                    │
                    └── make_pngs.py
                            │
                            └── PNG resources
                                    │
                                    └── mastermind.py
                                            │
                                            └── modified ARC files
```

The diagram describes the intended workflow; in particular, the automatic CSV → PNG integration is not fully implemented in the current `make_pngs.py`.

---

# Encoding and binary assumptions

These scripts rely on several format-specific assumptions discovered during the reverse-engineering process.

### Character data

`extract_unitbase.py` uses fixed-size records and fixed-size name fields.

### Japanese text

Japanese text is handled using Shift-JIS in:

* `extract_unitbase.py`
* `command_extract.py`

### Move detection

`command_extract.py` identifies candidate move entries using specific Japanese elemental byte values.

### Graphics

The ARC workflow assumes that extracted resources contain CTPK data and that the expected CTPK payload begins at `0x80` for the replacement performed by `mastermind.py`.

These assumptions are specific to the game resources this project targets.

---

# Important limitations

## The scripts are project-specific

They should not be assumed to work unchanged on other games, other releases, or different revisions of the same game.

## Some paths and filenames are hard-coded

Several scripts expect specific filenames or executables, such as:

* `write_text.py`
* `mossejap.csv`
* `ctpktool`
* `TCCB____.TTF`
* `DejaVuSansCondensed-Bold.ttf`

## `make_pngs.py` is currently a test implementation

Its CSV support is present, but the active `main()` generates the fixed string:

```text
Buona la pizza
```

for all three modes.

## `mastermind.py` performs direct binary replacement

It assumes that the rebuilt CTPK can be inserted at offset `0x80` in the original ARC without requiring a full archive rebuild.

## No automatic Japanese/target move matching

`command_extract.py` extracts names from a resource, but it does not solve the cross-version offset mapping problem by itself.

---

# Backups

Always keep backups of the original:

* `unitbase.dat`
* `command.STR`
* `.arc` files
* extracted `.ctpk` resources

In particular, `extract_unitbase.py --repack` modifies the supplied DAT file directly, while `mastermind.py` writes changes directly into the original ARC file.

Working on copies is strongly recommended.

---

# Project status

This repository should currently be considered a collection of **research and modding utilities** rather than a polished end-user application.

Some components are complete enough for practical use, while others are intermediate or experimental.

The most notably incomplete part is the automatic move-image generation pipeline:

* `command_extract.py` can extract move names.
* `write_text.py` can render move names.
* `make_pngs.py` contains CSV-related support but currently renders a fixed test string.
* `mastermind.py` contains integration for calling `make_pngs.py`, but that integration depends on the still-incomplete behavior of `make_pngs.py`.

This separation is intentional in the sense that the repository preserves the individual tools used during development.

---

# License

OgreTools is licensed under the ISC License.

Do not redistribute Nintendo/Level-5 game assets, extracted archives, fonts, or other copyrighted resources unless you have the appropriate rights to do so.