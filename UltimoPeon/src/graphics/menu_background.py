"""Fondo animado del Menú Principal en Pixel Art.
Muestra al Peón blanco de espaldas sobre un peñasco rocoso mirando un castillo colosal
en la cima de una montaña, con tormenta y relámpagos dinámicos.
"""
import random
import pygame
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_ACCENT
from src.graphics.pixel_art import draw_pixel_hatching


class MenuBackground:
    """Gestiona el fondo paisajístico del menú con efectos de trueno y relámpagos."""

    def __init__(self):
        # Superficie estática base para no recalcular montañas cada fotograma
        self.base_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        # Estado del sistema de relámpagos
        self.lightning_active: bool = False
        self.lightning_timer: int = 0
        self.lightning_duration: int = 0
        self.lightning_bolt: list[tuple[int, int]] = []
        self.next_strike: int = random.randint(120, 260)  # frames hasta el próximo rayo

        # Partículas de lluvia / viento
        self.rain_particles = [
            [random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT), random.randint(4, 8)]
            for _ in range(45)
        ]

        self._render_static_scenery()

    def _render_static_scenery(self) -> None:
        """Dibuja el cielo, montañas, el castillo colosal y el peón de espaldas."""
        surf = self.base_surf

        # 1. Cielo de tormenta degradado oscuro
        for y in range(SCREEN_HEIGHT):
            factor = y / SCREEN_HEIGHT
            r = int(12 + factor * 14)
            g = int(12 + factor * 16)
            b = int(22 + factor * 22)
            pygame.draw.line(surf, (r, g, b), (0, y), (SCREEN_WIDTH, y))

        # 2. Montañas lejanas (silueta oscura)
        pts_distant_mountains = [
            (0, 380),
            (140, 280),
            (280, 340),
            (400, 200),  # Pico principal donde se asienta el castillo
            (520, 310),
            (680, 270),
            (SCREEN_WIDTH, 360),
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            (0, SCREEN_HEIGHT),
        ]
        pygame.draw.polygon(surf, (22, 21, 32), pts_distant_mountains)

        # 3. El Castillo Colosal (En la cima de la montaña central x=400, y=200)
        cx, cy = 400, 200
        # Gran muralla y bastión
        pygame.draw.rect(surf, (14, 13, 20), (cx - 70, cy - 80, 140, 80))
        # Torre central gigantesca
        pygame.draw.rect(surf, (10, 9, 16), (cx - 30, cy - 160, 60, 160))
        # Agujas y almenas
        for tx in [-65, -35, 10, 45]:
            pygame.draw.rect(surf, (10, 9, 16), (cx + tx, cy - 110, 20, 35))
            pygame.draw.polygon(surf, (8, 7, 12), [(cx + tx, cy - 110), (cx + tx + 10, cy - 135), (cx + tx + 20, cy - 110)])

        # Aguja de la gran torre central
        pygame.draw.polygon(surf, (6, 5, 10), [(cx - 30, cy - 160), (cx, cy - 210), (cx + 30, cy - 160)])

        # Ventanas góticas con brillo carmesí oscuro
        for wy in [-130, -90, -50]:
            pygame.draw.rect(surf, (160, 40, 40), (cx - 4, cy + wy, 8, 14), border_radius=2)
            pygame.draw.circle(surf, (255, 80, 80), (cx, cy + wy + 4), 2)

        # 4. Colinas intermedias
        pts_mid = [
            (0, 420),
            (180, 360),
            (320, 410),
            (500, 370),
            (700, 430),
            (SCREEN_WIDTH, 440),
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            (0, SCREEN_HEIGHT),
        ]
        pygame.draw.polygon(surf, (28, 27, 40), pts_mid)

        # 5. Peñasco rocoso en primer plano (donde se para el Peón)
        pts_cliff = [
            (180, SCREEN_HEIGHT),
            (260, 480),
            (380, 450),
            (540, 470),
            (620, SCREEN_HEIGHT),
        ]
        pygame.draw.polygon(surf, (36, 38, 52), pts_cliff)
        pygame.draw.lines(surf, (55, 60, 80), False, pts_cliff[:4], 2)

        # 6. EL PEÓN BLANCO DE ESPALDAS (mirando al castillo)
        # Posicionado en el peñasco (x=400, y=455)
        px, py = 400, 455
        self._render_back_pawn(surf, px, py)

    def _render_back_pawn(self, surf: pygame.Surface, px: int, py: int) -> None:
        """Dibuja al peón blanco visto desde atrás contemplando la fortaleza."""
        size = 86

        # Sombra en la roca
        pygame.draw.ellipse(surf, (0, 0, 0, 140), (px - 28, py + 14, 56, 16))

        # Base de madera tallada (vista posterior)
        base_rect = pygame.Rect(px - 24, py + 4, 48, 16)
        pygame.draw.ellipse(surf, (235, 225, 205), base_rect)
        pygame.draw.ellipse(surf, (20, 18, 25), base_rect, 2)

        # Torso del peón (de espaldas)
        torso_pts = [
            (px - 14, py - 18),
            (px + 14, py - 18),
            (px + 20, py + 8),
            (px - 20, py + 8),
        ]
        pygame.draw.polygon(surf, (240, 230, 210), torso_pts)

        # Tramado de sombreado en la espalda (veta de madera tallada)
        back_hatch_rect = pygame.Rect(px - 10, py - 14, 20, 20)
        draw_pixel_hatching(surf, back_hatch_rect, (175, 160, 135), spacing=3, cross=True)
        pygame.draw.polygon(surf, (20, 18, 25), torso_pts, 2)

        # Cuello / Anillo
        neck_rect = pygame.Rect(px - 15, py - 22, 30, 8)
        pygame.draw.ellipse(surf, (245, 235, 215), neck_rect)
        pygame.draw.ellipse(surf, (20, 18, 25), neck_rect, 2)

        # Cabeza (vista desde atrás)
        head_r = 17
        pygame.draw.circle(surf, (250, 240, 220), (px, py - 36), head_r)
        # Sombreado inferior de la cabeza
        head_shade = pygame.Rect(px - head_r, py - 36, head_r * 2, head_r)
        draw_pixel_hatching(surf, head_shade, (180, 165, 140), spacing=3, cross=False)
        pygame.draw.circle(surf, (20, 18, 25), (px, py - 36), head_r, 2)

        # Capa o emblema rúnico en la espalda
        pygame.draw.polygon(surf, (140, 35, 45), [
            (px - 10, py - 16), (px + 10, py - 16), (px + 14, py + 12), (px - 14, py + 12)
        ])
        pygame.draw.circle(surf, COLOR_ACCENT, (px, py - 2), 4)

    def _generate_lightning(self) -> None:
        """Genera un relámpago quebrado que desciende de las nubes."""
        start_x = random.randint(250, 550)
        start_y = 40
        points = [(start_x, start_y)]

        curr_x, curr_y = start_x, start_y
        while curr_y < 260:
            curr_x += random.randint(-18, 18)
            curr_y += random.randint(15, 30)
            points.append((curr_x, curr_y))

        self.lightning_bolt = points
        self.lightning_duration = random.randint(4, 9)
        self.lightning_active = True

    def update(self) -> None:
        """Actualiza el temporizador de relámpagos y la lluvia."""
        # 1. Temporizador de relámpagos
        if self.lightning_active:
            self.lightning_duration -= 1
            if self.lightning_duration <= 0:
                self.lightning_active = False
                self.next_strike = random.randint(150, 320)
        else:
            self.next_strike -= 1
            if self.next_strike <= 0:
                self._generate_lightning()

        # 2. Movimiento de lluvia
        for p in self.rain_particles:
            p[0] -= 2  # Viento hacia la izquierda
            p[1] += p[2]
            if p[1] > SCREEN_HEIGHT:
                p[1] = random.randint(-20, 0)
                p[0] = random.randint(0, SCREEN_WIDTH + 40)

    def render(self, surface: pygame.Surface) -> None:
        """Dibuja el fondo, los relámpagos y las partículas de tormenta."""
        surface.blit(self.base_surf, (0, 0))

        # Si hay relámpago activo, iluminar el cielo con un fogonazo
        if self.lightning_active:
            flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            alpha = random.randint(80, 160)
            flash_surf.fill((190, 210, 255, alpha))
            surface.blit(flash_surf, (0, 0))

            # Dibujar el rayo principal
            if len(self.lightning_bolt) > 1:
                pygame.draw.lines(surface, (255, 255, 255), False, self.lightning_bolt, 3)
                pygame.draw.lines(surface, (140, 200, 255), False, self.lightning_bolt, 6)

        # Lluvia racheada
        for p in self.rain_particles:
            pygame.draw.line(surface, (160, 180, 220, 120), (p[0], p[1]), (p[0] - 3, p[1] + 6), 1)
