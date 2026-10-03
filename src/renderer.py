from pathlib import Path
import random

import numpy as np

from PIL import (
    Image,
    ImageDraw,
    ImageFont,
    ImageFilter,
)

from .effects import apply_text_effects
from .handwriting import apply_handwriting_variation

from .layout import (
    draw_margin_markers,
    draw_section_marker,
    highlight_text_region,
)


# ================================================================
# NATURAL INK VARIATION
# ================================================================

def apply_natural_ink_variation(
    text_layer,
    rng
):
    """
    Make digitally rendered manuscript text look more natural.

    The complete Indic line is kept together so that
    Devanagari / Modi / Sharada conjuncts and vowel marks
    are not broken.
    """

    rgba = np.asarray(
        text_layer.convert("RGBA"),
        dtype=np.uint8
    ).copy()

    height, width, _ = rgba.shape

    alpha = rgba[:, :, 3].astype(
        np.float32
    )

    # ------------------------------------------------------------
    # 1. LOW-FREQUENCY INK DENSITY VARIATION
    # ------------------------------------------------------------

    noise_h = max(
        8,
        height // 10
    )

    noise_w = max(
        8,
        width // 10
    )

    # random.Random does not have normal().
    # Use gauss() instead.
    low_noise = np.array(
        [
            [
                rng.gauss(
                    0,
                    1
                )
                for _ in range(noise_w)
            ]
            for _ in range(noise_h)
        ],
        dtype=np.float32
    )

    low_noise = Image.fromarray(
        np.uint8(
            np.clip(
                low_noise * 32 + 128,
                0,
                255
            )
        )
    )

    low_noise = low_noise.resize(
        (
            width,
            height
        ),
        Image.Resampling.BICUBIC
    )

    low_noise = low_noise.filter(
        ImageFilter.GaussianBlur(
            4
        )
    )

    low_noise_array = (
        np.asarray(
            low_noise,
            dtype=np.float32
        )
        - 128.0
    )

    opacity_factor = (
        1.0
        +
        (
            low_noise_array
            /
            128.0
        )
        *
        0.13
    )

    alpha *= opacity_factor

    # ------------------------------------------------------------
    # 2. VERTICAL INK PRESSURE VARIATION
    # ------------------------------------------------------------

    vertical_noise = np.array(
        [
            rng.gauss(
                0,
                1.0
            )
            for _ in range(height)
        ],
        dtype=np.float32
    )

    vertical_noise = np.cumsum(
        vertical_noise
    )

    max_value = np.max(
        np.abs(
            vertical_noise
        )
    )

    if max_value > 0:

        vertical_noise /= max_value

    vertical_factor = (
        1.0
        +
        vertical_noise[:, None]
        *
        0.035
    )

    alpha *= vertical_factor

    alpha = np.clip(
        alpha,
        0,
        255
    )

    rgba[:, :, 3] = (
        alpha.astype(
            np.uint8
        )
    )

    # ------------------------------------------------------------
    # 3. VERY SLIGHT INK SOFTNESS
    # ------------------------------------------------------------

    softened = Image.fromarray(
        rgba,
        mode="RGBA"
    )

    softened = softened.filter(
        ImageFilter.GaussianBlur(
            0.22
        )
    )

    # ------------------------------------------------------------
    # 4. SUBTLE INK FEATHERING
    # ------------------------------------------------------------

    blurred_alpha = softened.getchannel(
        "A"
    )

    blurred_alpha = blurred_alpha.filter(
        ImageFilter.GaussianBlur(
            0.65
        )
    )

    original_alpha = np.asarray(
        softened.getchannel(
            "A"
        ),
        dtype=np.float32
    )

    feather_alpha = np.asarray(
        blurred_alpha,
        dtype=np.float32
    )

    final_alpha = (
        original_alpha * 0.91
        +
        feather_alpha * 0.09
    )

    final_alpha = np.clip(
        final_alpha,
        0,
        255
    ).astype(
        np.uint8
    )

    softened.putalpha(
        Image.fromarray(
            final_alpha,
            mode="L"
        )
    )

    return softened


# ================================================================
# HANDWRITTEN LINE SHAPE VARIATION
# ================================================================

