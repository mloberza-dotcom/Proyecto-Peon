"""Escena de cinemática final de victoria tras derrotar al Rey Gigante.
Muestra al Peón Blanco como el último guerrero en la cima del castillo bajo la lluvia con truenos.
"""
import math
import random
import pygame
from src.config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED,
    COLOR_ACCENT,
    COLOR_STONE_DARK,
    COLOR_STONE_BORDER,
    COLOR_PIECE_WHITE,
    COLOR_PIECE_WHITE_SHADE,
    COLOR_PIECE_OUTLINE,
)
from src.ui.button import Button
from src.graphics.pixel_art import draw_pixel_hatching


class VictoryCinematicScene:
    """Gestiona la cinemática de victoria final con atmósfera de lluvia, castillo y victoria épica."""

    def __init__(self, on_return_to_menu):
        self.on_return_to_menu = on_return_to_menu
        self.font_title = pygame.font.SysFont("georgia", 32, bold=True)
        self.font_subtitle = pygame.font.SysFont("georgia", 18, bold=True)
        self.font_narrative = pygame.font.SysFont("georgia", 15, italic=True)
        self.font_btn = pygame.font.SysFont("georgia", 16, bold=True)

        btn_w, btn_h = 260, 46
        btn_x = (SCREEN_WIDTH - btn_w) // 2
        btn_y = SCREEN_HEIGHT - 75
        self.menu_button = Button(
            pygame.Rect(btn_x, btn_y, btn_w, btn_h),
            "VOLVER AL MENÚ PRINCIPAL",
            self.font_btn,
            on_click=self.on_return_to_menu,
        )

        # Gotas de lluvia densas
        self.rain_particles = [
            [random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT), random.randint(6, 11)]
            for _ in range(85)
        ]

        # Relámpagos cinemáticos
        self.lightning_active = False
        self.lightning_timer = 0
        self.lightning_duration = 0
        self.lightning_bolt: list[tuple[int, int]] = []
        self.next_strike = 80

        # Animación de capa y brillo
        self.time_counter = 0

    def _generate_cinematic_lightning(self) -> None:
        start_x = random.randint(200, 600)
        start_y = 10
        points = [(start_x, start_y)]
        curr_x, curr_y = start_x, start_y
        while curr_y < 280:
            curr_x += random.randint(-16, 16)
            curr_y += random.randint(18, 32)
            points.append((curr_x, curr_y))

        self.lightning_bolt = points
        self.lightning_duration = random.randint(4, 8)
        self.lightning_active = True

    def update(self) -> None:
        """Actualiza lluvia, viento y relámpagos de la cinemática."""
        self.time_counter += 1

        # Relámpago
        if self.lightning_active:
            self.lightning_duration -= 1
            if self.lightning_duration <= 0:
                self.lightning_active = False
                self.next_strike = random.randint(120, 240)
        else:
            self.next_strike -= 1
            if self.next_strike <= 0:
                self._generate_cinematic_lightning()

        # Lluvia racheada
        for p in self.rain_particles:
            p[0] -= 2.5
            p[1] += p[2]
            if p[1] > SCREEN_HEIGHT:
                p[1] = random.randint(-20, 0)
                p[0] = random.randint(0, SCREEN_WIDTH + 50)

    def handle_event(self, event: pygame.event.Event) -> None:
        self.menu_button.handle_event(event)

    def render(self, surface: pygame.Surface) -> None:
        """Renderiza la cinemática completa."""
        # 1. Cielo tempestuoso oscuro
        for y in range(SCREEN_HEIGHT):
            factor = y / SCREEN_HEIGHT
            r = int(8 + factor * 10)
            g = int(8 + factor * 12)
            b = int(18 + factor * 20)
            pygame.draw.line(surface, (r, g, b), (0, y), (SCREEN_WIDTH, y))

        # 2. Silueta del gran bastión y almenas del castillo
        castle_y = 260
        # Gran pared de piedra del castillo
        pygame.draw.rect(surface, (14, 15, 22), (100, castle_y, 600, SCREEN_HEIGHT - castle_y))
        pygame.draw.rect(surface, (24, 26, 36), (100, castle_y, 600, SCREEN_HEIGHT - castle_y), 3)

        # Almenas de la torre más alta
        almena_w = 40
        almena_h = 32
        for ax in range(120, 680, 60):
            pygame.draw.rect(surface, (16, 17, 26), (ax, castle_y - almena_h, almena_w, almena_h))
            pygame.draw.rect(surface, (34, 38, 52), (ax, castle_y - almena_h, almena_w, almena_h), 2)

        # 3. La corona rota del Rey Tirano caído (en el suelo de piedra a la izquierda)
        crown_x, crown_y = 310, castle_y + 35
        # Corona inclinada y resquebrajada
        crown_pts = [
            (crown_x - 18, crown_y + 10),
            (crown_x - 14, crown_y - 6),
            (crown_x - 6, crown_y + 2),
            (crown_x, crown_y - 12),
            (crown_x + 8, crown_y + 2),
            (crown_x + 16, crown_y - 4),
            (crown_x + 20, crown_y + 10),
        ]
        pygame.draw.polygon(surface, (45, 42, 50), crown_pts)
        pygame.draw.polygon(surface, (200, 150, 40), crown_pts, 2)
        # Rubí apagado / agrietado
        pygame.draw.circle(surface, (140, 30, 30), (crown_x, crown_y), 3)
        # Grieta en la corona caída
        pygame.draw.line(surface, (15, 15, 20), (crown_x - 4, crown_y - 8), (crown_x + 4, crown_y + 8), 2)

        # 4. EL PEÓN BLANCO: El Último Guerrero victorioso en el centro
        px, py = 450, castle_y + 10
        self._render_hero_pawn(surface, px, py)

        # 5. Relámpago y fogonazo
        if self.lightning_active:
            flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            flash_surf.fill((210, 225, 255, random.randint(90, 160)))
            surface.blit(flash_surf, (0, 0))

            if len(self.lightning_bolt) > 1:
                pygame.draw.lines(surface, (255, 255, 255), False, self.lightning_bolt, 3)
                pygame.draw.lines(surface, (130, 200, 255), False, self.lightning_bolt, 6)

        # 6. Partículas de lluvia densa
        for p in self.rain_particles:
            pygame.draw.line(surface, (180, 200, 235, 150), (p[0], p[1]), (p[0] - 4, p[1] + 9), 1)

        # 7. Textos narrativos épicos
        t_glow = (math.sin(self.time_counter / 18.0) + 1.0) * 0.5
        title_surf = self.font_title.render("¡EL REY TIRANO HA CAÍDO!", True, COLOR_ACCENT)
        surface.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH // 2, 60)))

        sub_surf = self.font_subtitle.render("EL PEÓN BLANCO: EL ÚLTIMO GUERRERO", True, COLOR_TEXT_MAIN)
        surface.blit(sub_surf, sub_surf.get_rect(center=(SCREEN_WIDTH // 2, 102)))

        lines = [
            "Bajo la tormenta incesante y el rugido de los truenos,",
            "el último Peón conquista la cima más alta de la fortaleza.",
            "La dinastía de las piezas negras ha llegado a su fin.",
            "Larga vida al Último Peón.",
        ]
        curr_ty = 135
        for line in lines:
            txt_surf = self.font_narrative.render(line, True, COLOR_TEXT_MUTED)
            surface.blit(txt_surf, txt_surf.get_rect(center=(SCREEN_WIDTH // 2, curr_ty)))
            curr_ty += 24

        # 8. Botón interactivo para volver al Menú Principal
        mouse_pos = pygame.mouse.get_pos()
        self.menu_button.update(mouse_pos)
        self.menu_button.render(surface)

    def _render_hero_pawn(self, surface: pygame.Surface, px: int, py: int) -> None:
        """Dibuja al peón blanco erguido con capa flameante y espada/estandarte de victoria."""
        size = 80
        # Sombra
        pygame.draw.ellipse(surface, (0, 0, 0, 140), (px - 26, py + 22, 52, 14))

        # Capa roja flameante al viento hacia la derecha
        wave = math.sin(self.time_counter / 10.0) * 4
        cape_pts = [
            (px - 6, py - 4),
            (px + 8, py - 4),
            (px + 36 + int(wave), py + 12),
            (px + 44 + int(wave * 1.5), py + 28),
            (px + 18, py + 24),
            (px - 4, py + 14),
        ]
        pygame.draw.polygon(surface, (160, 30, 40), cape_pts)
        pygame.draw.polygon(surface, (20, 15, 20), cape_pts, 2)

        # Base de madera clara del Peón héroe
        base_rect = pygame.Rect(px - 24, py + 14, 48, 14)
        pygame.draw.ellipse(surface, COLOR_PIECE_WHITE, base_rect)
        pygame.draw.ellipse(surface, COLOR_PIECE_OUTLINE, base_rect, 2)

        # Torso
        torso_pts = [
            (px - 14, py - 10),
            (px + 14, py - 10),
            (px + 18, py + 16),
            (px - 18, py + 16),
        ]
        pygame.draw.polygon(surface, COLOR_PIECE_WHITE, torso_pts)
        draw_pixel_hatching(surface, pygame.Rect(px, py - 6, 16, 20), COLOR_PIECE_WHITE_SHADE, spacing=3, cross=True)
        pygame.draw.polygon(surface, COLOR_PIECE_OUTLINE, torso_pts, 2)

        # Cuello y Cabeza
        neck_rect = pygame.Rect(px - 14, py - 14, 28, 8)
        pygame.draw.ellipse(surface, COLOR_PIECE_WHITE, neck_rect)
        pygame.draw.ellipse(surface, COLOR_PIECE_OUTLINE, neck_rect, 2)

        head_r = 16
        pygame.draw.circle(surface, COLOR_PIECE_WHITE, (px, py - 26), head_r)
        draw_pixel_hatching(surface, pygame.Rect(px, py - 26, head_r, head_r), COLOR_PIECE_WHITE_SHADE, spacing=3)
        pygame.draw.circle(surface, COLOR_PIECE_OUTLINE, (px, py - 26), head_r, 2)

        # Corona de victoria dorada reluciente
        crown_hero_pts = [
            (px - 11, py - 36),
            (px - 12, py - 46),
            (px - 6, py - 40),
            (px, py - 49),
            (px + 6, py - 40),
            (px + 12, py - 46),
            (px + 11, py - 36),
        ]
        pygame.draw.polygon(surface, COLOR_ACCENT, crown_hero_pts)
        pygame.draw.polygon(surface, (20, 15, 20), crown_hero_pts, 2)
        pygame.draw.circle(surface, (255, 255, 255), (px, py - 49), 2)

        # Espada de luz clavada en la roca victoriosa
        sword_x = px - 28
        sword_top_y = py - 32
        pygame.draw.line(surface, (240, 245, 255), (sword_x, sword_top_y + 12), (sword_x, py + 24), 3)
        pygame.draw.line(surface, COLOR_ACCENT, (sword_x - 8, sword_top_y + 12), (sword_x + 8, sword_top_y + 12), 2)
        pygame.draw.line(surface, (140, 90, 40), (sword_x, sword_top_y), (sword_x, sword_top_y + 12), 3)
        pygame.draw.circle(surface, COLOR_ACCENT, (sword_x, sword_top_y), 3)
