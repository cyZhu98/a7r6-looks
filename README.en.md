# A7R6 Looks

**12 Sony Creative Looks reverse-engineered for the Sony A7R VI (ILCE-7RM6) — profiles for Lightroom / Camera Raw**

[中文](README.md) | **English**

![License](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)
![Status](https://img.shields.io/badge/Status-Beta-orange.svg)
![Camera](https://img.shields.io/badge/Sony-A7R%20VI%20(ILCE--7RM6)-blue.svg)
![Looks](https://img.shields.io/badge/Looks-12%20Creative%20Looks-green.svg)
![Table](https://img.shields.io/badge/RGBTable-64%C2%B3%20ProPhoto-purple.svg)

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

**Windows**

```text
SonyA7R6 Linear Base.dcp  →  C:\ProgramData\Adobe\CameraRaw\CameraProfiles\
A7R6 *.xmp                →  %APPDATA%\Adobe\CameraRaw\Settings\
```

**macOS**

```text
SonyA7R6 Linear Base.dcp  →  /Library/Application Support/Adobe/CameraRaw/CameraProfiles/
A7R6 *.xmp                →  ~/Library/Application Support/Adobe/CameraRaw/Settings/
```

Fully quit Photoshop / Lightroom and reopen.

### 3. Use

In the Profile browser pick the group **Sony A7R6**, then a look (e.g. `A7R6 ST`).

- Keep white balance on **As Shot**;
- The profile already contains the tone rendering — no additional preset needed;
- The **Amount** slider next to the profile can fine-tune strength.

> Note: the look XMPs reference the base DCP by name. Copying the XMPs without the DCP will show a "profile missing" error.

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

Licensed under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/):

- ✅ Personal study, research and non-commercial use
- ✅ Share and adapt with attribution
- ❌ **Commercial use of any kind is prohibited**
- ⚠️ Not affiliated with Sony or Adobe; trademarks belong to their respective owners

**Disclaimer**: provided "as is", without warranty of any kind. Use at your own risk. If reverse engineering is restricted in your jurisdiction, comply with local law.
