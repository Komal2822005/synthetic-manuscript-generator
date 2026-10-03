# Synthetic Manuscript Generator

A Python pipeline for generating synthetic historical manuscript images and
their corresponding transcriptions for OCR dataset creation.

The project focuses on three Indic scripts — **Devanagari, Modi, and Sharada** —
and combines text rendering with manuscript-style backgrounds, handwriting
variation, ink degradation, page deformation, and fold effects.

## Overview

Historical manuscripts are valuable OCR resources, but collecting and manually
annotating large amounts of manuscript data is difficult. This project
generates paired synthetic samples automatically:

```text
manuscript image (.png)  →  transcription (.md)
```

The same text used to render an image is saved as its ground-truth
transcription, making the generated samples directly usable for OCR dataset
preparation.

## How It Works

Each sample passes through a sequence of independent processing stages:

```text
Source Text
    ↓
Passage Selection
    ↓
Paper Background
    ↓
Text Rendering
    ↓
Handwriting Variation
    ↓
Ink Effects
    ↓
Page Deformation
    ↓
Fold / Aging Effects
    ↓
PNG + MD Pair
```

The implementation is intentionally modular so that individual generation
stages can be changed without rewriting the complete pipeline.

## Project Structure

```text
synthetic-manuscript-generator/
│
├── data/
│   ├── raw/
│   │   ├── devanagari.md
│   │   ├── Modi.md
│   │   └── sharada.md
│   │
│   └── fonts/
│       ├── devanagari.ttf
│       ├── Modi.ttf
│       └── Sharada.ttf
│
├── src/
│   ├── __init__.py
│   ├── background.py
│   ├── config.py
│   ├── deformation.py
│   ├── effects.py
│   ├── folds.py
│   ├── generator.py
│   ├── handwriting.py
│   ├── layout.py
│   ├── renderer.py
│   └── text_processor.py
│
├── output/
├── temp/
│
├── generate.py
├── validate_dataset.py
├── requirements.txt
└── README.md
```

### Module responsibilities

| Module | Purpose |
|---|---|
| `text_processor.py` | Loads manuscript text and selects passages |
| `background.py` | Creates aged manuscript-style paper backgrounds |
| `renderer.py` | Renders script text onto the generated page |
| `handwriting.py` | Adds subtle waviness and baseline variation |
| `effects.py` | Applies ink variation, fading, bleeding, and smudging |
| `deformation.py` | Simulates page surface distortion |
| `folds.py` | Adds folds, creases, and edge aging |
| `layout.py` | Adds manuscript-style layout elements |
| `generator.py` | Connects the complete generation pipeline |
| `config.py` | Stores paths and generation parameters |
| `generate.py` | Command-line entry point |

## Supported Scripts

The current configuration supports:

- Devanagari
- Modi
- Sharada

Each script has its own source text and font:

```text
data/raw/devanagari.md  → data/fonts/devanagari.ttf
data/raw/Modi.md        → data/fonts/Modi.ttf
data/raw/sharada.md     → data/fonts/Sharada.ttf
```

The script configuration is centralized in `src/config.py`, which makes the
pipeline extensible to additional scripts.

## Manuscript Appearance

The image generation process combines several visual transformations to move
the output away from clean digital text.

### Background

The generated page includes:

- Paper texture
- Natural brightness variation
- Aged appearance
- Darkened edges

### Writing

The renderer introduces controlled variation in:

- Line position
- Baseline
- Waviness
- Rotation
- Ink opacity
- Ink tone

### Degradation

Additional effects simulate common physical characteristics of old
manuscripts:

- Faded strokes
- Ink bleeding
- Smudging
- Page warping
- Folds and creases

Layout elements such as margin markers, section markers, and highlighted
regions are also procedurally added.

## Dataset Generation

The assignment requires **100 samples for each script**.

The complete dataset therefore contains:

```text
Devanagari : 100
Modi       : 100
Sharada    : 100
-----------------
Total      : 300
```

The dataset is divided into:

```text
Train      : 85%
Validation : 10%
Test       : 5%
```

For each script this results in:

```text
Train      : 85
Validation : 10
Test       : 5
```

## Output Format

Generated samples are stored by script and split:

```text
output/
├── devanagari/
│   ├── train/
│   ├── validation/
│   └── test/
│
├── modi/
│   ├── train/
│   ├── validation/
│   └── test/
│
└── sharada/
    ├── train/
    ├── validation/
    └── test/
```

Every image has a matching transcription file.

For example:

```text
devanagari_0001.png
devanagari_0001.md
```

The `.md` file contains the exact passage selected for that generated image.

This keeps the image and ground truth synchronized throughout the generation
process.

## Installation

Create a virtual environment:

```powershell
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\activate
```

Install the project dependencies:

```powershell
pip install -r requirements.txt
```

## Running the Generator

The main entry point is `generate.py`.

To generate the complete dataset:

```powershell
python generate.py
```

To generate samples for one script:

```powershell
python generate.py --script devanagari --num-images 10
```

```powershell
python generate.py --script modi --num-images 10
```

```powershell
python generate.py --script sharada --num-images 10
```

To generate all scripts with a specified number of samples:

```powershell
python generate.py --script all --num-images 100
```

A seed can be supplied when reproducible generation is required:

```powershell
python generate.py --seed 42
```

For example:

```powershell
python generate.py --script devanagari --num-images 10 --seed 42
```

## Configuration

The main generation settings are maintained in:

```text
src/config.py
```

Current settings include:

```text
Image size       : 1600 × 1000
Font size        : 45
Page margin      : 130
Line spacing     : 25
Samples/script   : 100
Train split      : 85%
Validation split : 10%
Test split       : 5%
```

Keeping these values in one configuration module makes it easier to experiment
with different dataset sizes and visual parameters.

## Dataset Validation

`validate_dataset.py` is used to verify the generated dataset before
submission or upload.

Run:

```powershell
python validate_dataset.py
```

The validation checks include:

- Image and transcription counts
- PNG/MD filename pairing
- Image dimensions
- Empty transcription files
- Train/validation/test distribution
- Overall dataset consistency

For the completed assignment dataset, the expected result is:

```text
300 images
300 transcription files
300 matching image-text pairs
```

## Hugging Face Dataset

The generated dataset is available on Hugging Face:

https://huggingface.co/datasets/Ankulx13/synthetic-manuscript-generator

It contains three script-specific subsets:

- devanagari
- modi
- sharada

Each subset contains:

- train
- validation
- test

## Reproducibility

The generator uses explicit random seeds for the procedural generation steps.

For example:

```powershell
python generate.py --seed 42
```

Using the same seed and configuration allows the generation process to be
reproduced.

Changing the seed produces different visual variations while keeping the
overall generation pipeline unchanged.

## Implementation Notes

The Indic scripts are rendered as complete text lines rather than manually
placing individual characters. This preserves the shaping behavior provided
by the selected fonts.

The handwriting variation is applied after text rendering through controlled
geometric transformations. This avoids disrupting Unicode shaping while still
introducing visual irregularity.

The current implementation is therefore a practical synthetic-data approach:
the source text and script structure remain controlled, while the manuscript
surface and writing appearance are varied procedurally.



## Requirements

The project uses:

```text
Pillow
NumPy
OpenCV
Hugging Face Datasets
Hugging Face Hub
```

Pinned versions are provided in:

```text
requirements.txt
```

## Project Goal

The final deliverable is a reproducible Python pipeline that can generate
historical manuscript-style training samples at scale while maintaining an
exact transcription for every generated image.

