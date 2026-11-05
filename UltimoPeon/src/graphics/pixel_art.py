"""Módulo de generación y renderizado de gráficos Pixel Art procedurales.
Crea texturas de madera tallada, marcos de piedra con runas, piezas de ajedrez y trampas.
"""
import math
import random
import pygame
from src.config import (
    COLOR_WOOD_LIGHT,
    COLOR_WOOD_LIGHT_ALT,
    COLOR_WOOD_DARK,
    COLOR_WOOD_DARK_ALT,
    COLOR_WOOD_BARK,
    COLOR_STONE_DARK,
    COLOR_STONE_LIGHT,
    COLOR_STONE_BORDER,
    COLOR_RUNE_GLOW,
    COLOR_RUNE_DARK,
    COLOR_PIECE_WHITE,
    COLOR_PIECE_WHITE_SHADE,
    COLOR_PIECE_BLACK,
    COLOR_PIECE_BLACK_SHADE,
    COLOR_PIECE_BLACK_HIGHLIGHT,
    COLOR_PIECE_OUTLINE,
    COLOR_LAVA,
    COLOR_VINES,
    COLOR_BEAR_TRAP,
    COLOR_ACCENT,
    COLOR_RARITY_1,
    COLOR_RARITY_2,
    COLOR_RARITY_3,
)

# Caché de texturas para máximo rendimiento
_TEXTURE_CACHE: dict[str, pygame.Surface] = {}


def get_wood_tile(size: int, is_light: bool) -> pygame.Surface:
    """Genera o recupera de caché una casilla de madera tallada en pixel art."""
    cache_key = f"wood_tile_{size}_{is_light}"
    if cache_key in _TEXTURE_CACHE:
        return _TEXTURE_CACHE[cache_key]

    surf = pygame.Surface((size, size))
    base_col = COLOR_WOOD_LIGHT if is_light else COLOR_WOOD_DARK
    alt_col = COLOR_WOOD_LIGHT_ALT if is_light else COLOR_WOOD_DARK_ALT

    surf.fill(base_col)

    # Patrón de veta de madera en pixel art
    random.seed(size * 17 + (1 if is_light else 2))
    for y in range(0, size, 4):
        veta_offset = random.randint(-1, 2)
        for x in range(size):
            if (x + veta_offset) % 6 in (0, 1):
                pygame.draw.rect(surf, alt_col, (x, y, 1, 3))

    # Borde biselado tallado (efecto losa de madera)
    pygame.draw.line(surf, (255, 255, 255, 40), (0, 0), (size - 1, 0), 2)
    pygame.draw.line(surf, (255, 255, 255, 30), (0, 0), (0, size - 1), 2)
    pygame.draw.line(surf, COLOR_WOOD_BARK, (0, size - 1), (size - 1, size - 1), 2)
    pygame.draw.line(surf, COLOR_WOOD_BARK, (size - 1, 0), (size - 1, size - 1), 2)

    _TEXTURE_CACHE[cache_key] = surf
    return surf


def draw_pixel_hatching(
    surface: pygame.Surface,
    rect: pygame.Rect,
    color: tuple[int, int, int],
    spacing: int = 4,
    cross: bool = False,
) -> None:
    """Dibuja tramado de líneas diagonales en pixel art (crosshatching)."""
    prev_clip = surface.get_clip()
    surface.set_clip(rect)

    rx, ry, rw, rh = rect
    start_d = -rh
    end_d = rw + rh

    for d in range(start_d, end_d, spacing):
        x1 = rx + d
        y1 = ry
        x2 = rx + d + rh
        y2 = ry + rh
        pygame.draw.line(surface, color, (x1, y1), (x2, y2), 1)

    if cross:
        for d in range(start_d, end_d, spacing):
            x1 = rx + d + rh
            y1 = ry
            x2 = rx + d
            y2 = ry + rh
            pygame.draw.line(surface, color, (x1, y1), (x2, y2), 1)

    surface.set_clip(prev_clip)


