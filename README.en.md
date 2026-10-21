# A7R6 Looks

**12 Sony Creative Looks reverse-engineered for the Sony A7R VI (ILCE-7RM6) — profiles for Lightroom / Camera Raw**

[中文](README.md) | **English**

![License: Code](https://img.shields.io/badge/License%20(code)-MIT-blue.svg)
![License: Profiles](https://img.shields.io/badge/License%20(profiles)-CC%20BY--NC%204.0-lightgrey.svg)
![Status](https://img.shields.io/badge/Status-Beta-orange.svg)
![Camera](https://img.shields.io/badge/Sony-A7R%20VI%20(ILCE--7RM6)-blue.svg)
![Looks](https://img.shields.io/badge/Looks-12%20Creative%20Looks-green.svg)
![Table](https://img.shields.io/badge/RGBTable-64%C2%B3%20ProPhoto-purple.svg)

⚠️ **If the looks don't take effect, update Camera Raw to 18.7 or later.**

> ⚠️ **Beta notice**: personal reverse-engineering project, in **beta**. **Not affiliated with Sony or Adobe.** For personal, non-commercial use only — **commercial use is prohibited**. The goal is "close to the in-camera look", not colorimetric accuracy.

---

## Contents

- [Background](#background)
- [Included looks](#included-looks)
- [Design](#design)
- [Features](#features)
- [Installation](#installation)
- [Sample comparison](#sample-comparison)
- [Accuracy](#accuracy)
- [How it works](#how-it-works)
- [Known limitations](#known-limitations)
- [Credits](#credits)
- [License](#license)

---

## Background

The A7R VI is recent enough that Adobe does not ship a Camera Matching profile for it. In Lightroom / Camera Raw, Adobe Color, Adobe Standard and even Adobe Landscape all drift away from what the camera and Sony's Imaging Edge Desktop (IEDT) produce — greens lean yellow, saturation is muted.

Instead of fitting an empirical "Adobe output → Sony output" curve, this project **moves Sony's actual look pipeline into the profile**:

- the parameters of all 12 Creative Looks are read from the encrypted SR2 data inside any A7R6 ARW;
- the constant tables the pipeline needs are located in the locally installed Imaging Edge Edit;
- the pipeline is evaluated on a regular grid and written as a native ACR 3D table (`RGBTable`).

Each look is therefore a deterministic 64³ mapping — no training images involved.

## Included looks

| Code | Name | Character |
|---|---|---|
| ST | Standard | Sony's default baseline |
| VV | Vivid | Punchy, high saturation and contrast |
| NT | Neutral | Flat, low saturation, made for grading |
| PT | Portrait | Soft, skin-friendly |
| FL | Film | Cinematic, teal-orange lean |
| VV2 | Vivid 2 | Restrained vivid |
| IN | Instant | Matte, lifted blacks |
| SH | Soft High-key | Soft, low contrast |
| BW | Black & White | Monochrome |
| SE | Sepia | Sepia toned |
| FL2 | Film 2 | Gentle cinematic |
| FL3 | Film 3 | Warm cinematic |

## Design

- **Algorithm-level, not curve fitting**: the profiles are a discretisation of Sony's look pipeline, so they need no per-scene retraining;
- **No Adobe color on top**: a custom linear base DCP makes ACR's working space equal the white-balanced camera RGB, avoiding Adobe's own color and tone processing;
- **Tone included**: the profiles carry the full tone rendering (curves, fade, chroma distribution), so the look is the starting point, not an afterthought.

## Features

- 🎨 **All 12 looks**: ST / VV / VV2 / NT / PT / FL / FL2 / FL3 / IN / SH / BW / SE
- 🎯 **High fidelity**: ΔE₀₀ ≈ 0.75–1.00 against IEDT exports
- 📦 **Reproducible**: parameters come from your ARW, constants from your installed software
- 🔧 **Native format**: `crs:RGBTable` (64³, ProPhoto gamma 1.8), executed by Camera Raw
- 🧩 **Drop-in**: one base DCP plus a set of look XMPs

## Installation

### 1. Download

Grab everything under `profiles/`: `SonyA7R6 Linear Base.dcp` and the 12 `A7R6 *.xmp` files.

### 2. Install

You need **both** file types (the look XMPs depend on the base DCP), placed in the **current user's** Adobe folders:

**Windows**

| File | Destination |
|---|---|
| `SonyA7R6 Linear Base.dcp` | `%APPDATA%\Adobe\CameraRaw\CameraProfiles\` |
| `A7R6 *.xmp` (12 files) | `%APPDATA%\Adobe\CameraRaw\Settings\` |

**macOS**

| File | Destination |
|---|---|
| `SonyA7R6 Linear Base.dcp` | `~/Library/Application Support/Adobe/CameraRaw/CameraProfiles/` |
| `A7R6 *.xmp` (12 files) | `~/Library/Application Support/Adobe/CameraRaw/Settings/` |

- Create the folders if they don't exist (the `CameraProfiles` level often doesn't);
- These are hidden folders: on Windows press `Win+R`, paste the path, hit Enter; on macOS use Finder → Go to Folder (`Cmd+Shift+G`) and type the full path **starting with `~`**;
- ⚠️ **macOS warning**: `/Library/Application Support/...` (system) and `~/Library/Application Support/...` (user) are different folders — use the **user-level one with the `~`**;
- Older revisions of this guide put the DCP in the system-level folder (`C:\ProgramData\...` / `/Library/...`) — that requires admin rights and is not scanned in some environments. **Use the user-level paths above.**

**Or do it in one go from Terminal on macOS** (`cd` into the extracted `profiles` folder first):

```bash
mkdir -p ~/Library/Application\ Support/Adobe/CameraRaw/CameraProfiles \
         ~/Library/Application\ Support/Adobe/CameraRaw/Settings
cp "SonyA7R6 Linear Base.dcp" ~/Library/Application\ Support/Adobe/CameraRaw/CameraProfiles/
cp A7R6\ *.xmp ~/Library/Application\ Support/Adobe/CameraRaw/Settings/

# verify (should show 1 dcp and 12 xmp files)
ls ~/Library/Application\ Support/Adobe/CameraRaw/CameraProfiles/
ls ~/Library/Application\ Support/Adobe/CameraRaw/Settings/
```

### 3. Before you start, check three things

1. **Camera**: these profiles only apply to **ILCE-7RM6 (A7R VI)** RAW files. With files from any other camera, the group simply won't appear in the Profile browser — that's Adobe's camera-scoping mechanism, not a failed install;
2. **App**: works with **Lightroom Classic** and **Photoshop (Camera Raw)**. The **cloud-based Lightroom desktop does not read these local folders**;
3. **Version**: requires **Camera Raw 18.7 or later**.

Fully **quit and restart** Lightroom / Photoshop after copying (profiles are scanned at startup only).

### 4. Use

In the Profile browser, expand the group **Sony A7R6 (12)** and pick a look (e.g. `A7R6 ST`).

> ⚠️ You'll also see a standalone **SonyA7R6 Linear Base** entry — that's the shared **linear base** for all 12 looks (every DCP camera profile shows up in the list; it can't be hidden). **Don't pick it.** Choosing it gives you plain decoding with no Sony look at all — flat and lifeless.

- Keep white balance on **As Shot**;
- The profile already contains the tone rendering — no additional preset needed;
- The **Amount** slider next to the profile can fine-tune strength.

> Note: the look XMPs reference the base DCP by name. Copying the XMPs without the DCP will show a "profile missing" error.

### Profiles not showing up? Check in this order

| Check | Why |
|---|---|
| Did you pick a look, not the base? | Choose `A7R6 ST` etc. inside the `Sony A7R6 (12)` group; picking the standalone `SonyA7R6 Linear Base` gives a flat image that looks "not working" |
| Was the RAW shot on an A7R VI? | Other cameras never show these profiles — by design |
| Is the DCP really in the folder? | Look with your own eyes: actual file, not inside a subfolder, not an alias. On macOS, `/Library` (system) ≠ `~/Library` (user) — a classic mix-up |
| Did you fully restart? | `Cmd+Q` Lightroom/Photoshop completely, then relaunch |
| Are you on Classic? | Cloud-based Lightroom desktop can't use local profiles |
| Is your version new enough? | Camera Raw 18.7 or later — earlier versions may list the looks but not apply them |
| Is "store presets with catalog" on? | Preferences → Presets → **Store presets with this catalog**: when enabled, the global CameraRaw folders are bypassed — both the XMPs and the DCP must go into `<catalog folder>\Lightroom Settings\` (Settings / CameraProfiles subfolders). A mismatch produces exactly "listed but all inert" |

### All 12 looks show up, but they all render identically?

The XML header of the XMP loaded fine, but the embedded RGBTable isn't taking effect — **most likely an incomplete download** (each XMP is 1.7–1.9 MB; an unstable connection or a size-limited mirror can truncate the file so only the header survives). Check the file sizes (the 12 files should be 1.68–1.90 MB and **all different**); if they don't match, download again — the single Release zip is far more robust than fetching raw files one by one. If the sizes are fine and the problem persists, please open an issue with your Lightroom version.

## Sample comparison

Same RAW, this profile versus Sony's own IEDT render:

![ST comparison](pic/ST对比.jpg)

*Left: this project's ST profile. Right: IEDT output — tone and color essentially coincide.*

## Accuracy

Same ARW, this profile (LR JPEG export) versus IEDT (16-bit TIFF), geometrically aligned and downsampled 8× (sRGB / D50, 500 px long edge):

| Scene | ΔE76 | ΔE00 | Note |
|---|---|---|---|
| DSC00697 (lake) | 0.98 | 0.75 | used for black-level calibration |
| DSC00737 (forest) | 0.98 | 0.79 | used for white-balance compromise |
| DSC00642 (documentary) | 1.15 | 1.00 | **held out, not used in calibration** |

Average: ΔE76 ≈ 1.04, ΔE00 ≈ 0.85.

Beyond the look pipeline, generation bakes in a **shared calibration** (`calib.json`):

- black level / gain: R ×0.9986, G ×0.9963, B ×0.9987 with ≈ −0.011 offset — aligns ACR's black point and overall brightness with IEDT;
- white-balance compromise: R ×1.002, G ×0.994, B ×0.990 — compensates the two applications' differing interpretation of "As Shot".

Both are look-independent, so all 12 tables share the same coefficients. After calibration ΔL is within ±0.2; the residual is chromatic and concentrates in foliage-heavy scenes (mid-tone Δa ≈ −0.2), which comes from the two demosaic/chroma pipelines and is outside a profile's reach.

The remaining 10 looks use identical code and data but have **no IEDT reference render** yet (same situation as the reference project); they are validated structurally only: BW is strictly neutral, Sepia is sepia-toned, the others are neutral on the gray axis.

## How it works

```
ARW (encrypted SR2)
  └─ 12 look IFDs: 0x780f / 0x7805 / 0x7806 / 0x7842-46 ……
        │
        ▼
  Look pipeline (per pixel)
   LinearMatrix16 → MainGamma → RGB2YCC → quadrant processing
   → ChromaSuppress → AreaComp → YGamma → YCC2RGB → Effect (BW/SE)
        ▲
        │  constant tables (atan, contrast family) read from the local Edit.exe
        │
        ▼
   f_look ∘ E⁻¹  → 64³ RGBTable → .xmp
```

- **E** is Camera Raw's internal encoding of the pipeline input (linear mid-tones, hue-preserving highlight compression), calibrated on a synthetic chart and inverted here;
- the base DCP takes its ColorMatrix from Adobe Standard A7R6 (so white balance behaves like Adobe's), sets ForwardMatrix to linear ProPhoto → XYZ D50 and an identity tone curve;
- the table is written as `crs:RGBTable` + `crs:Table_<MD5>` (base85 + zlib), **not** `crs:LookTable`, which only accepts the DNG hue/sat format and would be silently ignored.

Details of the reverse engineering (table offsets, pipeline stages, calibration) are documented in [TECHNICAL.md](TECHNICAL.md) (Chinese).

## Known limitations

- **DRO / high dynamic range**: spatially adaptive, not part of the per-pixel pipeline, therefore not included;
- **Sharpening / noise reduction / clarity**: implemented per application, not a profile's job;
- **Fade**: baked at the camera defaults (FL2/FL3 = 1, IN = 3, SH = 6) and not adjustable afterwards;
- **Camera-specific**: parameters come from A7R6 ARWs; do not use on other bodies;
- **E model**: calibrated against a specific Camera Raw build; a major Adobe pipeline change would require recalibration.

## Credits

Approach and pipeline implementation are based on:

- **[751K/sony-a7m5-looks](https://github.com/751K/sony-a7m5-looks)** — a bit-exact reverse engineering and Python port of Sony Imaging Edge Edit's look pipeline (MIT License). This project builds on it: A7R6 parameter extraction, Windows constant-table locating, and ACR profile generation.

## License

This repository uses **split licensing**:

| Scope | License |
|---|---|
| `code/**` (generator and scripts) | **MIT** |
| `profiles/**`, `pic/**`, all documentation | **CC BY-NC 4.0** ([full text](LICENSE-CC-BY-NC-4.0.txt)) |

- ✅ Code may be used, modified and redistributed (keep the copyright notice)
- ✅ Profiles may be shared and adapted with attribution, non-commercially
- ❌ **Commercial use of the profiles is prohibited**
- ⚠️ Not affiliated with Sony or Adobe; third-party code and trademark notices in [THIRD-PARTY.md](THIRD-PARTY.md)

**Disclaimer**: provided "as is", without warranty of any kind. Use at your own risk. If reverse engineering is restricted in your jurisdiction, comply with local law.
