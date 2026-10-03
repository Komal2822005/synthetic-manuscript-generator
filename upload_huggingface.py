from pathlib import Path
import argparse

from huggingface_hub import login, HfApi


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_ROOT / "output"


# ============================================================
# EXPECTED DATASET STRUCTURE
# ============================================================

SCRIPTS = [
    "devanagari",
    "modi",
    "sharada",
]

SPLITS = [
    "train",
    "validation",
    "test",
]


# ============================================================
# VALIDATE DATASET
# ============================================================

def validate_split(script, split):
    """
    Check that every PNG image has a corresponding MD file.
    """

    split_dir = OUTPUT_DIR / script / split

    if not split_dir.exists():
        raise FileNotFoundError(
            f"Directory not found:\n{split_dir}"
        )

    image_files = sorted(
        split_dir.glob("*.png")
    )

    md_files = sorted(
        split_dir.glob("*.md")
    )

    image_names = {
        file.stem
        for file in image_files
    }

    md_names = {
        file.stem
        for file in md_files
    }

    missing_md = image_names - md_names
    missing_images = md_names - image_names

    if missing_md:
        print(
            f"\nWARNING: Missing MD files in "
            f"{script}/{split}:"
        )

        for name in sorted(missing_md):
            print(f"  {name}.md")

    if missing_images:
        print(
            f"\nWARNING: Missing PNG files in "
            f"{script}/{split}:"
        )

        for name in sorted(missing_images):
            print(f"  {name}.png")

    if missing_md or missing_images:
        raise RuntimeError(
            f"Image/MD pairing problem found in "
            f"{script}/{split}."
        )

    print(
        f"{script}/{split}: "
        f"{len(image_files)} PNG + "
        f"{len(md_files)} MD"
    )

    return len(image_files), len(md_files)


# ============================================================
# VALIDATE COMPLETE DATASET
# ============================================================

def validate_dataset():
    """
    Validate all three scripts and all three splits.
    """

    print("\n" + "=" * 60)
    print("VALIDATING DATASET")
    print("=" * 60)

    total_images = 0
    total_md = 0

    for script in SCRIPTS:

        print(f"\n--- {script.upper()} ---")

        script_images = 0
        script_md = 0

        for split in SPLITS:

            images, md = validate_split(
                script,
                split
            )

            script_images += images
            script_md += md

        print(
            f"{script}: "
            f"{script_images} PNG, "
            f"{script_md} MD"
        )

        if script_images != 100:
            raise RuntimeError(
                f"{script} must contain exactly "
                f"100 images, but found "
                f"{script_images}."
            )

        if script_md != 100:
            raise RuntimeError(
                f"{script} must contain exactly "
                f"100 MD files, but found "
                f"{script_md}."
            )

        total_images += script_images
        total_md += script_md

    print("\n" + "-" * 60)

    print(
        f"TOTAL IMAGES : {total_images}"
    )

    print(
        f"TOTAL MD FILES: {total_md}"
    )

    if total_images != 300:
        raise RuntimeError(
            f"Expected 300 images, "
            f"found {total_images}."
        )

    if total_md != 300:
        raise RuntimeError(
            f"Expected 300 MD files, "
            f"found {total_md}."
        )

    print("\n✓ Dataset validation successful.")


# ============================================================
# UPLOAD ONE SCRIPT
# ============================================================

def upload_script(
    api,
    repo_id,
    script
):
    """
    Upload one script directory while preserving
    PNG and MD files and the train/validation/test structure.
    """

    script_dir = OUTPUT_DIR / script

    if not script_dir.exists():
        raise FileNotFoundError(
            f"Script directory not found:\n"
            f"{script_dir}"
        )

    print("\n" + "=" * 60)

    print(
        f"UPLOADING: {script}"
    )

    print("=" * 60)

    api.upload_folder(
        folder_path=str(script_dir),
        path_in_repo=script,
        repo_id=repo_id,
        repo_type="dataset",
    )

    print(
        f"✓ {script} uploaded successfully."
    )


# ============================================================
# MAIN
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Upload synthetic manuscript "
            "dataset to Hugging Face."
        )
    )

    parser.add_argument(
        "--repo-id",
        required=True,
        help=(
            "Hugging Face dataset repository. "
            "Example: "
            "Komal28022005/"
            "synthetic-manuscript-generator"
        ),
    )

    parser.add_argument(
        "--script",
        choices=[
            "devanagari",
            "modi",
            "sharada",
            "all",
        ],
        default="all",
        help=(
            "Script to upload. "
            "Default: all"
        ),
    )

    args = parser.parse_args()

    print("\n")
    print("=" * 60)
    print("SYNTHETIC MANUSCRIPT")
    print("HUGGING FACE DATASET UPLOADER")
    print("=" * 60)

    # --------------------------------------------------------
    # Validate local dataset first
    # --------------------------------------------------------

    validate_dataset()

    # --------------------------------------------------------
    # Login
    # --------------------------------------------------------

    print("\nLogging in to Hugging Face...")

    login()

    # --------------------------------------------------------
    # Create API object
    # --------------------------------------------------------

    api = HfApi()

    # --------------------------------------------------------
    # Determine scripts
    # --------------------------------------------------------

    if args.script == "all":

        scripts = [
            "devanagari",
            "modi",
            "sharada",
        ]

    else:

        scripts = [
            args.script
        ]

    # --------------------------------------------------------
    # Upload
    # --------------------------------------------------------

    for script in scripts:

        upload_script(
            api=api,
            repo_id=args.repo_id,
            script=script,
        )

    # --------------------------------------------------------
    # Complete
    # --------------------------------------------------------

    print("\n")
    print("=" * 60)
    print("✓ HUGGING FACE UPLOAD COMPLETE")
    print("=" * 60)

    print(
        f"\nDataset repository:"
    )

    print(
        f"https://huggingface.co/datasets/"
        f"{args.repo_id}"
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()