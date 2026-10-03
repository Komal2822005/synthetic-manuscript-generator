import random

from PIL import Image, ImageFilter


def apply_ink_variation(text_layer, rng):
    """
    Apply subtle variation to ink opacity.
    """

    alpha = text_layer.getchannel("A")

    opacity = rng.uniform(0.80, 1.00)

    alpha = alpha.point(
        lambda value: int(value * opacity)
    )

    text_layer.putalpha(alpha)

    return text_layer


def apply_ink_bleeding(text_layer, rng):
    """
    Create a subtle blurred halo around ink,
    simulating ink absorption into paper.
    """

    if rng.random() > 0.35:
        return text_layer

    blurred = text_layer.filter(
        ImageFilter.GaussianBlur(
            radius=rng.uniform(0.3, 0.8)
        )
    )

    alpha = blurred.getchannel("A")

    alpha = alpha.point(
        lambda value: int(value * rng.uniform(0.12, 0.25))
    )

    blurred.putalpha(alpha)

    result = Image.new(
        "RGBA",
        text_layer.size,
        (0, 0, 0, 0)
    )

    result.alpha_composite(blurred)
    result.alpha_composite(text_layer)

    return result


def apply_fading(text_layer, rng):
    """
    Occasionally make ink lighter,
    simulating old or faded writing.
    """

    if rng.random() > 0.20:
        return text_layer

    alpha = text_layer.getchannel("A")

    fade_factor = rng.uniform(0.60, 0.85)

    alpha = alpha.point(
        lambda value: int(value * fade_factor)
    )

    text_layer.putalpha(alpha)

    return text_layer


def apply_smudge(text_layer, rng):
    """
    Apply a very subtle smudge to selected text.
    """

    if rng.random() > 0.10:
        return text_layer

    smudge = text_layer.filter(
        ImageFilter.GaussianBlur(
            radius=rng.uniform(0.6, 1.0)
        )
    )

    alpha = smudge.getchannel("A")

    alpha = alpha.point(
        lambda value: int(value * 0.30)
    )

    smudge.putalpha(alpha)

    result = Image.new(
        "RGBA",
        text_layer.size,
        (0, 0, 0, 0)
    )

    result.alpha_composite(smudge)
    result.alpha_composite(text_layer)

    return result


def apply_text_effects(text_layer, rng):
    """
    Apply the complete manuscript ink-effect pipeline.
    """

    text_layer = apply_ink_variation(
        text_layer,
        rng
    )

    text_layer = apply_ink_bleeding(
        text_layer,
        rng
    )

    text_layer = apply_fading(
        text_layer,
        rng
    )

    text_layer = apply_smudge(
        text_layer,
        rng
    )

    return text_layer