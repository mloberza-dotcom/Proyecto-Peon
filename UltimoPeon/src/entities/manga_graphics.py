"""Utilidades de renderizado gráfico estilo Manga / Tinta en blanco y negro con tramado (crosshatching)."""
import pygame


def draw_hatch_lines(
    surface: pygame.Surface,
    rect: pygame.Rect,
    color: tuple[int, int, int],
    spacing: int = 4,
    angle: int = 45,
    cross: bool = False,
    line_width: int = 1,
) -> None:
    """
    Dibuja líneas diagonales de sombreado (tramado estilo manga/grabado) dentro del rectángulo indicado.
    Si cross es True, dibuja líneas cruzadas perpendiculares.
    """
    # Guardamos el clip actual para dibujar únicamente dentro del área delimitada
    prev_clip = surface.get_clip()
    surface.set_clip(rect)

    rx, ry, rw, rh = rect
    # Diagonal principal (arriba-izquierda a abajo-derecha)
    diag_start = -rh
    diag_end = rw + rh
    for d in range(diag_start, diag_end, spacing):
        x1 = rx + d
        y1 = ry
        x2 = rx + d + rh
        y2 = ry + rh
        pygame.draw.line(surface, color, (x1, y1), (x2, y2), line_width)

    # Si se pide tramado cruzado, añadimos la diagonal inversa
    if cross:
        for d in range(diag_start, diag_end, spacing):
            x1 = rx + d + rh
            y1 = ry
            x2 = rx + d
            y2 = ry + rh
            pygame.draw.line(surface, color, (x1, y1), (x2, y2), line_width)

    surface.set_clip(prev_clip)


