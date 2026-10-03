import argparse

from src.config import validate_config
from src.generator import (
    generate_all_scripts,
    generate_script
)


def main():

    parser = argparse.ArgumentParser(
        description="Synthetic Manuscript Generator"
    )

    parser.add_argument(
        "--script",
        choices=[
            "devanagari",
            "modi",
            "sharada",
            "all"
        ],
        default="all",
        help="Script to generate. Default: all"
    )

    parser.add_argument(
        "--num-images",
        type=int,
        default=100,
        help="Number of images per script. Default: 100"
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed. Default: 42"
    )

    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("SYNTHETIC MANUSCRIPT GENERATOR")
    print("=" * 60)

    # Check configuration
    if not validate_config():

        print("\nConfiguration validation failed.")

        print(
            "Please check the files inside "
            "data/raw and data/fonts."
        )

        return

    # Validate number of images
    if args.num_images <= 0:

        raise ValueError(
            "--num-images must be greater than 0"
        )

    # Generate all scripts
    if args.script == "all":

        generate_all_scripts(
            number_of_images=args.num_images,
            seed=args.seed
        )

    # Generate one selected script
    else:

        generate_script(
            script=args.script,
            number_of_images=args.num_images,
            seed=args.seed
        )

    print("\n" + "=" * 60)
    print("GENERATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()