def draw_stone_rune_border(
    surface: pygame.Surface,
    board_rect: pygame.Rect,
    thickness: int = 22,
    time_ms: int = 0,
) -> None:
    """Dibuja un marco de piedra mística con runas nórdicas talladas que brillan sutilmente."""
    outer_rect = board_rect.inflate(thickness * 2, thickness * 2)

    # Base de piedra oscura
    pygame.draw.rect(surface, COLOR_STONE_DARK, outer_rect, border_radius=6)
    pygame.draw.rect(surface, COLOR_STONE_LIGHT, outer_rect, width=thickness, border_radius=6)
    pygame.draw.rect(surface, COLOR_STONE_BORDER, outer_rect, width=2, border_radius=6)
    pygame.draw.rect(surface, COLOR_STONE_BORDER, board_rect, width=2)

    # Brillo de las runas (pulsación senoidal)
    pulse = (math.sin(time_ms / 600.0) + 1.0) * 0.5  # 0.0 a 1.0
    r_val = int(COLOR_RUNE_GLOW[0] * (0.6 + 0.4 * pulse))
    g_val = int(COLOR_RUNE_GLOW[1] * (0.6 + 0.4 * pulse))
    b_val = int(COLOR_RUNE_GLOW[2] * (0.6 + 0.4 * pulse))
    glow_col = (r_val, g_val, b_val)

    # Runas nórdicas/místicas talladas en el marco superior e inferior
    runes = [
        # Forma ᛏ (Flecha rúnica)
        [(-4, -6), (0, -10), (4, -6), (0, -10), (0, 10)],
        # Forma ᚱ (Viajero)
        [(-4, 8), (-4, -8), (2, -8), (4, -4), (-4, 0), (4, 8)],
        # Forma ᛋ (Relámpago / Sol)
        [(4, -8), (-4, -2), (4, 2), (-4, 8)],
        # Forma ᚦ (Espina)
        [(-4, -8), (-4, 8), (-4, -4), (3, 0), (-4, 4)],
        # Forma ᚠ (Fuego / Riqueza)
        [(-4, 8), (-4, -8), (-4, -4), (4, -7), (-4, 0), (3, -3)],
        # Forma ᛟ (Herencia / Castillo)
        [(0, -8), (4, -4), (0, 0), (-4, -4), (0, -8), (-4, 6), (4, 6)],
    ]

    # Distribución de runas en los 4 lados del marco
    # Superior e Inferior
    num_runes_h = max(3, board_rect.width // 70)
    for i in range(num_runes_h):
        cx = board_rect.left + (i + 0.5) * (board_rect.width / num_runes_h)
        rune_pts = runes[i % len(runes)]

        # Runa superior
        cy_top = board_rect.top - thickness // 2
        _render_etched_rune(surface, cx, cy_top, rune_pts, glow_col)

        # Runa inferior
        cy_bot = board_rect.bottom + thickness // 2
        _render_etched_rune(surface, cx, cy_bot, rune_pts, glow_col)

    # Laterales
    num_runes_v = max(2, board_rect.height // 80)
    for i in range(num_runes_v):
        cy = board_rect.top + (i + 0.5) * (board_rect.height / num_runes_v)
        rune_pts = runes[(i + 2) % len(runes)]

        cx_left = board_rect.left - thickness // 2
        _render_etched_rune(surface, cx_left, cy, rune_pts, glow_col)

        cx_right = board_rect.right + thickness // 2
        _render_etched_rune(surface, cx_right, cy, rune_pts, glow_col)


def _render_etched_rune(
    surface: pygame.Surface,
    cx: float,
    cy: float,
    pts: list[tuple[int, int]],
    glow_col: tuple[int, int, int],
) -> None:
    """Dibuja una runa con hendidura oscura y brillo mágico."""
    # Sombra de hendidura de piedra
    for i in range(len(pts) - 1):
        p1 = (int(cx + pts[i][0] + 1), int(cy + pts[i][1] + 1))
        p2 = (int(cx + pts[i + 1][0] + 1), int(cy + pts[i + 1][1] + 1))
        pygame.draw.line(surface, COLOR_RUNE_DARK, p1, p2, 2)

    # Brillo mágico de la runa
    for i in range(len(pts) - 1):
        p1 = (int(cx + pts[i][0]), int(cy + pts[i][1]))
        p2 = (int(cx + pts[i + 1][0]), int(cy + pts[i + 1][1]))
        pygame.draw.line(surface, glow_col, p1, p2, 1)


# =========================================================================
# PIEZAS EN PIXEL ART (MADERA TALLADA + CROSSHATCHING)
# =========================================================================

def draw_pixel_pawn(
    surface: pygame.Surface,
    cx: int,
    cy: int,
    size: int,
    is_white: bool = True,
    is_hovered: bool = False,
    is_immobilized: bool = False,
    has_shield: bool = False,
) -> None:
    """Dibuja un peón de madera tallada en pixel art con sombreado de líneas cruzadas y escudo opcional."""
    pawn_surf = pygame.Surface((size, size), pygame.SRCALPHA)
    pcx, pcy = size // 2, size // 2

    # Proporciones en píxeles ajustadas
    base_w = int(size * 0.54)
    base_h = int(size * 0.16)
    neck_w = int(size * 0.32)
    neck_h = int(size * 0.08)
    head_r = int(size * 0.18)

    y_base = pcy + int(size * 0.28)
    y_neck = pcy - int(size * 0.02)
    y_head = pcy - int(size * 0.20)
    y_torso_bot = y_base - base_h // 2

    torso_pts = [
        (pcx - neck_w // 2, y_neck),
        (pcx + neck_w // 2, y_neck),
        (pcx + int(base_w * 0.36), y_torso_bot),
        (pcx - int(base_w * 0.36), y_torso_bot),
    ]

    # Sombra en el suelo
    shadow_rect = pygame.Rect(0, 0, int(size * 0.58), int(size * 0.16))
    shadow_rect.center = (pcx, y_base + int(size * 0.07))
    pygame.draw.ellipse(pawn_surf, (0, 0, 0, 95), shadow_rect)

    if is_white:
        # --- PEÓN BLANCO: Madera de Haya / Roble Claro Tallada ---
        base_rect = pygame.Rect(0, 0, base_w, base_h)
        base_rect.center = (pcx, y_base)
        pygame.draw.ellipse(pawn_surf, COLOR_PIECE_WHITE, base_rect)

        pygame.draw.polygon(pawn_surf, COLOR_PIECE_WHITE, torso_pts)

        neck_rect = pygame.Rect(0, 0, neck_w, neck_h)
        neck_rect.center = (pcx, y_neck)
        pygame.draw.ellipse(pawn_surf, COLOR_PIECE_WHITE, neck_rect)

        pygame.draw.circle(pawn_surf, COLOR_PIECE_WHITE, (pcx, y_head), head_r)

        torso_shadow = pygame.Rect(pcx, y_neck, base_w // 2, y_torso_bot - y_neck)
        draw_pixel_hatching(pawn_surf, torso_shadow, COLOR_PIECE_WHITE_SHADE, spacing=3, cross=False)

        cross_rect = pygame.Rect(pcx - 8, y_neck - 2, 16, 7)
        draw_pixel_hatching(pawn_surf, cross_rect, (140, 125, 105), spacing=3, cross=True)

        base_shadow = pygame.Rect(pcx, y_base - base_h // 2, base_w // 2, base_h)
        draw_pixel_hatching(pawn_surf, base_shadow, COLOR_PIECE_WHITE_SHADE, spacing=3, cross=False)

        head_shadow = pygame.Rect(pcx, y_head, head_r, head_r)
        draw_pixel_hatching(pawn_surf, head_shadow, COLOR_PIECE_WHITE_SHADE, spacing=3, cross=False)

        pygame.draw.ellipse(pawn_surf, COLOR_PIECE_OUTLINE, base_rect, 2)
        pygame.draw.polygon(pawn_surf, COLOR_PIECE_OUTLINE, torso_pts, 2)
        pygame.draw.ellipse(pawn_surf, COLOR_PIECE_OUTLINE, neck_rect, 2)
        pygame.draw.circle(pawn_surf, COLOR_PIECE_OUTLINE, (pcx, y_head), head_r, 2)

        pygame.draw.circle(pawn_surf, COLOR_ACCENT, (pcx, y_head - 2), 3)
        pygame.draw.circle(pawn_surf, (255, 255, 255), (pcx - 3, y_head - 5), 2)

    else:
        # --- PEÓN NEGRO: Madera de Ébano Quemada / Carbón Rúnico ---
        base_rect = pygame.Rect(0, 0, base_w, base_h)
        base_rect.center = (pcx, y_base)
        pygame.draw.ellipse(pawn_surf, COLOR_PIECE_BLACK, base_rect)

        pygame.draw.polygon(pawn_surf, COLOR_PIECE_BLACK, torso_pts)

        neck_rect = pygame.Rect(0, 0, neck_w, neck_h)
        neck_rect.center = (pcx, y_neck)
        pygame.draw.ellipse(pawn_surf, COLOR_PIECE_BLACK, neck_rect)

        pygame.draw.circle(pawn_surf, COLOR_PIECE_BLACK, (pcx, y_head), head_r)

        torso_texture = pygame.Rect(pcx - neck_w // 2, y_neck + 2, neck_w, y_torso_bot - y_neck - 4)
        draw_pixel_hatching(pawn_surf, torso_texture, COLOR_PIECE_BLACK_HIGHLIGHT, spacing=4, cross=True)

        base_texture = pygame.Rect(pcx - base_w // 3, y_base - base_h // 2 + 1, (base_w * 2) // 3, base_h - 2)
        draw_pixel_hatching(pawn_surf, base_texture, COLOR_PIECE_BLACK_HIGHLIGHT, spacing=4, cross=False)

        pygame.draw.ellipse(pawn_surf, COLOR_PIECE_OUTLINE, base_rect, 2)
        pygame.draw.polygon(pawn_surf, COLOR_PIECE_OUTLINE, torso_pts, 2)
        pygame.draw.ellipse(pawn_surf, COLOR_PIECE_OUTLINE, neck_rect, 2)
        pygame.draw.circle(pawn_surf, COLOR_PIECE_OUTLINE, (pcx, y_head), head_r, 2)

        pygame.draw.ellipse(pawn_surf, (235, 45, 45), (pcx - 6, y_head - 2, 12, 4))
        pygame.draw.circle(pawn_surf, (255, 200, 200), (pcx, y_head), 2)

    # Escudo rúnico (si la pieza tiene escudo)
    if has_shield:
        sh_w = int(size * 0.32)
        sh_h = int(size * 0.44)
        sh_x = pcx - int(size * 0.32)
        sh_y = pcy - int(size * 0.12)
        shield_pts = [
            (sh_x, sh_y),
            (sh_x + sh_w, sh_y),
            (sh_x + sh_w, sh_y + int(sh_h * 0.6)),
            (sh_x + sh_w // 2, sh_y + sh_h),
            (sh_x, sh_y + int(sh_h * 0.6)),
        ]
        # Fondo y bisel de escudo de acero oscuro
        pygame.draw.polygon(pawn_surf, (30, 48, 72), shield_pts)
        pygame.draw.polygon(pawn_surf, (90, 215, 255), shield_pts, 2)
        # Runa protectora brillante
        pygame.draw.line(pawn_surf, (180, 240, 255), (sh_x + sh_w // 2, sh_y + 4), (sh_x + sh_w // 2, sh_y + sh_h - 4), 2)
        pygame.draw.line(pawn_surf, (180, 240, 255), (sh_x + 4, sh_y + int(sh_h * 0.38)), (sh_x + sh_w - 4, sh_y + int(sh_h * 0.38)), 2)
        pygame.draw.circle(pawn_surf, (255, 255, 255), (sh_x + sh_w // 2, sh_y + int(sh_h * 0.38)), 2)

    # Efecto de inmovilización (atrapado en trampa / congelado)
    if is_immobilized:
        ice_rect = pygame.Rect(pcx - base_w // 2 - 2, y_head - head_r - 2, base_w + 4, size - 10)
        pygame.draw.rect(pawn_surf, (100, 220, 255, 90), ice_rect, border_radius=6)
        pygame.draw.rect(pawn_surf, (150, 240, 255, 200), ice_rect, 2, border_radius=6)

    # Brillo de hover
    if is_hovered:
        glow_rect = pygame.Rect(pcx - base_w // 2 - 4, y_head - head_r - 4, base_w + 8, size - 8)
        pygame.draw.rect(pawn_surf, (255, 215, 60, 140), glow_rect, 2, border_radius=6)

    surface.blit(pawn_surf, (cx - pcx, cy - pcy))


def draw_pixel_knight(
    surface: pygame.Surface,
    cx: int,
    cy: int,
    size: int,
    is_ally: bool = True,
    is_hovered: bool = False,
    turns_left: int = 15,
) -> None:
    """Dibuja un Caballo aliado o enemigo de madera tallada en pixel art."""
    k_surf = pygame.Surface((size, size), pygame.SRCALPHA)
    pcx, pcy = size // 2, size // 2

    shadow_rect = pygame.Rect(0, 0, int(size * 0.62), int(size * 0.18))
    shadow_rect.center = (pcx, pcy + int(size * 0.35))
    pygame.draw.ellipse(k_surf, (0, 0, 0, 95), shadow_rect)

    col_base = (245, 235, 215) if is_ally else (42, 38, 48)
    col_shade = (185, 170, 145) if is_ally else (85, 80, 95)

    head_pts = [
        (pcx - 14, pcy + 18),
        (pcx - 14, pcy + 4),
        (pcx - 22, pcy - 4),
        (pcx - 18, pcy - 16),
        (pcx - 4, pcy - 12),
        (pcx + 2, pcy - 22),
        (pcx + 8, pcy - 14),
        (pcx + 14, pcy + 2),
        (pcx + 16, pcy + 18),
    ]

    pygame.draw.polygon(k_surf, col_base, head_pts)
    pygame.draw.polygon(k_surf, COLOR_PIECE_OUTLINE, head_pts, 2)

    crin_rect = pygame.Rect(pcx, pcy - 15, 16, 28)
    draw_pixel_hatching(k_surf, crin_rect, col_shade, spacing=3, cross=False)

    eye_col = COLOR_RUNE_GLOW if is_ally else (235, 45, 45)
    pygame.draw.circle(k_surf, eye_col, (pcx - 8, pcy - 8), 3)

    base_rect = pygame.Rect(pcx - 18, pcy + 16, 36, 10)
    pygame.draw.ellipse(k_surf, col_base, base_rect)
    pygame.draw.ellipse(k_surf, COLOR_PIECE_OUTLINE, base_rect, 2)

    if is_ally and turns_left > 0:
        font_mini = pygame.font.SysFont("arial", 11, bold=True)
        badge_surf = font_mini.render(str(turns_left), True, COLOR_ACCENT)
        k_surf.blit(badge_surf, (pcx + 10, pcy - 22))

    if is_hovered:
        pygame.draw.rect(k_surf, (100, 220, 255, 150), (pcx - 24, pcy - 24, 48, 52), 2, border_radius=6)

    surface.blit(k_surf, (cx - pcx, cy - pcy))


def draw_pixel_enemy_piece(
    surface: pygame.Surface,
    cx: int,
    cy: int,
    size: int,
    piece_role: str,
    is_hovered: bool = False,
    is_immobilized: bool = False,
    has_shield: bool = False,
    is_boss: bool = False,
) -> None:
    """Renderiza cualquier pieza enemiga en pixel art de madera de ébano tallada según su rol."""
    if piece_role == "pawn":
        draw_pixel_pawn(
            surface,
            cx,
            cy,
            size,
            is_white=False,
            is_hovered=is_hovered,
            is_immobilized=is_immobilized,
            has_shield=has_shield,
        )
        return
    elif piece_role == "knight":
        draw_pixel_knight(surface, cx, cy, size, is_ally=False, is_hovered=is_hovered, turns_left=0)
        return

    # Renderizado para Bishop, Rook, Queen y King (Jefe Final)
    scale = 1.35 if is_boss else 1.0
    render_size = int(size * scale)
    p_surf = pygame.Surface((render_size, render_size), pygame.SRCALPHA)
    pcx, pcy = render_size // 2, render_size // 2

    # Aura cósmica oscura si es el Jefe Rey Gigante
    if is_boss:
        aura_r = int(render_size * 0.44)
        aura_surf = pygame.Surface((render_size, render_size), pygame.SRCALPHA)
        pygame.draw.circle(aura_surf, (160, 40, 220, 60), (pcx, pcy), aura_r)
        pygame.draw.circle(aura_surf, (245, 185, 45, 80), (pcx, pcy), aura_r, 2)
        p_surf.blit(aura_surf, (0, 0))

    # Sombra en el suelo
    shadow_rect = pygame.Rect(0, 0, int(render_size * 0.62), int(render_size * 0.18))
    shadow_rect.center = (pcx, pcy + int(render_size * 0.35))
    pygame.draw.ellipse(p_surf, (0, 0, 0, 115), shadow_rect)

    # Base común de madera oscura
    base_w = int(render_size * 0.58)
    base_h = int(render_size * 0.16)
    base_rect = pygame.Rect(pcx - base_w // 2, pcy + int(render_size * 0.25), base_w, base_h)
    pygame.draw.ellipse(p_surf, COLOR_PIECE_BLACK, base_rect)
    pygame.draw.ellipse(p_surf, COLOR_PIECE_OUTLINE, base_rect, 2)

    if piece_role == "bishop":
        # --- ALFIL ENEMIGO (Mitra alta hendida con cruz tallada) ---
        body_pts = [
            (pcx - 14, pcy + 16), (pcx + 14, pcy + 16),
            (pcx + 10, pcy - 8), (pcx, pcy - 24), (pcx - 10, pcy - 8)
        ]
        pygame.draw.polygon(p_surf, COLOR_PIECE_BLACK, body_pts)
        draw_pixel_hatching(p_surf, pygame.Rect(pcx - 8, pcy - 12, 16, 24), COLOR_PIECE_BLACK_HIGHLIGHT, spacing=3, cross=True)
        pygame.draw.polygon(p_surf, COLOR_PIECE_OUTLINE, body_pts, 2)

        pygame.draw.line(p_surf, (220, 45, 45), (pcx, pcy - 16), (pcx, pcy - 2), 2)
        pygame.draw.line(p_surf, (220, 45, 45), (pcx - 4, pcy - 10), (pcx + 4, pcy - 10), 2)
        pygame.draw.circle(p_surf, (255, 60, 60), (pcx, pcy + 4), 3)

    elif piece_role == "rook":
        # --- TORRE ENEMIGA (Fortaleza acorazada con almenas) ---
        tower_rect = pygame.Rect(pcx - 16, pcy - 12, 32, 28)
        pygame.draw.rect(p_surf, COLOR_PIECE_BLACK, tower_rect)
        draw_pixel_hatching(p_surf, tower_rect, COLOR_PIECE_BLACK_HIGHLIGHT, spacing=4, cross=True)
        pygame.draw.rect(p_surf, COLOR_PIECE_OUTLINE, tower_rect, 2)

        for bx in [-16, -5, 6]:
            b_rect = pygame.Rect(pcx + bx, pcy - 20, 10, 8)
            pygame.draw.rect(p_surf, COLOR_PIECE_BLACK, b_rect)
            pygame.draw.rect(p_surf, COLOR_PIECE_OUTLINE, b_rect, 2)

        pygame.draw.rect(p_surf, (235, 40, 40), (pcx - 3, pcy - 4, 6, 10), border_radius=2)
        pygame.draw.circle(p_surf, (255, 200, 200), (pcx, pcy + 1), 2)

    elif piece_role == "queen":
        # --- REINA ENEMIGA (Corona regia puntiaguda con rubí central) ---
        gown_pts = [
            (pcx - 18, pcy + 18), (pcx + 18, pcy + 18),
            (pcx + 12, pcy - 6), (pcx - 12, pcy - 6)
        ]
        pygame.draw.polygon(p_surf, COLOR_PIECE_BLACK, gown_pts)
        draw_pixel_hatching(p_surf, pygame.Rect(pcx - 10, pcy - 4, 20, 20), COLOR_PIECE_BLACK_HIGHLIGHT, spacing=3, cross=True)
        pygame.draw.polygon(p_surf, COLOR_PIECE_OUTLINE, gown_pts, 2)

        crown_pts = [
            (pcx - 14, pcy - 8),
            (pcx - 14, pcy - 20),
            (pcx - 7, pcy - 13),
            (pcx, pcy - 24),
            (pcx + 7, pcy - 13),
            (pcx + 14, pcy - 20),
            (pcx + 14, pcy - 8),
        ]
        pygame.draw.polygon(p_surf, COLOR_PIECE_BLACK, crown_pts)
        pygame.draw.polygon(p_surf, (245, 185, 45), crown_pts, 2)
        pygame.draw.circle(p_surf, (255, 30, 30), (pcx, pcy - 6), 4)
        pygame.draw.circle(p_surf, (255, 210, 210), (pcx - 1, pcy - 7), 2)

    elif piece_role == "king":
        # --- REY GIGANTE / JEFE FINAL (Manto carmesí imperial, cruz monumental y corona dorada) ---
        # Manto imperial
        mantle_pts = [
            (pcx - 22, pcy + 18), (pcx + 22, pcy + 18),
            (pcx + 15, pcy - 8), (pcx - 15, pcy - 8)
        ]
        pygame.draw.polygon(p_surf, (130, 22, 32), mantle_pts)
        draw_pixel_hatching(p_surf, pygame.Rect(pcx - 14, pcy - 6, 28, 24), COLOR_PIECE_BLACK, spacing=3, cross=True)
        pygame.draw.polygon(p_surf, COLOR_PIECE_OUTLINE, mantle_pts, 2)

        # Pechera de obsidiana
        chest_rect = pygame.Rect(pcx - 10, pcy - 8, 20, 22)
        pygame.draw.rect(p_surf, COLOR_PIECE_BLACK, chest_rect)
        pygame.draw.rect(p_surf, COLOR_PIECE_OUTLINE, chest_rect, 2)

        # Corona regia cuadrada
        crown_k_rect = pygame.Rect(pcx - 14, pcy - 18, 28, 12)
        pygame.draw.rect(p_surf, COLOR_PIECE_BLACK, crown_k_rect)
        pygame.draw.rect(p_surf, COLOR_ACCENT, crown_k_rect, 2)

        # Gran Cruz Real en la cúspide (+)
        cross_y = pcy - 26
        pygame.draw.line(p_surf, COLOR_ACCENT, (pcx, cross_y - 6), (pcx, cross_y + 8), 3)
        pygame.draw.line(p_surf, COLOR_ACCENT, (pcx - 6, cross_y - 1), (pcx + 6, cross_y - 1), 3)
        pygame.draw.circle(p_surf, (255, 255, 255), (pcx, cross_y - 1), 2)

        # Ojos demoníacos carmesí del Rey
        pygame.draw.circle(p_surf, (255, 45, 45), (pcx - 5, pcy - 12), 2)
        pygame.draw.circle(p_surf, (255, 45, 45), (pcx + 5, pcy - 12), 2)

    if is_immobilized:
        ice_rect = pygame.Rect(pcx - base_w // 2, pcy - int(render_size * 0.35), base_w, int(render_size * 0.7))
        pygame.draw.rect(p_surf, (100, 220, 255, 95), ice_rect, border_radius=6)
        pygame.draw.rect(p_surf, (150, 240, 255, 210), ice_rect, 2, border_radius=6)

    if is_hovered:
        glow_rect = pygame.Rect(pcx - base_w // 2 - 3, pcy - int(render_size * 0.38), base_w + 6, int(render_size * 0.75))
        pygame.draw.rect(p_surf, (255, 215, 60, 150), glow_rect, 2, border_radius=6)

    surface.blit(p_surf, (cx - pcx, cy - pcy))


def draw_boss_health_bar(
    surface: pygame.Surface,
    current_hp: int,
    max_hp: int,
    name: str = "EL REY TIRANO • JEFE FINAL",
) -> None:
    """Renderiza la barra de vida del Rey Gigante en la parte superior con marcadores de división."""
    bar_w = 420
    bar_h = 24
    bx = (surface.get_width() - bar_w) // 2
    by = 56

    font_b = pygame.font.SysFont("georgia", 13, bold=True)
    font_num = pygame.font.SysFont("arial", 12, bold=True)

    # Marco de piedra exterior
    outer_rect = pygame.Rect(bx - 4, by - 4, bar_w + 8, bar_h + 8)
    pygame.draw.rect(surface, (20, 22, 28), outer_rect, border_radius=6)
    pygame.draw.rect(surface, (85, 90, 110), outer_rect, width=2, border_radius=6)

    # Fondo de la barra vacía
    inner_rect = pygame.Rect(bx, by, bar_w, bar_h)
    pygame.draw.rect(surface, (45, 15, 20), inner_rect, border_radius=4)

    # Relleno de vida (proporcional)
    hp_ratio = max(0.0, min(1.0, current_hp / max(1, max_hp)))
    fill_w = int(bar_w * hp_ratio)
    if fill_w > 0:
        fill_rect = pygame.Rect(bx, by, fill_w, bar_h)
        # Degradado carmesí y oro
        pygame.draw.rect(surface, (220, 35, 45), fill_rect, border_radius=4)
        top_shine = pygame.Rect(bx, by, fill_w, bar_h // 2)
        pygame.draw.rect(surface, (255, 110, 70), top_shine, border_radius=4)

    # Marcadores de fractura de tablero (a 2/3 y a 1/3 de vida)
    for frac in (1 / 3, 2 / 3):
        mark_x = bx + int(bar_w * frac)
        pygame.draw.line(surface, (245, 185, 45), (mark_x, by - 3), (mark_x, by + bar_h + 3), 2)
        # Runa divisoria
        pygame.draw.circle(surface, (255, 215, 60), (mark_x, by + bar_h // 2), 3)

    # Nombre del jefe y vida numérica
    name_surf = font_b.render(name, True, (245, 195, 60))
    surface.blit(name_surf, (bx + 8, by - 22))

    hp_text = f"{max(0, current_hp)} / {max_hp} HP"
    hp_surf = font_num.render(hp_text, True, (250, 250, 250))
    surface.blit(hp_surf, (bx + bar_w - hp_surf.get_width() - 8, by - 20))


def draw_board_fissure(
    surface: pygame.Surface,
    board,
    split_rows: list[int],
    time_ms: int = 0,
) -> None:
    """Dibuja una falla ardiente y agrietada de magma cuando el Rey divide el tablero en dos."""
    pulse = (math.sin(time_ms / 250.0) + 1.0) * 0.5
    for r in split_rows:
        if not (0 <= r < board.rows):
            continue
        y_line = board.offset_y + r * board.tile_size
        total_w = board.cols * board.tile_size

        # Fissure fissure banner across the whole row line
        fissure_surf = pygame.Surface((total_w, 12), pygame.SRCALPHA)
        fissure_surf.fill((255, 60, 20, int(150 + 80 * pulse)))
        surface.blit(fissure_surf, (board.offset_x, y_line - 6))

        # Líneas quebradas de magma ardiente
        points = []
        for c in range(board.cols + 1):
            px = board.offset_x + c * board.tile_size
            py = y_line + (random.randint(-4, 4) if (c % 2 == 1) else 0)
            points.append((px, py))
        if len(points) > 1:
            pygame.draw.lines(surface, (255, 215, 60), False, points, 3)
            pygame.draw.lines(surface, (255, 50, 20), False, points, 5)


# =========================================================================
# TRAMPAS EN PIXEL ART
# =========================================================================

def draw_trap_sprite(
    surface: pygame.Surface,
    trap_type: str,
    cx: int,
    cy: int,
    size: int,
    time_ms: int = 0,
) -> None:
    """Dibuja una trampa procedural (Trampa de oso, Enredadera o Charco de lava)."""
    t_surf = pygame.Surface((size, size), pygame.SRCALPHA)
    pcx, pcy = size // 2, size // 2

    if trap_type == "bear_trap":
        # Mandíbulas serradas de hierro con resorte
        jaw_radius = int(size * 0.32)
        pygame.draw.circle(t_surf, (80, 85, 95), (pcx, pcy), jaw_radius, 4)

        # Dientes serrados en cruz
        for angle_deg in range(0, 360, 45):
            rad = math.radians(angle_deg)
            x_out = pcx + math.cos(rad) * jaw_radius
            y_out = pcy + math.sin(rad) * jaw_radius
            x_in = pcx + math.cos(rad) * (jaw_radius - 7)
            y_in = pcy + math.sin(rad) * (jaw_radius - 7)
            pygame.draw.line(t_surf, (200, 205, 215), (int(x_out), int(y_out)), (int(x_in), int(y_in)), 2)

        # Plato de presión central (gatillo rojo peligro)
        pygame.draw.circle(t_surf, (160, 50, 50), (pcx, pcy), 5)
        pygame.draw.circle(t_surf, (220, 70, 70), (pcx, pcy), 2)

    elif trap_type == "vines":
        # Enredadera espinosa que crece sobre la casilla
        pygame.draw.ellipse(t_surf, (35, 90, 45, 180), (pcx - 22, pcy - 22, 44, 44))
        # Tallos retorcidos
        pts_stem1 = [(pcx - 24, pcy - 10), (pcx - 8, pcy + 4), (pcx + 12, pcy - 8), (pcx + 24, pcy + 14)]
        pts_stem2 = [(pcx - 18, pcy + 18), (pcx - 4, pcy - 12), (pcx + 10, pcy + 6), (pcx + 22, pcy - 16)]
        pygame.draw.lines(t_surf, COLOR_VINES, False, pts_stem1, 3)
        pygame.draw.lines(t_surf, (75, 185, 90), False, pts_stem2, 3)

        # Espinas
        for sp in [(pcx - 6, pcy + 6), (pcx + 8, pcy - 10), (pcx - 2, pcy - 14), (pcx + 14, pcy + 8)]:
            pygame.draw.circle(t_surf, (210, 50, 50), sp, 3)

    elif trap_type == "lava":
        # Charco de magma hirviente con burbujas y borde chamuscado
        pulse = (math.sin(time_ms / 300.0) + 1.0) * 0.5
        lava_r = int(size * 0.38 + pulse * 2)

        # Borde chamuscado oscuro
        pygame.draw.circle(t_surf, (50, 25, 20), (pcx, pcy), lava_r + 4)
        # Núcleo de lava naranja intenso
        pygame.draw.circle(t_surf, COLOR_LAVA, (pcx, pcy), lava_r)
        # Magma amarillo central caliente
        pygame.draw.circle(t_surf, (255, 205, 45), (pcx - 3, pcy - 2), int(lava_r * 0.55))

        # Burbujas de magma animadas
        b1_y = pcy + int(math.sin(time_ms / 200.0) * 6)
        pygame.draw.circle(t_surf, (255, 255, 120), (pcx + 8, b1_y), 4)

    surface.blit(t_surf, (cx - pcx, cy - pcy))


# =========================================================================
# ICONOS DE PODERES (PIXEL ART)
# =========================================================================

def draw_power_icon(surface: pygame.Surface, icon_id: str, cx: int, cy: int, size: int = 40) -> None:
    """Dibuja un icono pixel art temático para cada bendición / poder."""
    icon_surf = pygame.Surface((size, size), pygame.SRCALPHA)
    pcx, pcy = size // 2, size // 2

    if icon_id == "range_kill":
        # Dos dagas / espadas cruzadas de largo alcance
        pygame.draw.line(icon_surf, (255, 255, 255), (pcx - 12, pcy + 12), (pcx + 12, pcy - 12), 3)
        pygame.draw.line(icon_surf, (255, 255, 255), (pcx - 12, pcy - 12), (pcx + 12, pcy + 12), 3)
        pygame.draw.circle(icon_surf, (245, 60, 60), (pcx, pcy), 4)

    elif icon_id == "range_move":
        # Bota alada / Flechas de velocidad
        pygame.draw.polygon(icon_surf, (100, 220, 255), [
            (pcx - 12, pcy + 8), (pcx + 6, pcy + 8), (pcx + 12, pcy + 2), (pcx + 4, pcy - 10), (pcx - 10, pcy - 4)
        ])
        # Alas
        pygame.draw.line(icon_surf, (255, 255, 255), (pcx - 10, pcy - 6), (pcx - 16, pcy - 14), 2)
        pygame.draw.line(icon_surf, (255, 255, 255), (pcx - 6, pcy - 8), (pcx - 10, pcy - 16), 2)

    elif icon_id == "kill_rook":
        # Corona de almena de Torre de ajedrez
        pygame.draw.rect(icon_surf, (220, 220, 230), (pcx - 12, pcy - 10, 24, 20))
        # Almenas
        for ax in [-10, -2, 6]:
            pygame.draw.rect(icon_surf, (40, 40, 50), (pcx + ax, pcy - 10, 4, 6))

    elif icon_id == "kill_bishop":
        # Mitra diagonal de Alfil con cruz
        pygame.draw.polygon(icon_surf, (200, 160, 255), [
            (pcx, pcy - 14), (pcx + 10, pcy + 4), (pcx + 8, pcy + 12), (pcx - 8, pcy + 12), (pcx - 10, pcy + 4)
        ])
        # Cruz tallada
        pygame.draw.line(icon_surf, (255, 255, 255), (pcx, pcy - 6), (pcx, pcy + 4), 2)
        pygame.draw.line(icon_surf, (255, 255, 255), (pcx - 4, pcy - 2), (pcx + 4, pcy - 2), 2)

    elif icon_id == "summon_knight":
        # Silueta de cabeza de corcel
        pts = [(pcx - 8, pcy + 12), (pcx - 12, pcy), (pcx + 4, pcy - 12), (pcx + 10, pcy - 4), (pcx + 10, pcy + 12)]
        pygame.draw.polygon(icon_surf, (120, 215, 255), pts)
        pygame.draw.circle(icon_surf, (255, 255, 255), (pcx - 4, pcy - 4), 2)

    elif icon_id == "black_hole":
        # Agujero negro cósmico arremolinado
        pygame.draw.circle(icon_surf, (140, 50, 255), (pcx, pcy), 14)
        pygame.draw.circle(icon_surf, (20, 10, 30), (pcx, pcy), 9)
        # Brazos de espiral
        pygame.draw.arc(icon_surf, (220, 150, 255), (pcx - 16, pcy - 16, 32, 32), 0, 3.14, 2)
        pygame.draw.arc(icon_surf, (100, 240, 255), (pcx - 16, pcy - 16, 32, 32), 3.14, 6.28, 2)

    elif icon_id == "fireball":
        # Orbe de llamas ardientes
        pygame.draw.circle(icon_surf, (255, 80, 20), (pcx, pcy), 13)
        pygame.draw.circle(icon_surf, (255, 210, 40), (pcx - 2, pcy - 2), 8)
        # Llamas superiores
        pygame.draw.polygon(icon_surf, (255, 60, 20), [(pcx - 8, pcy - 8), (pcx, pcy - 18), (pcx + 8, pcy - 8)])

    elif icon_id == "arrow":
        # Flecha veloz perforante
        pygame.draw.line(icon_surf, (240, 240, 240), (pcx - 14, pcy + 14), (pcx + 10, pcy - 10), 3)
        # Punta
        pygame.draw.polygon(icon_surf, (255, 205, 50), [
            (pcx + 14, pcy - 14), (pcx + 4, pcy - 12), (pcx + 12, pcy - 4)
        ])

    elif icon_id == "place_trap":
        # Trampa de oso desplegable
        pygame.draw.circle(icon_surf, (180, 180, 195), (pcx, pcy), 12, 3)
        pygame.draw.circle(icon_surf, (235, 50, 50), (pcx, pcy), 4)

    surface.blit(icon_surf, (cx - pcx, cy - pcy))