def apply_line_shape_variation(
    text_layer,
    rng
):
    """
    Add subtle natural variation to a complete text line.

    The entire Indic line remains together.
    """

    width, height = text_layer.size

    # ------------------------------------------------------------
    # 1. VERY SMALL HORIZONTAL SHEAR
    # ------------------------------------------------------------

    shear = rng.uniform(
        -0.012,
        0.012
    )

    shift = int(
        abs(shear)
        *
        height
        *
        1.5
    )

    new_width = (
        width
        +
        shift * 2
        +
        2
    )

    if shear >= 0:

        transformed = text_layer.transform(
            (
                new_width,
                height
            ),
            Image.Transform.AFFINE,
            (
                1,
                shear,
                0,
                0,
                1,
                0
            ),
            resample=Image.Resampling.BICUBIC
        )

    else:

        transformed = text_layer.transform(
            (
                new_width,
                height
            ),
            Image.Transform.AFFINE,
            (
                1,
                shear,
                -shear * height,
                0,
                1,
                0
            ),
            resample=Image.Resampling.BICUBIC
        )

    # ------------------------------------------------------------
    # 2. VERY SMALL WIDTH VARIATION
    # ------------------------------------------------------------

    scale_x = rng.uniform(
        0.988,
        1.012
    )

    scaled_width = max(
        1,
        int(
            transformed.width
            *
            scale_x
        )
    )

    transformed = transformed.resize(
        (
            scaled_width,
            transformed.height
        ),
        Image.Resampling.BICUBIC
    )

    return transformed


# ================================================================
# MAIN TEXT RENDERER
# ================================================================

