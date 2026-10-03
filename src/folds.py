from pathlib import Path
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


def add_folds(
    input_path,
    output_path,
    number_of_folds=3,
    seed=42
):
    """
    Add subtle historical folds and creases
    to a manuscript image.

    Effects:
    - diagonal creases
    - soft crease shadows
    - light highlights
    - subtle edge aging
    """

    rng = random.Random(seed)

    # ------------------------------------------------
    # LOAD IMAGE
    # ------------------------------------------------

    image = Image.open(
        str(input_path)
    ).convert("RGB")

    width, height = image.size

    # ------------------------------------------------
    # CREATE OVERLAY
    # ------------------------------------------------

    overlay = Image.new(
        "RGBA",
        (width, height),
        (0, 0, 0, 0)
    )

    draw = ImageDraw.Draw(
        overlay
    )

    # ------------------------------------------------
    # CREATE RANDOM FOLDS
    # ------------------------------------------------

    for _ in range(number_of_folds):

        # Random starting point
        start_x = rng.randint(
            0,
            width
        )

        start_y = rng.randint(
            0,
            height
        )

        # Random ending point
        end_x = rng.randint(
            0,
            width
        )

        end_y = rng.randint(
            0,
            height
        )

        # ------------------------------------------------
        # FOLD SHADOW
        # ------------------------------------------------

        shadow_color = (
            55,
            35,
            15,
            rng.randint(25, 55)
        )

        draw.line(
            [
                (start_x, start_y),
                (end_x, end_y)
            ],
            fill=shadow_color,
            width=rng.randint(3, 7)
        )

        # ------------------------------------------------
        # FOLD HIGHLIGHT
        # ------------------------------------------------

        highlight_color = (
            245,
            225,
            185,
            rng.randint(20, 45)
        )

        offset = rng.randint(
            2,
            5
        )

        draw.line(
            [
                (
                    start_x + offset,
                    start_y + offset
                ),
                (
                    end_x + offset,
                    end_y + offset
                )
            ],
            fill=highlight_color,
            width=rng.randint(1, 3)
        )

    # ------------------------------------------------
    # BLUR CREASES
    # ------------------------------------------------

    overlay = overlay.filter(
        ImageFilter.GaussianBlur(
            radius=2.0
        )
    )

    # ------------------------------------------------
    # COMBINE WITH IMAGE
    # ------------------------------------------------

    image = Image.alpha_composite(
        image.convert("RGBA"),
        overlay
    )

    # ------------------------------------------------
    # ADD SUBTLE EDGE DARKENING
    # ------------------------------------------------

    array = np.asarray(
        image.convert("RGB")
    ).astype(np.float32)

    yy, xx = np.mgrid[
        0:height,
        0:width
    ]

    distance = np.minimum.reduce(
        [
            xx,
            width - 1 - xx,
            yy,
            height - 1 - yy
        ]
    )

    edge_width = min(
        width,
        height
    ) * 0.08

    edge_factor = np.clip(
        1 - distance / edge_width,
        0,
        1
    )

    edge_factor = edge_factor ** 2

    # Keep edge effect subtle
    array -= (
        edge_factor[:, :, None] * 8
    )

    array = np.clip(
        array,
        0,
        255
    ).astype(np.uint8)

    result = Image.fromarray(
        array,
        mode="RGB"
    )

    # ------------------------------------------------
    # SAVE
    # ------------------------------------------------

    result.save(
        str(output_path)
    )

    print(
        f"Folded manuscript saved:\n"
        f"{output_path}"
    )


if __name__ == "__main__":

    project_root = (
        Path(__file__).resolve().parent.parent
    )

    input_file = (
        project_root
        / "devanagari_deformed_test.png"
    )

    output_file = (
        project_root
        / "devanagari_folded_test.png"
    )

    if not input_file.exists():

        raise FileNotFoundError(
            f"Input file not found:\n"
            f"{input_file}"
        )

    add_folds(
        input_path=input_file,
        output_path=output_file,
        number_of_folds=3,
        seed=42
    )