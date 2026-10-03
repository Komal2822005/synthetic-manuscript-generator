from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


# ================================================================
# SYNTHETIC MANUSCRIPT BACKGROUND
# ================================================================
#
# FINAL STYLE
#
# 1. Old aged / yellow-brown manuscript paper
# 2. Natural paper grain
# 3. Darkened old edges
# 4. Irregular dried-water stains
# 5. Water-ring boundaries mainly around edges/corners
# 6. No rectangular page border
# 7. No small repeated circles
# 8. No long geometric curves across the page
# 9. Central text area remains comparatively clean
# 10. Red manuscript margin retained
#
# Compatible with generate.py
# ================================================================


# ================================================================
# 1. SMOOTH ORGANIC NOISE
# ================================================================

def smooth_noise(
    height,
    width,
    rng,
    grid_size=40,
    blur=10
):
    """
    Creates smooth random organic noise.

    Used for:
        - paper texture
        - old-paper discoloration
        - water-stain irregularity
    """

    small_h = max(
        4,
        int(height / grid_size)
    )

    small_w = max(
        4,
        int(width / grid_size)
    )

    noise = rng.normal(
        0,
        1,
        (
            small_h,
            small_w
        )
    )

    noise -= noise.min()

    maximum = noise.max()

    if maximum > 0:
        noise /= maximum

    noise *= 255.0

    noise_image = Image.fromarray(
        noise.astype(np.uint8),
        mode="L"
    )

    noise_image = noise_image.resize(
        (
            width,
            height
        ),
        Image.Resampling.BICUBIC
    )

    if blur > 0:
        noise_image = noise_image.filter(
            ImageFilter.GaussianBlur(
                blur
            )
        )

    result = np.asarray(
        noise_image,
        dtype=np.float32
    )

    result -= result.mean()

    maximum = np.max(
        np.abs(result)
    )

    if maximum > 0:
        result /= maximum

    return result


# ================================================================
# 2. CREATE IRREGULAR WATER SHAPE
# ================================================================

def create_irregular_ring(
    cx,
    cy,
    rx,
    ry,
    rng,
    points=900
):
    """
    Creates a large imperfect organic water-stain boundary.

    This is intentionally NOT a perfect ellipse.
    """

    theta = np.linspace(
        0,
        2 * np.pi,
        points,
        endpoint=False,
        dtype=np.float32
    )

    # ------------------------------------------------------------
    # Large natural waves
    # ------------------------------------------------------------

    phase1 = rng.uniform(
        0,
        2 * np.pi
    )

    phase2 = rng.uniform(
        0,
        2 * np.pi
    )

    phase3 = rng.uniform(
        0,
        2 * np.pi
    )

    wave1 = (
        np.sin(
            theta * 2.0
            +
            phase1
        )
        *
        rng.uniform(
            0.035,
            0.070
        )
    )

    wave2 = (
        np.sin(
            theta * 4.0
            +
            phase2
        )
        *
        rng.uniform(
            0.015,
            0.035
        )
    )

    wave3 = (
        np.sin(
            theta * 7.0
            +
            phase3
        )
        *
        rng.uniform(
            0.008,
            0.020
        )
    )

    # ------------------------------------------------------------
    # Smooth random deformation
    # ------------------------------------------------------------

    random_values = rng.normal(
        0,
        1,
        points
    ).astype(
        np.float32
    )

    window = 81

    kernel = (
        np.ones(
            window,
            dtype=np.float32
        )
        /
        float(window)
    )

    padded = np.pad(
        random_values,
        (
            window // 2,
            window // 2
        ),
        mode="wrap"
    )

    random_values = np.convolve(
        padded,
        kernel,
        mode="valid"
    )

    random_values -= random_values.mean()

    maximum = np.max(
        np.abs(
            random_values
        )
    )

    if maximum > 0:
        random_values /= maximum

    random_values *= rng.uniform(
        0.015,
        0.035
    )

    deformation = (
        1.0
        +
        wave1
        +
        wave2
        +
        wave3
        +
        random_values
    )

    # ------------------------------------------------------------
    # Final coordinates
    # ------------------------------------------------------------

    x = (
        cx
        +
        np.cos(theta)
        *
        rx
        *
        deformation
    )

    y = (
        cy
        +
        np.sin(theta)
        *
        ry
        *
        deformation
    )

    return (
        np.asarray(
            x,
            dtype=np.float32
        ).reshape(-1),

        np.asarray(
            y,
            dtype=np.float32
        ).reshape(-1)
    )


