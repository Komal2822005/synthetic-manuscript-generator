from pathlib import Path
import shutil

from .background import generate_paper_background
from .deformation import apply_page_deformation
from .folds import add_folds
from .renderer import render_text
from .text_processor import load_text, get_random_passage

from .config import (
    PROJECT_ROOT,
    OUTPUT_DIR,
    SCRIPT_CONFIG,
    IMAGE_WIDTH,
    IMAGE_HEIGHT,
    FONT_SIZE,
    MARGIN,
    LINE_SPACING,
)


def create_directories(script):
    """Create train, validation and test directories."""

    script_dir = OUTPUT_DIR / script

    train_dir = script_dir / "train"
    validation_dir = script_dir / "validation"
    test_dir = script_dir / "test"

    train_dir.mkdir(parents=True, exist_ok=True)
    validation_dir.mkdir(parents=True, exist_ok=True)
    test_dir.mkdir(parents=True, exist_ok=True)

    return {
        "train": train_dir,
        "validation": validation_dir,
        "test": test_dir,
    }


def get_split(index, total_images):
    """Return dataset split using 85/10/5 ratio."""

    train_count = int(total_images * 0.85)
    validation_count = int(total_images * 0.10)

    if index < train_count:
        return "train"

    elif index < train_count + validation_count:
        return "validation"

    else:
        return "test"


def generate_single_sample(
    script,
    index,
    total_images,
    seed
):
    """Generate one complete manuscript sample."""

    if script not in SCRIPT_CONFIG:
        raise ValueError(f"Unsupported script: {script}")

    script_config = SCRIPT_CONFIG[script]

    text_file = script_config["text_file"]
    font_file = script_config["font_file"]

    # Check input files
    if not text_file.exists():
        raise FileNotFoundError(
            f"Text file not found:\n{text_file}"
        )

    if not font_file.exists():
        raise FileNotFoundError(
            f"Font file not found:\n{font_file}"
        )

    # Load manuscript text
    text = load_text(str(text_file))

    # Select random passage
    passage = get_random_passage(
        text,
        min_chars=400,
        max_chars=800
    )

    # Temporary directory
    temp_dir = PROJECT_ROOT / "temp"
    temp_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # Temporary files
    background_file = (
        temp_dir /
        f"{script}_{index}_background.png"
    )

    rendered_file = (
        temp_dir /
        f"{script}_{index}_rendered.png"
    )

    deformed_file = (
        temp_dir /
        f"{script}_{index}_deformed.png"
    )

    final_file = (
        temp_dir /
        f"{script}_{index}_final.png"
    )

    # --------------------------------------------------
    # STEP 1: Generate aged paper background
    # --------------------------------------------------

    generate_paper_background(
        width=IMAGE_WIDTH,
        height=IMAGE_HEIGHT,
        output_path=background_file,
        seed=seed
    )

    # --------------------------------------------------
    # STEP 2: Render manuscript text
    # --------------------------------------------------

    render_text(
        text=passage,
        font_path=font_file,
        background_path=background_file,
        output_path=rendered_file,
        image_width=IMAGE_WIDTH,
        image_height=IMAGE_HEIGHT,
        font_size=FONT_SIZE,
        margin=MARGIN,
        line_spacing=LINE_SPACING,
        seed=seed
    )

    # --------------------------------------------------
    # STEP 3: Apply page deformation
    # --------------------------------------------------

    apply_page_deformation(
        input_path=rendered_file,
        output_path=deformed_file,
        strength=3.0,
        seed=seed
    )

    # --------------------------------------------------
    # STEP 4: Add folds and aging
    # --------------------------------------------------

    add_folds(
        input_path=deformed_file,
        output_path=final_file,
        number_of_folds=3,
        seed=seed
    )

    # --------------------------------------------------
    # STEP 5: Determine dataset split
    # --------------------------------------------------

    split = get_split(
        index,
        total_images
    )

    directories = create_directories(script)

    output_directory = directories[split]

    # Output filenames
    image_name = f"{script}_{index:04d}.png"
    md_name = f"{script}_{index:04d}.md"

    image_output = output_directory / image_name
    md_output = output_directory / md_name

    # --------------------------------------------------
    # STEP 6: Save image
    # --------------------------------------------------

    shutil.copy2(
        final_file,
        image_output
    )

    # --------------------------------------------------
    # STEP 7: Save ground-truth transcription
    # --------------------------------------------------

    md_output.write_text(
        passage,
        encoding="utf-8"
    )

    # --------------------------------------------------
    # STEP 8: Remove temporary files
    # --------------------------------------------------

    for file in [
        background_file,
        rendered_file,
        deformed_file,
        final_file
    ]:

        if file.exists():
            file.unlink()

    print(
        f"✓ {script} "
        f"{index + 1}/{total_images} "
        f"→ {split}"
    )


def generate_script(
    script,
    number_of_images=100,
    seed=42
):
    """Generate dataset for one script."""

    if script not in SCRIPT_CONFIG:
        raise ValueError(
            f"Unsupported script: {script}"
        )

    print("\n" + "=" * 60)
    print(f"GENERATING: {script.upper()}")
    print(f"SAMPLES: {number_of_images}")
    print("=" * 60)

    for index in range(number_of_images):

        generate_single_sample(
            script=script,
            index=index,
            total_images=number_of_images,
            seed=seed + index
        )

    print(
        f"\n✓ Finished {script}"
    )


def generate_all_scripts(
    number_of_images=100,
    seed=42
):
    """Generate datasets for all supported scripts."""

    print("\n" + "=" * 60)
    print("SYNTHETIC MANUSCRIPT DATASET")
    print("=" * 60)

    print(
        f"Total samples: "
        f"{number_of_images * 3}"
    )

    print(
        "Scripts: "
        "Devanagari, Modi, Sharada"
    )

    print(
        "Split: 85% / 10% / 5%"
    )

    print("=" * 60)

    # Different seed ranges create different samples
    generate_script(
        "devanagari",
        number_of_images,
        seed
    )

    generate_script(
        "modi",
        number_of_images,
        seed + 100
    )

    generate_script(
        "sharada",
        number_of_images,
        seed + 200
    )

    print("\n" + "=" * 60)
    print("✓ ALL SCRIPTS GENERATED")
    print("=" * 60)

    print(
        f"Devanagari : {number_of_images}"
    )

    print(
        f"Modi       : {number_of_images}"
    )

    print(
        f"Sharada    : {number_of_images}"
    )

    print(
        f"TOTAL      : {number_of_images * 3}"
    )

    print("=" * 60)