def render_text(
    text,
    font_path,
    background_path,
    output_path,
    image_width=1600,
    image_height=1000,
    font_size=45,
    margin=130,
    right_margin=270,
    line_spacing=25,
    seed=42,
):
    """
    Render manuscript text on aged paper.

    Features:
    - natural dark manuscript ink
    - slight handwritten variation
    - subtle line rotation
    - slight line-position variation
    - ink absorption
    - ink density variation
    - 3 red highlighted words
    - 2 brown highlighted words
    - Indic-script-safe rendering
    """

    rng = random.Random(
        seed
    )

    # ============================================================
    # 1. VALIDATE PATHS
    # ============================================================

    background_path = Path(
        background_path
    )

    font_path = Path(
        font_path
    )

    output_path = Path(
        output_path
    )

    if not background_path.exists():

        raise FileNotFoundError(
            f"Background file not found:\n"
            f"{background_path}"
        )

    if not font_path.exists():

        raise FileNotFoundError(
            f"Font file not found:\n"
            f"{font_path}"
        )

    # ============================================================
    # 2. LOAD BACKGROUND
    # ============================================================

    image = Image.open(
        background_path
    ).convert(
        "RGB"
    )

    image = image.resize(
        (
            image_width,
            image_height
        ),
        Image.Resampling.LANCZOS
    )

    # ============================================================
    # 3. LOAD FONT
    # ============================================================

    font = ImageFont.truetype(
        str(font_path),
        font_size
    )

    # ============================================================
    # 4. MANUSCRIPT LAYOUT ELEMENTS
    # ============================================================

    image = draw_margin_markers(
        image,
        margin=margin
    )

    section_y = rng.randint(
        int(
            image_height * 0.70
        ),
        int(
            image_height * 0.80
        )
    )

    image = draw_section_marker(
        image,
        y=section_y,
        margin=margin
    )

    highlight_y = rng.randint(
        int(
            image_height * 0.20
        ),
        int(
            image_height * 0.35
        )
    )

    image = highlight_text_region(
        image,
        x=margin,
        y=highlight_y,
        width=rng.randint(
            400,
            650
        ),
        height=48,
        opacity=20
    )

    # ============================================================
    # 5. WRITING AREA
    # ============================================================

    x_start = margin

    y = margin

    max_width = (
        image_width
        -
        margin
        -
        right_margin
    )

    max_height = (
        image_height
        -
        margin
    )

    # ============================================================
    # 6. WRAP MANUSCRIPT TEXT
    # ============================================================

    words = text.split()

    lines = []

    current_line = ""

    for word in words:

        test_line = (
            current_line
            +
            " "
            +
            word
        ).strip()

        bbox = font.getbbox(
            test_line
        )

        line_width = (
            bbox[2]
            -
            bbox[0]
        )

        if line_width <= max_width:

            current_line = test_line

        else:

            if current_line:

                lines.append(
                    current_line
                )

            current_line = word

    if current_line:

        lines.append(
            current_line
        )

    # ============================================================
    # 7. COUNT WORDS
    # ============================================================

    valid_word_count = 0

    for line in lines:

        for word in line.split():

            clean_word = word.strip(
                "।॥,;:!?()[]{}\"'"
                "“”‘’"
            )

            if clean_word:

                valid_word_count += 1

    # ============================================================
    # 8. SELECT HIGHLIGHT WORDS
    # ============================================================

    highlight_count = min(
        5,
        valid_word_count
    )

    highlight_indices = set()

    if valid_word_count > 0:

        highlight_indices = set(
            rng.sample(
                range(
                    valid_word_count
                ),
                highlight_count
            )
        )

    # ============================================================
    # 9. HIGHLIGHT COLORS
    # ============================================================

    highlight_colors = [
        (170, 55, 40),
        (170, 55, 40),
        (170, 55, 40),
        (125, 75, 40),
        (125, 75, 40),
    ]

    rng.shuffle(
        highlight_colors
    )

    highlight_color_map = {}

    selected_indices = list(
        highlight_indices
    )

    rng.shuffle(
        selected_indices
    )

    for index, word_index in enumerate(
        selected_indices
    ):

        highlight_color_map[
            word_index
        ] = highlight_colors[
            index
        ]

    # ============================================================
    # 10. RENDER EACH LINE
    # ============================================================

    page_word_index = 0

    for line_number, line in enumerate(
        lines
    ):

        if y > max_height:

            break

        # --------------------------------------------------------
        # Natural line position variation
        # --------------------------------------------------------

        x_jitter = rng.randint(
            -5,
            5
        )

        y_jitter = rng.randint(
            -3,
            3
        )

        # --------------------------------------------------------
        # Slight line rotation
        # --------------------------------------------------------

        rotation = rng.uniform(
            -1.15,
            1.15
        )

        # --------------------------------------------------------
        # Slight line width variation
        # --------------------------------------------------------

        line_scale = rng.uniform(
            0.985,
            1.015
        )

        # --------------------------------------------------------
        # Natural ink color
        # --------------------------------------------------------

        ink_base = rng.randint(
            34,
            43
        )

        ink_color = (
            ink_base + 2,
            ink_base - 3,
            max(
                0,
                ink_base - 10
            )
        )

        # ========================================================
        # LINE DIMENSIONS
        # ========================================================

        bbox = font.getbbox(
            line
        )

        text_width = (
            bbox[2]
            -
            bbox[0]
        )

        text_height = (
            bbox[3]
            -
            bbox[1]
        )

        padding = 45

        layer_width = (
            text_width
            +
            padding * 2
        )

        layer_height = (
            text_height
            +
            padding * 2
        )

        # ========================================================
        # CREATE LINE LAYER
        # ========================================================

        text_layer = Image.new(
            "RGBA",
            (
                layer_width,
                layer_height
            ),
            (
                0,
                0,
                0,
                0
            )
        )

        layer_draw = ImageDraw.Draw(
            text_layer
        )

        # ========================================================
        # DRAW COMPLETE LINE
        # ========================================================

        alpha = rng.randint(
            220,
            250
        )

        text_position = (
            padding - bbox[0],
            padding - bbox[1]
        )

        layer_draw.text(
            text_position,
            line,
            font=font,
            fill=(
                ink_color[0],
                ink_color[1],
                ink_color[2],
                alpha
            )
        )

        # ========================================================
        # DRAW HIGHLIGHT WORDS
        # ========================================================

        words_in_line = line.split()

        current_word_x = (
            padding
            -
            bbox[0]
        )

        for word in words_in_line:

            clean_word = word.strip(
                "।॥,;:!?()[]{}\"'"
                "“”‘’"
            )

            if clean_word:

                if (
                    page_word_index
                    in highlight_indices
                ):

                    highlight_color = (
                        highlight_color_map[
                            page_word_index
                        ]
                    )

                    layer_draw.text(
                        (
                            current_word_x,
                            padding - bbox[1]
                        ),
                        word,
                        font=font,
                        fill=(
                            highlight_color[0],
                            highlight_color[1],
                            highlight_color[2],
                            245
                        )
                    )

                page_word_index += 1

            current_word_x += (
                font.getlength(
                    word
                )
                +
                font.getlength(
                    " "
                )
            )

        # ========================================================
        # APPLY EXISTING HANDWRITING VARIATION
        # ========================================================

        text_layer = apply_handwriting_variation(
            text_layer,
            rng
        )

        # ========================================================
        # ADDITIONAL NATURAL LINE SHAPE
        # ========================================================

        text_layer = apply_line_shape_variation(
            text_layer,
            rng
        )

        # ========================================================
        # APPLY EXISTING TEXT EFFECTS
        # ========================================================

        text_layer = apply_text_effects(
            text_layer,
            rng
        )

        # ========================================================
        # APPLY NATURAL INK ABSORPTION
        # ========================================================

        text_layer = apply_natural_ink_variation(
            text_layer,
            rng
        )

        # ========================================================
        # SMALL SIZE VARIATION
        # ========================================================

        scaled_width = max(
            1,
            int(
                text_layer.width
                *
                line_scale
            )
        )

        text_layer = text_layer.resize(
            (
                scaled_width,
                text_layer.height
            ),
            Image.Resampling.BICUBIC
        )

        # ========================================================
        # ROTATE LINE
        # ========================================================

        text_layer = text_layer.rotate(
            rotation,
            resample=Image.Resampling.BICUBIC,
            expand=True
        )

        # ========================================================
        # CALCULATE POSITION
        # ========================================================

        paste_x = (
            x_start
            +
            x_jitter
        )

        paste_y = (
            y
            +
            y_jitter
        )

        if line_number % 2 == 0:

            paste_x += rng.randint(
                -2,
                2
            )

        else:

            paste_x += rng.randint(
                -4,
                4
            )

        # --------------------------------------------------------
        # LEFT BOUNDARY
        # --------------------------------------------------------

        if paste_x < margin:

            paste_x = margin

        # --------------------------------------------------------
        # RIGHT BOUNDARY
        # --------------------------------------------------------

        right_boundary = (
            image_width
            -
            right_margin
        )

        if (
            paste_x
            +
            text_layer.width
            >
            right_boundary
        ):

            paste_x = (
                right_boundary
                -
                text_layer.width
            )

        if paste_x < margin:

            paste_x = margin

        # --------------------------------------------------------
        # TOP BOUNDARY
        # --------------------------------------------------------

        if paste_y < margin:

            paste_y = margin

        # --------------------------------------------------------
        # BOTTOM BOUNDARY
        # --------------------------------------------------------

        if (
            paste_y
            +
            text_layer.height
            >
            image_height
            -
            margin
        ):

            break

        # ========================================================
        # PASTE LINE ON PAGE
        # ========================================================

        image.paste(
            text_layer,
            (
                int(paste_x),
                int(paste_y)
            ),
            text_layer
        )

        # ========================================================
        # NATURAL LINE SPACING
        # ========================================================

        spacing_variation = rng.randint(
            -3,
            5
        )

        y += (
            font_size
            +
            line_spacing
            +
            spacing_variation
        )

    # ============================================================
    # 11. SAVE
    # ============================================================

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    image.save(
        output_path
    )

    print(
        f"✓ Rendered manuscript: "
        f"{output_path.name}"
    )


