from pathlib import Path


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ============================================================
# DIRECTORIES
# ============================================================

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

FONT_DIR = PROJECT_ROOT / "data" / "fonts"

OUTPUT_DIR = PROJECT_ROOT / "output"


# ============================================================
# IMAGE SETTINGS
# ============================================================

IMAGE_WIDTH = 1600

IMAGE_HEIGHT = 1000

FONT_SIZE = 45

MARGIN = 130

LINE_SPACING = 25


# ============================================================
# DATASET SETTINGS
# ============================================================

IMAGES_PER_SCRIPT = 100

TRAIN_RATIO = 0.85

VALIDATION_RATIO = 0.10

TEST_RATIO = 0.05


# ============================================================
# SCRIPT CONFIGURATION
# ============================================================

SCRIPT_CONFIG = {

    "devanagari": {

        "text_file": (
            RAW_DATA_DIR / "devanagari.md"
        ),

        "font_file": (
            FONT_DIR / "devanagari.ttf"
        ),
    },

    "modi": {

        "text_file": (
            RAW_DATA_DIR / "Modi.md"
        ),

        "font_file": (
            FONT_DIR / "Modi.ttf"
        ),
    },

    "sharada": {

        "text_file": (
            RAW_DATA_DIR / "sharada.md"
        ),

        "font_file": (
            FONT_DIR / "Sharada.ttf"
        ),
    },
}


# ============================================================
# VALIDATE CONFIGURATION
# ============================================================

def validate_config():

    print(
        "\nChecking project configuration..."
    )

    print(
        "===================================="
    )

    all_valid = True

    for script, config in SCRIPT_CONFIG.items():

        text_file = config["text_file"]

        font_file = config["font_file"]

        # ----------------------------------------------------
        # TEXT FILE
        # ----------------------------------------------------

        if text_file.exists():

            print(
                f"✓ {script} text: {text_file.name}"
            )

        else:

            print(
                f"✗ {script} text NOT FOUND:"
            )

            print(
                f"  {text_file}"
            )

            all_valid = False

        # ----------------------------------------------------
        # FONT FILE
        # ----------------------------------------------------

        if font_file.exists():

            print(
                f"✓ {script} font: {font_file.name}"
            )

        else:

            print(
                f"✗ {script} font NOT FOUND:"
            )

            print(
                f"  {font_file}"
            )

            all_valid = False

    print(
        "===================================="
    )

    if all_valid:

        print(
            "✓ All configured files found."
        )

    else:

        print(
            "✗ Some configured files are missing."
        )

    return all_valid


# ============================================================
# TEST CONFIGURATION
# ============================================================

if __name__ == "__main__":

    validate_config()