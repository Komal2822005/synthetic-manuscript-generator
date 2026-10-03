from PIL import Image, ImageDraw


def draw_margin_markers(
    image,
    margin=130,
    color=(75, 48, 25)
):
    """
    Keep the manuscript page clean by removing
    the left and right arrow-like marginal markers.

    The red vertical manuscript margin is generated
    separately in background.py.
    """

    return image


def draw_section_marker(
    image,
    y,
    margin=130,
    color=(65, 42, 24)
):
    """
    Draw a subtle horizontal manuscript section marker.
    """

    draw = ImageDraw.Draw(image)

    width, _ = image.size

    center_x = width // 2

    marker_width = 100

    # Left horizontal section line
    draw.line(
        [
            (
                center_x - marker_width,
                y
            ),
            (
                center_x - 20,
                y
            )
        ],
        fill=color,
        width=2
    )

    # Right horizontal section line
    draw.line(
        [
            (
                center_x + 20,
                y
            ),
            (
                center_x + marker_width,
                y
            )
        ],
        fill=color,
        width=2
    )

    # Small central symbol
    draw.ellipse(
        [
            center_x - 7,
            y - 7,
            center_x + 7,
            y + 7
        ],
        outline=color,
        width=2
    )

    return image


def highlight_text_region(
    image,
    x,
    y,
    width,
    height,
    opacity=35
):
    """
    Add a subtle faded highlight behind a text region.

    The highlight does not alter the transcription.
    """

    overlay = Image.new(
        "RGBA",
        image.size,
        (0, 0, 0, 0)
    )

    draw = ImageDraw.Draw(
        overlay
    )

    draw.rounded_rectangle(
        [
            x,
            y,
            x + width,
            y + height
        ],
        radius=5,
        fill=(
            180,
            140,
            60,
            opacity
        )
    )

    return Image.alpha_composite(
        image.convert("RGBA"),
        overlay
    ).convert("RGB")


def apply_layout_variation(
    image,
    seed=42,
    margin=130
):
    """
    Apply manuscript layout elements.

    Includes:
    - No left/right arrow-like marginal markers
    - Subtle section marker
    - Subtle highlighted text region

    Returns:
        Modified PIL Image
    """

    import random

    rng = random.Random(
        seed
    )

    # ------------------------------------------------
    # MARGINAL MARKERS
    # ------------------------------------------------

    # Intentionally disabled.
    # This removes the < and > arrow-like symbols.

    image = draw_margin_markers(
        image,
        margin=margin
    )

    # ------------------------------------------------
    # SECTION MARKER
    # ------------------------------------------------

    width, height = image.size

    section_y = rng.randint(
        int(height * 0.45),
        int(height * 0.60)
    )

    image = draw_section_marker(
        image,
        y=section_y,
        margin=margin
    )

    # ------------------------------------------------
    # HIGHLIGHT REGION
    # ------------------------------------------------

    highlight_x = margin

    highlight_y = rng.randint(
        int(height * 0.20),
        int(height * 0.35)
    )

    highlight_width = rng.randint(
        350,
        600
    )

    highlight_height = 45

    image = highlight_text_region(
        image,
        x=highlight_x,
        y=highlight_y,
        width=highlight_width,
        height=highlight_height,
        opacity=25
    )

    return image