# ================================================================
# 3. CONVERT NUMPY COORDINATES TO PIL POINTS
# ================================================================

def ring_points_to_pil(
    x,
    y
):
    """
    Converts NumPy coordinates safely to PIL integer points.
    """

    return [
        (
            int(
                round(
                    float(px)
                )
            ),
            int(
                round(
                    float(py)
                )
            )
        )
        for px, py in zip(
            x.tolist(),
            y.tolist()
        )
    ]


# ================================================================
# 4. DRAW IRREGULAR WATER BOUNDARY
# ================================================================

def draw_ring_layer(
    width,
    height,
    points,
    line_width,
    blur=0
):
    """
    Draws one irregular water boundary.

    Anything outside the image is automatically clipped.
    """

    layer = Image.new(
        "L",
        (
            width,
            height
        ),
        0
    )

    draw = ImageDraw.Draw(
        layer
    )

    if len(points) < 3:
        return layer

    draw.line(
        points +
        [points[0]],
        fill=255,
        width=max(
            1,
            int(line_width)
        ),
        joint="curve"
    )

    if blur > 0:

        layer = layer.filter(
            ImageFilter.GaussianBlur(
                blur
            )
        )

    return layer


# ================================================================
# 5. MAIN BACKGROUND GENERATOR
# ================================================================

