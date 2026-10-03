from pathlib import Path
from PIL import Image


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent

OUTPUT_DIR = PROJECT_ROOT / "output"

SCRIPTS = [
    "devanagari",
    "modi",
    "sharada"
]

EXPECTED_IMAGES_PER_SCRIPT = 100

EXPECTED_SPLITS = {
    "train": 85,
    "validation": 10,
    "test": 5
}

EXPECTED_IMAGE_SIZE = (
    1600,
    1000
)


# ============================================================
# VALIDATE ONE SPLIT
# ============================================================

def validate_split(
    script,
    split,
    expected_count
):

    folder = (
        OUTPUT_DIR
        / script
        / split
    )

    print(
        f"\nChecking {script}/{split}..."
    )

    # --------------------------------------------------------
    # CHECK FOLDER
    # --------------------------------------------------------

    if not folder.exists():

        print(
            f"✗ Folder missing: {folder}"
        )

        return False

    # --------------------------------------------------------
    # FIND FILES
    # --------------------------------------------------------

    png_files = sorted(
        folder.glob("*.png")
    )

    md_files = sorted(
        folder.glob("*.md")
    )

    # --------------------------------------------------------
    # CHECK COUNTS
    # --------------------------------------------------------

    print(
        f"  PNG files: {len(png_files)}"
    )

    print(
        f"  MD files:  {len(md_files)}"
    )

    valid = True

    if len(png_files) != expected_count:

        print(
            f"✗ Expected {expected_count} PNG files"
        )

        valid = False

    if len(md_files) != expected_count:

        print(
            f"✗ Expected {expected_count} MD files"
        )

        valid = False

    # --------------------------------------------------------
    # MATCH PNG ↔ MD
    # --------------------------------------------------------

    png_stems = {
        file.stem
        for file in png_files
    }

    md_stems = {
        file.stem
        for file in md_files
    }

    missing_md = (
        png_stems - md_stems
    )

    missing_png = (
        md_stems - png_stems
    )

    if missing_md:

        print(
            "✗ PNG files without matching MD:"
        )

        for name in sorted(missing_md):

            print(
                f"    {name}"
            )

        valid = False

    if missing_png:

        print(
            "✗ MD files without matching PNG:"
        )

        for name in sorted(missing_png):

            print(
                f"    {name}"
            )

        valid = False

    # --------------------------------------------------------
    # CHECK EACH IMAGE
    # --------------------------------------------------------

    for image_file in png_files:

        try:

            with Image.open(
                image_file
            ) as image:

                # --------------------------------------------
                # CHECK IMAGE SIZE
                # --------------------------------------------

                if image.size != EXPECTED_IMAGE_SIZE:

                    print(
                        f"✗ Wrong size: "
                        f"{image_file.name} "
                        f"{image.size}"
                    )

                    valid = False

                # --------------------------------------------
                # VERIFY IMAGE
                # --------------------------------------------

                image.verify()

        except Exception as error:

            print(
                f"✗ Corrupt image: "
                f"{image_file.name}"
            )

            print(
                f"  Error: {error}"
            )

            valid = False

    # --------------------------------------------------------
    # CHECK MD FILES
    # --------------------------------------------------------

    for md_file in md_files:

        try:

            text = md_file.read_text(
                encoding="utf-8"
            ).strip()

            if not text:

                print(
                    f"✗ Empty MD file: "
                    f"{md_file.name}"
                )

                valid = False

        except Exception as error:

            print(
                f"✗ Could not read: "
                f"{md_file.name}"
            )

            print(
                f"  Error: {error}"
            )

            valid = False

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    if valid:

        print(
            f"✓ {script}/{split} passed"
        )

    else:

        print(
            f"✗ {script}/{split} FAILED"
        )

    return valid


# ============================================================
# VALIDATE ONE SCRIPT
# ============================================================

def validate_script(script):

    print()
    print("=" * 60)
    print(
        f"VALIDATING {script.upper()}"
    )
    print("=" * 60)

    script_valid = True

    total_images = 0
    total_md = 0

    for split, expected_count in (
        EXPECTED_SPLITS.items()
    ):

        result = validate_split(
            script=script,
            split=split,
            expected_count=expected_count
        )

        if not result:

            script_valid = False

        folder = (
            OUTPUT_DIR
            / script
            / split
        )

        if folder.exists():

            total_images += len(
                list(
                    folder.glob("*.png")
                )
            )

            total_md += len(
                list(
                    folder.glob("*.md")
                )
            )

    # --------------------------------------------------------
    # TOTALS
    # --------------------------------------------------------

    print()
    print(
        f"{script} total PNG: {total_images}"
    )

    print(
        f"{script} total MD:  {total_md}"
    )

    if total_images != EXPECTED_IMAGES_PER_SCRIPT:

        print(
            f"✗ Expected "
            f"{EXPECTED_IMAGES_PER_SCRIPT} images"
        )

        script_valid = False

    if total_md != EXPECTED_IMAGES_PER_SCRIPT:

        print(
            f"✗ Expected "
            f"{EXPECTED_IMAGES_PER_SCRIPT} MD files"
        )

        script_valid = False

    if script_valid:

        print(
            f"✓ {script} PASSED"
        )

    else:

        print(
            f"✗ {script} FAILED"
        )

    return script_valid


# ============================================================
# VALIDATE COMPLETE DATASET
# ============================================================

def validate_dataset():

    print()
    print("=" * 60)
    print("SYNTHETIC MANUSCRIPT DATASET VALIDATION")
    print("=" * 60)

    dataset_valid = True

    total_images = 0
    total_md = 0

    # --------------------------------------------------------
    # VALIDATE EACH SCRIPT
    # --------------------------------------------------------

    for script in SCRIPTS:

        result = validate_script(
            script
        )

        if not result:

            dataset_valid = False

    # --------------------------------------------------------
    # CALCULATE GLOBAL TOTALS
    # --------------------------------------------------------

    for script in SCRIPTS:

        script_dir = (
            OUTPUT_DIR / script
        )

        if not script_dir.exists():

            continue

        for split in EXPECTED_SPLITS:

            folder = (
                script_dir / split
            )

            if folder.exists():

                total_images += len(
                    list(
                        folder.glob("*.png")
                    )
                )

                total_md += len(
                    list(
                        folder.glob("*.md")
                    )
                )

    # --------------------------------------------------------
    # FINAL REPORT
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("FINAL DATASET REPORT")
    print("=" * 60)

    print(
        f"Total PNG files : {total_images}"
    )

    print(
        f"Total MD files  : {total_md}"
    )

    print(
        "Expected PNG    : 300"
    )

    print(
        "Expected MD     : 300"
    )

    # --------------------------------------------------------
    # GLOBAL TOTAL CHECK
    # --------------------------------------------------------

    if total_images != 300:

        print(
            "✗ Incorrect total image count"
        )

        dataset_valid = False

    if total_md != 300:

        print(
            "✗ Incorrect total MD count"
        )

        dataset_valid = False

    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    print()
    print("=" * 60)

    if dataset_valid:

        print(
            "✓ DATASET VALIDATION PASSED"
        )

        print(
            "✓ 300 images found"
        )

        print(
            "✓ 300 transcription files found"
        )

        print(
            "✓ All PNG/MD pairs matched"
        )

        print(
            "✓ All images have correct dimensions"
        )

        print(
            "✓ No empty transcription files"
        )

        print(
            "✓ Train/validation/test splits correct"
        )

    else:

        print(
            "✗ DATASET VALIDATION FAILED"
        )

        print(
            "Review the errors above."
        )

    print("=" * 60)

    return dataset_valid


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    validate_dataset()