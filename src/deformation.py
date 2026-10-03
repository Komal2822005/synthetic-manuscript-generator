from pathlib import Path

import cv2
import numpy as np


def apply_page_deformation(
    input_path,
    output_path,
    strength=3.0,
    seed=42
):
    """
    Apply subtle physical deformation to a manuscript page.

    Simulates:
    - paper waviness
    - uneven surface
    - slight horizontal displacement
    - slight vertical displacement

    The deformation is intentionally subtle so that
    OCR readability is preserved.
    """

    rng = np.random.default_rng(seed)

    # ------------------------------------------------
    # LOAD IMAGE
    # ------------------------------------------------

    image = cv2.imread(
        str(input_path)
    )

    if image is None:
        raise FileNotFoundError(
            f"Could not load image:\n{input_path}"
        )

    height, width = image.shape[:2]

    # ------------------------------------------------
    # CREATE COORDINATE GRID
    # ------------------------------------------------

    x, y = np.meshgrid(
        np.arange(width),
        np.arange(height)
    )

    x = x.astype(np.float32)
    y = y.astype(np.float32)

    # ------------------------------------------------
    # HORIZONTAL WAVINESS
    # ------------------------------------------------

    horizontal_wave = (
        np.sin(
            y / rng.uniform(45, 80)
        )
        * rng.uniform(0.5, strength)
    )

    # ------------------------------------------------
    # VERTICAL WAVINESS
    # ------------------------------------------------

    vertical_wave = (
        np.sin(
            x / rng.uniform(70, 120)
        )
        * rng.uniform(0.5, strength)
    )

    # ------------------------------------------------
    # LOW-FREQUENCY RANDOM DISTORTION
    # ------------------------------------------------

    small_h = max(2, height // 40)
    small_w = max(2, width // 40)

    random_field_x = rng.normal(
        0,
        1,
        (small_h, small_w)
    ).astype(np.float32)

    random_field_y = rng.normal(
        0,
        1,
        (small_h, small_w)
    ).astype(np.float32)

    random_field_x = cv2.resize(
        random_field_x,
        (width, height),
        interpolation=cv2.INTER_CUBIC
    )

    random_field_y = cv2.resize(
        random_field_y,
        (width, height),
        interpolation=cv2.INTER_CUBIC
    )

    # Blur the random fields
    random_field_x = cv2.GaussianBlur(
        random_field_x,
        (0, 0),
        sigmaX=25
    )

    random_field_y = cv2.GaussianBlur(
        random_field_y,
        (0, 0),
        sigmaX=25
    )

    # ------------------------------------------------
    # COMBINE DEFORMATION
    # ------------------------------------------------

    map_x = (
        x
        + horizontal_wave
        + random_field_x * strength
    )

    map_y = (
        y
        + vertical_wave
        + random_field_y * strength
    )

    # ------------------------------------------------
    # APPLY WARP
    # ------------------------------------------------

    warped = cv2.remap(
        image,
        map_x,
        map_y,
        interpolation=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REFLECT
    )

    # ------------------------------------------------
    # SAVE
    # ------------------------------------------------

    success = cv2.imwrite(
        str(output_path),
        warped
    )

    if not success:
        raise IOError(
            f"Could not save image:\n{output_path}"
        )

    print(
        f"Deformed manuscript saved:\n"
        f"{output_path}"
    )


if __name__ == "__main__":

    project_root = (
        Path(__file__).resolve().parent.parent
    )

    input_file = (
        project_root
        / "devanagari_handwritten_test.png"
    )

    output_file = (
        project_root
        / "devanagari_deformed_test.png"
    )

    if not input_file.exists():
        raise FileNotFoundError(
            f"Input manuscript not found:\n"
            f"{input_file}"
        )

    apply_page_deformation(
        input_path=input_file,
        output_path=output_file,
        strength=3.0,
        seed=42
    )