def generate_paper_background(
    width=1600,
    height=1000,
    output_path="paper_background_test.png",
    seed=None
):

    rng = np.random.default_rng(
        seed
    )

    # ============================================================
    # OLD AGED PAPER BASE
    # ============================================================
    #
    # Keep this darker/yellower to retain the old manuscript look.
    # ============================================================

    base_color = np.array(
        [
            204,
            177,
            130
        ],
        dtype=np.float32
    )

    image = np.ones(
        (
            height,
            width,
            3
        ),
        dtype=np.float32
    ) * base_color

    # ============================================================
    # 6. FINE PAPER GRAIN
    # ============================================================

    fine_noise = rng.normal(
        0,
        3.2,
        (
            height,
            width,
            1
        )
    )

    image += fine_noise

    # ============================================================
    # 7. LARGE OLD-PAPER TEXTURE
    # ============================================================

    paper_texture = smooth_noise(
        height,
        width,
        rng,
        grid_size=28,
        blur=10
    )

    image += (
        paper_texture[:, :, None]
        *
        5.5
    )

    # ============================================================
    # 8. SECONDARY AGED CLOUD TEXTURE
    # ============================================================

    old_clouds = smooth_noise(
        height,
        width,
        rng,
        grid_size=55,
        blur=18
    )

    old_clouds_normalized = (
        old_clouds
        +
        1.0
    ) / 2.0

    image[:, :, 0] -= (
        old_clouds_normalized
        *
        4.0
    )

    image[:, :, 1] -= (
        old_clouds_normalized
        *
        7.0
    )

    image[:, :, 2] -= (
        old_clouds_normalized
        *
        10.0
    )

    # ============================================================
    # 9. PAGE COORDINATES
    # ============================================================

    yy, xx = np.mgrid[
        0:height,
        0:width
    ]

    # ============================================================
    # 10. TEXT AREA
    # ============================================================

    text_left = int(
        width * 0.09
    )

    text_top = int(
        height * 0.13
    )

    text_right = int(
        width * 0.86
    )

    text_bottom = int(
        height * 0.87
    )

    text_mask = np.zeros(
        (
            height,
            width
        ),
        dtype=np.float32
    )

    text_mask[
        text_top:text_bottom,
        text_left:text_right
    ] = 1.0

    text_mask_image = Image.fromarray(
        np.uint8(
            text_mask * 255
        ),
        mode="L"
    )

    text_mask_image = text_mask_image.filter(
        ImageFilter.GaussianBlur(
            12
        )
    )

    text_mask_array = (
        np.asarray(
            text_mask_image,
            dtype=np.float32
        )
        /
        255.0
    )

    # ============================================================
    # 11. WATER EFFECT LAYERS
    # ============================================================

    soft_stain = np.zeros(
        (
            height,
            width
        ),
        dtype=np.float32
    )

    ring_layer = np.zeros(
        (
            height,
            width
        ),
        dtype=np.float32
    )

    dark_ring_layer = np.zeros(
        (
            height,
            width
        ),
        dtype=np.float32
    )

    faint_ring_layer = np.zeros(
        (
            height,
            width
        ),
        dtype=np.float32
    )

    # ============================================================
    # 12. REFERENCE-STYLE WATER STAIN LOCATIONS
    # ============================================================
    #
    # IMPORTANT:
    #
    # These are NOT huge page-wide ellipses.
    #
    # The centers are positioned around/near the edges so only
    # irregular parts of the stain enter the manuscript page.
    #
    # This produces the reference-style:
    #
    #       ~~~~~
    #     ~~     ~~
    #    ~
    #
    # rather than:
    #
    #       ----------------
    #       page border
    #
    # ============================================================

    rings = [

        # --------------------------------------------------------
        # TOP-LEFT CORNER
        # --------------------------------------------------------

        (
            width * 0.025,
            height * 0.045,
            width * 0.145,
            height * 0.115
        ),

        # --------------------------------------------------------
        # TOP-RIGHT CORNER
        # --------------------------------------------------------

        (
            width * 0.975,
            height * 0.085,
            width * 0.155,
            height * 0.125
        ),

        # --------------------------------------------------------
        # LEFT SIDE
        # --------------------------------------------------------

        (
            width * 0.015,
            height * 0.53,
            width * 0.145,
            height * 0.18
        ),

        # --------------------------------------------------------
        # RIGHT SIDE
        # --------------------------------------------------------

        (
            width * 0.985,
            height * 0.54,
            width * 0.15,
            height * 0.20
        ),

        # --------------------------------------------------------
        # BOTTOM-LEFT CORNER
        # --------------------------------------------------------

        (
            width * 0.035,
            height * 0.965,
            width * 0.16,
            height * 0.12
        ),

        # --------------------------------------------------------
        # BOTTOM-RIGHT CORNER
        # --------------------------------------------------------

        (
            width * 0.965,
            height * 0.955,
            width * 0.16,
            height * 0.13
        )
    ]

    # ============================================================
    # 13. CREATE WATER RINGS
    # ============================================================

    for (
        cx,
        cy,
        rx,
        ry
    ) in rings:

        # Small natural random displacement.
        cx += rng.uniform(
            -8,
            8
        )

        cy += rng.uniform(
            -8,
            8
        )

        rx *= rng.uniform(
            0.90,
            1.10
        )

        ry *= rng.uniform(
            0.90,
            1.10
        )

        x, y = create_irregular_ring(
            cx,
            cy,
            rx,
            ry,
            rng,
            points=900
        )

        points = ring_points_to_pil(
            x,
            y
        )

        if len(points) < 3:
            continue

        # ========================================================
        # SOFT WATER HALO
        # ========================================================

        soft = draw_ring_layer(
            width,
            height,
            points,
            line_width=max(
                14,
                int(
                    min(
                        rx,
                        ry
                    )
                    *
                    0.10
                )
            ),
            blur=max(
                7,
                int(
                    min(
                        rx,
                        ry
                    )
                    *
                    0.055
                )
            )
        )

        soft_array = (
            np.asarray(
                soft,
                dtype=np.float32
            )
            /
            255.0
        )

        soft_stain += (
            soft_array
            *
            rng.uniform(
                12,
                20
            )
        )

        # ========================================================
        # MAIN DRIED WATER EDGE
        # ========================================================

        main_ring = draw_ring_layer(
            width,
            height,
            points,
            line_width=max(
                3,
                int(
                    min(
                        rx,
                        ry
                    )
                    *
                    0.018
                )
            ),
            blur=1.5
        )

        main_array = (
            np.asarray(
                main_ring,
                dtype=np.float32
            )
            /
            255.0
        )

        ring_layer += (
            main_array
            *
            rng.uniform(
                32,
                48
            )
        )

        # ========================================================
        # OUTER DRIED-WATER EDGE
        # ========================================================

        outer_x = (
            cx
            +
            (
                x -
                cx
            )
            *
            1.025
        )

        outer_y = (
            cy
            +
            (
                y -
                cy
            )
            *
            1.025
        )

        outer_points = ring_points_to_pil(
            outer_x,
            outer_y
        )

        outer_ring = draw_ring_layer(
            width,
            height,
            outer_points,
            line_width=max(
                2,
                int(
                    min(
                        rx,
                        ry
                    )
                    *
                    0.010
                )
            ),
            blur=1.5
        )

        outer_array = (
            np.asarray(
                outer_ring,
                dtype=np.float32
            )
            /
            255.0
        )

        dark_ring_layer += (
            outer_array
            *
            rng.uniform(
                18,
                32
            )
        )

        # ========================================================
        # INNER FAINT WATER EDGE
        # ========================================================

        inner_x = (
            cx
            +
            (
                x -
                cx
            )
            *
            0.955
        )

        inner_y = (
            cy
            +
            (
                y -
                cy
            )
            *
            0.955
        )

        inner_points = ring_points_to_pil(
            inner_x,
            inner_y
        )

        inner_ring = draw_ring_layer(
            width,
            height,
            inner_points,
            line_width=max(
                2,
                int(
                    min(
                        rx,
                        ry
                    )
                    *
                    0.009
                )
            ),
            blur=2.0
        )

        inner_array = (
            np.asarray(
                inner_ring,
                dtype=np.float32
            )
            /
            255.0
        )

        faint_ring_layer += (
            inner_array
            *
            rng.uniform(
                12,
                22
            )
        )

        # ========================================================
        # CLOUDY WATER STAIN INSIDE RING
        # ========================================================

        stain_mask = Image.new(
            "L",
            (
                width,
                height
            ),
            0
        )

        stain_draw = ImageDraw.Draw(
            stain_mask
        )

        stain_draw.polygon(
            points,
            fill=255
        )

        stain_mask = stain_mask.filter(
            ImageFilter.GaussianBlur(
                max(
                    18,
                    int(
                        min(
                            rx,
                            ry
                        )
                        *
                        0.12
                    )
                )
            )
        )

        stain_array = (
            np.asarray(
                stain_mask,
                dtype=np.float32
            )
            /
            255.0
        )

        local_noise = smooth_noise(
            height,
            width,
            rng,
            grid_size=80,
            blur=15
        )

        local_noise = (
            local_noise
            +
            1.0
        ) / 2.0

        stain_array *= (
            0.65
            +
            local_noise
            *
            0.35
        )

        soft_stain += (
            stain_array
            *
            rng.uniform(
                9,
                18
            )
        )

    # ============================================================
    # 14. BROAD CLOUDY OLD WATER DISCOLORATION
    # ============================================================
    #
    # These broad stains make the ring blend naturally into
    # the old manuscript instead of looking like a drawn circle.
    # ============================================================

    cloudy_regions = [

        # TOP LEFT
        (
            width * 0.08,
            height * 0.12,
            width * 0.20,
            height * 0.18
        ),

        # TOP RIGHT
        (
            width * 0.91,
            height * 0.17,
            width * 0.20,
            height * 0.22
        ),

        # LEFT SIDE
        (
            width * 0.04,
            height * 0.56,
            width * 0.17,
            height * 0.24
        ),

        # RIGHT SIDE
        (
            width * 0.96,
            height * 0.58,
            width * 0.17,
            height * 0.25
        ),

        # BOTTOM LEFT
        (
            width * 0.10,
            height * 0.91,
            width * 0.21,
            height * 0.17
        ),

        # BOTTOM RIGHT
        (
            width * 0.90,
            height * 0.91,
            width * 0.21,
            height * 0.18
        )
    ]

    for (
        cx,
        cy,
        rx,
        ry
    ) in cloudy_regions:

        distance = (
            (
                (xx - cx)
                /
                rx
            ) ** 2
            +
            (
                (yy - cy)
                /
                ry
            ) ** 2
        )

        cloud = np.exp(
            -distance
            *
            1.1
        )

        cloud_noise = smooth_noise(
            height,
            width,
            rng,
            grid_size=100,
            blur=18
        )

        cloud_noise = (
            cloud_noise
            +
            1.0
        ) / 2.0

        cloud *= (
            0.65
            +
            cloud_noise
            *
            0.35
        )

        soft_stain += (
            cloud
            *
            rng.uniform(
                6,
                13
            )
        )

    # ============================================================
    # 15. STRONG OLD PAPER EDGES
    # ============================================================

    distance_to_edge = np.minimum.reduce(
        [
            xx,
            width - 1 - xx,
            yy,
            height - 1 - yy
        ]
    )

    edge_width = (
        min(
            width,
            height
        )
        *
        0.16
    )

    edge_factor = np.clip(
        1.0
        -
        distance_to_edge
        /
        edge_width,
        0,
        1
    )

    edge_factor = (
        edge_factor ** 1.8
    )

    # Organic edge variation.
    edge_noise = smooth_noise(
        height,
        width,
        rng,
        grid_size=65,
        blur=14
    )

    edge_noise = (
        edge_noise
        +
        1.0
    ) / 2.0

    edge_aging = (
        edge_factor
        *
        (
            0.72
            +
            edge_noise
            *
            0.28
        )
    )

    # ============================================================
    # 16. PROTECT CENTRAL TEXT
    # ============================================================

    protection = (
        1.0
        -
        text_mask_array
        *
        0.96
    )

    soft_stain *= protection
    ring_layer *= protection
    dark_ring_layer *= protection
    faint_ring_layer *= protection

    # ============================================================
    # 17. APPLY SOFT WATER STAIN
    # ============================================================

    soft_stain = np.clip(
        soft_stain,
        0,
        60
    )

    soft_image = Image.fromarray(
        soft_stain.astype(
            np.uint8
        ),
        mode="L"
    )

    soft_image = soft_image.filter(
        ImageFilter.GaussianBlur(
            4
        )
    )

    soft_array = np.asarray(
        soft_image,
        dtype=np.float32
    )

    image[:, :, 0] -= (
        soft_array
        *
        0.08
    )

    image[:, :, 1] -= (
        soft_array
        *
        0.18
    )

    image[:, :, 2] -= (
        soft_array
        *
        0.30
    )

    # ============================================================
    # 18. APPLY OLD EDGE DARKENING
    # ============================================================

    edge_strength = (
        edge_aging
        *
        24
    )

    image[:, :, 0] -= (
        edge_strength
        *
        0.75
    )

    image[:, :, 1] -= (
        edge_strength
        *
        0.90
    )

    image[:, :, 2] -= (
        edge_strength
        *
        1.10
    )

    # ============================================================
    # 19. APPLY MAIN WATER RING
    # ============================================================

    ring_layer = np.clip(
        ring_layer,
        0,
        80
    )

    ring_image = Image.fromarray(
        ring_layer.astype(
            np.uint8
        ),
        mode="L"
    )

    ring_image = ring_image.filter(
        ImageFilter.GaussianBlur(
            0.8
        )
    )

    ring_array = np.asarray(
        ring_image,
        dtype=np.float32
    )

    image[:, :, 0] -= (
        ring_array
        *
        0.24
    )

    image[:, :, 1] -= (
        ring_array
        *
        0.40
    )

    image[:, :, 2] -= (
        ring_array
        *
        0.53
    )

    # ============================================================
    # 20. APPLY OUTER DARK WATER EDGE
    # ============================================================

    dark_ring_layer = np.clip(
        dark_ring_layer,
        0,
        55
    )

    dark_image = Image.fromarray(
        dark_ring_layer.astype(
            np.uint8
        ),
        mode="L"
    )

    dark_image = dark_image.filter(
        ImageFilter.GaussianBlur(
            0.9
        )
    )

    dark_array = np.asarray(
        dark_image,
        dtype=np.float32
    )

    image[:, :, 0] -= (
        dark_array
        *
        0.20
    )

    image[:, :, 1] -= (
        dark_array
        *
        0.34
    )

    image[:, :, 2] -= (
        dark_array
        *
        0.45
    )

    # ============================================================
    # 21. APPLY FAINT INNER WATER EDGE
    # ============================================================

    faint_ring_layer = np.clip(
        faint_ring_layer,
        0,
        45
    )

    faint_image = Image.fromarray(
        faint_ring_layer.astype(
            np.uint8
        ),
        mode="L"
    )

    faint_image = faint_image.filter(
        ImageFilter.GaussianBlur(
            1.4
        )
    )

    faint_array = np.asarray(
        faint_image,
        dtype=np.float32
    )

    image[:, :, 0] -= (
        faint_array
        *
        0.10
    )

    image[:, :, 1] -= (
        faint_array
        *
        0.18
    )

    image[:, :, 2] -= (
        faint_array
        *
        0.27
    )

    # ============================================================
    # 22. OLD BROWN PATCHES
    # ============================================================

    old_patches = smooth_noise(
        height,
        width,
        rng,
        grid_size=95,
        blur=22
    )

    old_patches = (
        old_patches
        +
        1.0
    ) / 2.0

    old_patches *= (
        0.35
        +
        edge_factor
        *
        0.65
    )

    image[:, :, 0] -= (
        old_patches
        *
        8
    )

    image[:, :, 1] -= (
        old_patches
        *
        12
    )

    image[:, :, 2] -= (
        old_patches
        *
        16
    )

    # ============================================================
    # 23. OLD PAPER SPOTS
    # ============================================================

    spots = np.zeros(
        (
            height,
            width
        ),
        dtype=np.float32
    )

    for _ in range(65):

        sx = rng.integers(
            0,
            width
        )

        sy = rng.integers(
            0,
            height
        )

        radius = rng.integers(
            4,
            28
        )

        spot = np.exp(
            -(
                (
                    xx - sx
                ) ** 2
                +
                (
                    yy - sy
                ) ** 2
            )
            /
            (
                2.0
                *
                radius
                *
                radius
            )
        )

        spots += (
            spot
            *
            rng.uniform(
                1,
                5
            )
        )

    spots = np.clip(
        spots,
        0,
        15
    )

    image[:, :, 0] -= (
        spots
        *
        0.20
    )

    image[:, :, 1] -= (
        spots
        *
        0.32
    )

    image[:, :, 2] -= (
        spots
        *
        0.44
    )

    # ============================================================
    # 24. FINAL OLD PAPER WARMTH
    # ============================================================

    image[:, :, 0] += 2
    image[:, :, 1] -= 1
    image[:, :, 2] -= 5

    # ============================================================
    # 25. FINAL CLAMP
    # ============================================================

    image = np.clip(
        image,
        0,
        255
    ).astype(
        np.uint8
    )

    result = Image.fromarray(
        image
    ).convert(
        "RGBA"
    )

    # ============================================================
    # 26. RIGHT RED MANUSCRIPT MARGIN
    # ============================================================

    margin_x = int(
        width * 0.875
    )

    margin_layer = Image.new(
        "RGBA",
        (
            width,
            height
        ),
        (
            0,
            0,
            0,
            0
        )
    )

    margin_draw = ImageDraw.Draw(
        margin_layer
    )

    # ------------------------------------------------------------
    # Shadow
    # ------------------------------------------------------------

    margin_draw.line(
        (
            margin_x - 5,
            0,
            margin_x - 5,
            height
        ),
        fill=(
            100,
            55,
            35,
            45
        ),
        width=3
    )

    # ------------------------------------------------------------
    # Main red line
    # ------------------------------------------------------------

    margin_draw.line(
        (
            margin_x,
            0,
            margin_x,
            height
        ),
        fill=(
            135,
            60,
            45,
            165
        ),
        width=2
    )

    # ------------------------------------------------------------
    # Secondary red line
    # ------------------------------------------------------------

    margin_draw.line(
        (
            margin_x + 7,
            0,
            margin_x + 7,
            height
        ),
        fill=(
            155,
            75,
            55,
            115
        ),
        width=1
    )

    # ------------------------------------------------------------
    # Faint third line
    # ------------------------------------------------------------

    margin_draw.line(
        (
            margin_x + 12,
            0,
            margin_x + 12,
            height
        ),
        fill=(
            170,
            90,
            65,
            75
        ),
        width=1
    )

    margin_layer = margin_layer.filter(
        ImageFilter.GaussianBlur(
            0.3
        )
    )

    result = Image.alpha_composite(
        result,
        margin_layer
    )

    # ============================================================
    # 27. FINAL RGB
    # ============================================================

    result = result.convert(
        "RGB"
    )

    result.save(
        output_path,
        quality=95
    )

    print(
        f"Background saved: {output_path}"
    )

    return result


# ================================================================
# DIRECT TEST
# ================================================================

if __name__ == "__main__":

    print(
        "Testing old aged manuscript background..."
    )

    project_root = (
        Path(__file__)
        .resolve()
        .parent
        .parent
    )

    output_file = (
        project_root
        /
        "paper_background_test.png"
    )

    generate_paper_background(
        width=1600,
        height=1000,
        output_path=output_file,
        seed=42
    )

    print(
        "Background test successful."
    )

    print(
        "Saved:",
        output_file
    )