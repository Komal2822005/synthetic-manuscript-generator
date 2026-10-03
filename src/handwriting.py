import random

import numpy as np
from PIL import Image


def apply_wavy_distortion(
    text_layer,
    rng,
    strength=2.0,
    frequency=0.035
):
    """
    Apply subtle horizontal waviness to a rendered text line.

    The complete already-shaped text line is distorted,
    so Devanagari conjuncts and vowel marks remain intact.

    Parameters
    ----------
    text_layer : PIL.Image
        RGBA text layer.

    rng : random.Random
        Random generator.

    strength : float
        Maximum pixel displacement.

    frequency : float
        Wave frequency.
    """

    width, height = text_layer.size

    source = np.asarray(
        text_layer
    ).copy()

    # ------------------------------------------------
    # CREATE OUTPUT
    # ------------------------------------------------

    result = np.zeros_like(
        source
    )

    # ------------------------------------------------
    # RANDOM PHASE
    # ------------------------------------------------

    phase = rng.uniform(
        0,
        2 * np.pi
    )

    # ------------------------------------------------
    # WAVE DISTORTION
    # ------------------------------------------------

    for y in range(height):

        displacement = (
            np.sin(
                y * frequency + phase
            )
            * strength
        )

        shift = int(
            round(displacement)
        )

        if shift == 0:
            result[y] = source[y]

        elif shift > 0:

            result[
                y,
                shift:
            ] = source[
                y,
                :width - shift
            ]

        else:

            shift_abs = abs(shift)

            result[
                y,
                :width - shift_abs
            ] = source[
                y,
                shift_abs:
            ]

    return Image.fromarray(
        result,
        mode="RGBA"
    )


def apply_baseline_variation(
    text_layer,
    rng,
    strength=1.5
):
    """
    Add extremely small vertical variation
    to the rendered text surface.
    """

    width, height = text_layer.size

    source = np.asarray(
        text_layer
    ).copy()

    result = np.zeros_like(
        source
    )

    phase = rng.uniform(
        0,
        2 * np.pi
    )

    for x in range(width):

        displacement = (
            np.sin(
                x * 0.025 + phase
            )
            * strength
        )

        shift = int(
            round(displacement)
        )

        if shift == 0:

            result[:, x] = source[:, x]

        elif shift > 0:

            result[
                shift:,
                x
            ] = source[
                :height - shift,
                x
            ]

        else:

            shift_abs = abs(shift)

            result[
                :height - shift_abs,
                x
            ] = source[
                shift_abs:,
                x
            ]

    return Image.fromarray(
        result,
        mode="RGBA"
    )


def apply_handwriting_variation(
    text_layer,
    rng
):
    """
    Apply controlled handwriting-style variation.

    The effects are intentionally subtle to preserve
    OCR readability.
    """

    text_layer = apply_wavy_distortion(
        text_layer,
        rng,
        strength=rng.uniform(
            0.8,
            2.0
        ),
        frequency=rng.uniform(
            0.025,
            0.045
        )
    )

    text_layer = apply_baseline_variation(
        text_layer,
        rng,
        strength=rng.uniform(
            0.5,
            1.3
        )
    )

    return text_layer