# ================================================================
# DIRECT TEST
# ================================================================

if __name__ == "__main__":

    print(
        "Testing manuscript renderer..."
    )

    project_root = (
        Path(__file__).resolve().parent.parent
    )

    background_path = (
        project_root
        /
        "paper_background_test.png"
    )

    font_path = (
        project_root
        /
        "fonts"
        /
        "devanagari.ttf"
    )

    output_path = (
        project_root
        /
        "renderer_test.png"
    )

    sample_text = (
        "लक्षणा अपूर्व असे परियेसा । "
        "ऋषि म्हणे रायासी प्रमुखविध "
        "पुसती एकोनी दुख पावसी कल्पोपरी सांगावे । "
        "राव विनती तये केली निरोपाचे सकळी उपाय करिसी "
        "तात्काळी दुखावळा तुचि करिसी । "
        "एकोनिया ऋषीश्वर सांगता झाला विस्तार ।"
    )

    render_text(
        text=sample_text,
        font_path=font_path,
        background_path=background_path,
        output_path=output_path,
        image_width=1600,
        image_height=1000,
        font_size=45,
        margin=130,
        right_margin=270,
        line_spacing=25,
        seed=42
    )

    print(
        "Renderer test successful."
    )

    print(
        "Saved:",
        output_path
    )