def draw_manga_pawn(
    surface: pygame.Surface,
    cx: int,
    cy: int,
    size: int,
    is_white: bool = True,
    is_hovered: bool = False,
) -> None:
    """
    Renderiza un peón de ajedrez con estética de dibujo en tinta en blanco y negro (estilo Manga),
    utilizando líneas de sombreado diagonal y líneas cruzadas (crosshatching).
    """
    # Superficie propia transparente para componer la pieza sin manchar el fondo
    pawn_surf = pygame.Surface((size, size), pygame.SRCALPHA)
    pcx, pcy = size // 2, size // 2

    # Paleta de tinta en blanco y negro estilo manga
    INK_BLACK = (15, 16, 20)
    INK_WHITE = (252, 252, 252)
    HATCH_DARK = (40, 42, 50)
    HATCH_LIGHT = (210, 215, 225)
    ENEMY_DARK = (24, 25, 30)
    ACCENT_RED = (235, 45, 55)

    # Dimensiones proporcionales del peón
    base_w, base_h = int(size * 0.54), int(size * 0.15)
    neck_w, neck_h = int(size * 0.32), int(size * 0.09)
    head_r = int(size * 0.17)

    y_base = pcy + int(size * 0.28)
    y_neck = pcy - int(size * 0.02)
    y_head = pcy - int(size * 0.20)
    y_torso_bot = y_base - base_h // 2

    # Puntos del torso (cuerpo cónico del peón)
    torso_pts = [
        (pcx - neck_w // 2, y_neck),
        (pcx + neck_w // 2, y_neck),
        (pcx + int(base_w * 0.36), y_torso_bot),
        (pcx - int(base_w * 0.36), y_torso_bot),
    ]

    # --- 1. Sombra base proyectada en el suelo ---
    shadow_w = int(size * 0.58)
    shadow_h = int(size * 0.16)
    shadow_rect = pygame.Rect(0, 0, shadow_w, shadow_h)
    shadow_rect.center = (pcx, y_base + int(size * 0.06))
    pygame.draw.ellipse(pawn_surf, (0, 0, 0, 80), shadow_rect)

    # --- 2. Relleno y Tramado según el bando (Blanco Manga vs Negro Manga) ---
    if is_white:
        # === PEÓN BLANCO (HEROE MANGA) ===
        # Relleno base blanco papel
        base_rect = pygame.Rect(0, 0, base_w, base_h)
        base_rect.center = (pcx, y_base)
        pygame.draw.ellipse(pawn_surf, INK_WHITE, base_rect)

        pygame.draw.polygon(pawn_surf, INK_WHITE, torso_pts)

        neck_rect = pygame.Rect(0, 0, neck_w, neck_h)
        neck_rect.center = (pcx, y_neck)
        pygame.draw.ellipse(pawn_surf, INK_WHITE, neck_rect)

        pygame.draw.circle(pawn_surf, INK_WHITE, (pcx, y_head), head_r)

        # Sombreado de líneas diagonales estilo manga en el lado derecho (sombra)
        # Sombreado del torso (mitad derecha)
        torso_shadow_rect = pygame.Rect(pcx, y_neck, base_w // 2, y_torso_bot - y_neck)
        draw_hatch_lines(pawn_surf, torso_shadow_rect, HATCH_DARK, spacing=4, angle=45, cross=False)

        # Sombreado en la base (mitad derecha, líneas diagonales)
        base_shadow_rect = pygame.Rect(pcx, y_base - base_h // 2, base_w // 2, base_h)
        draw_hatch_lines(pawn_surf, base_shadow_rect, HATCH_DARK, spacing=4, angle=45, cross=False)

        # Sombreado bajo el cuello con tramado cruzado (crosshatching para sombra profunda)
        cross_rect = pygame.Rect(pcx - 10, y_neck - 2, 20, 8)
        draw_hatch_lines(pawn_surf, cross_rect, HATCH_DARK, spacing=3, angle=45, cross=True)

        # Sombreado en la cabeza (media luna inferior-derecha con tramado)
        head_shadow_rect = pygame.Rect(pcx, y_head, head_r, head_r)
        draw_hatch_lines(pawn_surf, head_shadow_rect, HATCH_DARK, spacing=4, angle=45, cross=False)

        # Contornos gruesos de pluma de tinta japonesa
        line_thick = 3
        pygame.draw.ellipse(pawn_surf, INK_BLACK, base_rect, line_thick)
        pygame.draw.polygon(pawn_surf, INK_BLACK, torso_pts, line_thick)
        pygame.draw.ellipse(pawn_surf, INK_BLACK, neck_rect, line_thick)
        pygame.draw.circle(pawn_surf, INK_BLACK, (pcx, y_head), head_r, line_thick)

        # Detalles Manga del Peón Blanco:
        # Destello de brillo puro en la cabeza
        pygame.draw.circle(pawn_surf, (255, 255, 255), (pcx - head_r // 3, y_head - head_r // 3), 3)

        # Marca dorada sutil del "Último Peón" en el centro de la cabeza
        pygame.draw.circle(pawn_surf, (245, 185, 45), (pcx, y_head - 2), 3)

    else:
        # === PEÓN NEGRO (ENEMIGO MANGA) ===
        # Relleno negro carbón / tinta sumi profunda
        base_rect = pygame.Rect(0, 0, base_w, base_h)
        base_rect.center = (pcx, y_base)
        pygame.draw.ellipse(pawn_surf, ENEMY_DARK, base_rect)

        pygame.draw.polygon(pawn_surf, ENEMY_DARK, torso_pts)

        neck_rect = pygame.Rect(0, 0, neck_w, neck_h)
        neck_rect.center = (pcx, y_neck)
        pygame.draw.ellipse(pawn_surf, ENEMY_DARK, neck_rect)

        pygame.draw.circle(pawn_surf, ENEMY_DARK, (pcx, y_head), head_r)

        # Tramado de líneas cruzadas (Crosshatching claro) sobre el cuerpo oscuro (efecto screentone manga)
        torso_texture_rect = pygame.Rect(pcx - neck_w // 2, y_neck + 2, neck_w, y_torso_bot - y_neck - 4)
        draw_hatch_lines(pawn_surf, torso_texture_rect, HATCH_LIGHT, spacing=5, angle=45, cross=True)

        base_texture_rect = pygame.Rect(pcx - base_w // 3, y_base - base_h // 2 + 1, (base_w * 2) // 3, base_h - 2)
        draw_hatch_lines(pawn_surf, base_texture_rect, HATCH_LIGHT, spacing=5, angle=-45, cross=False)

        # Contorno definido en tinta negra profunda
        line_thick = 3
        pygame.draw.ellipse(pawn_surf, INK_BLACK, base_rect, line_thick)
        pygame.draw.polygon(pawn_surf, INK_BLACK, torso_pts, line_thick)
        pygame.draw.ellipse(pawn_surf, INK_BLACK, neck_rect, line_thick)
        pygame.draw.circle(pawn_surf, INK_BLACK, (pcx, y_head), head_r, line_thick)

        # Ojo / Hendidura amenazante estilo manga oscuro (rojo carmesí)
        eye_w = int(head_r * 0.9)
        eye_rect = pygame.Rect(pcx - eye_w // 2, y_head - 2, eye_w, 4)
        pygame.draw.ellipse(pawn_surf, ACCENT_RED, eye_rect)
        pygame.draw.circle(pawn_surf, (255, 230, 230), (pcx, y_head), 2)

    # Brillo exterior de hover si el cursor está sobre la pieza
    if is_hovered:
        glow_rect = pygame.Rect(pcx - base_w // 2 - 4, y_head - head_r - 4, base_w + 8, y_base - y_head + head_r + 10)
        pygame.draw.rect(pawn_surf, (245, 185, 45, 120), glow_rect, 2, border_radius=6)

    # Blit en la superficie de destino centrado en (cx, cy)
    surface.blit(pawn_surf, (cx - pcx, cy - pcy))
