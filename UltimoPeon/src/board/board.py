"""Módulo del tablero dinámico con marco de piedra rúnica y losas de madera tallada."""
import pygame
from src.config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_TEXT_MUTED,
)
from src.graphics.pixel_art import get_wood_tile, draw_stone_rune_border


class Board:
    """Tablero con estética de piedra rúnica y losas de madera tallada en pixel art."""

    def __init__(self, cols: int = 5, rows: int = 5):
        self.cols = cols
        self.rows = rows
        self.font = pygame.font.SysFont("georgia", 12, bold=True)
        self.update_layout()

    def set_dimensions(self, cols: int, rows: int) -> None:
        """Cambia el tamaño del tablero según el nivel (hasta 8x8) y recalcula posiciones."""
        self.cols = cols
        self.rows = rows
        self.update_layout()

    def update_layout(self) -> None:
        """Calcula el tamaño de casilla y offset para que el tablero se mantenga centrado."""
        # Calculamos el tamaño de casilla ideal para que siempre quepa con holgura
        max_board_px = 420
        self.tile_size = max(46, min(76, max_board_px // max(self.cols, self.rows)))

        board_w = self.cols * self.tile_size
        board_h = self.rows * self.tile_size

        self.offset_x = (SCREEN_WIDTH - board_w) // 2
        # Margen vertical para no chocar con el encabezado de turnos ni con el pie
        self.offset_y = (SCREEN_HEIGHT - board_h) // 2 + 15

    def is_within_bounds(self, col: int, row: int) -> bool:
        """Comprueba si las coordenadas están dentro del tablero."""
        return 0 <= col < self.cols and 0 <= row < self.rows

    def tile_to_pixel(self, col: int, row: int) -> tuple[int, int]:
        """Obtiene la coordenada (x, y) de la esquina superior izquierda de la casilla."""
        x = self.offset_x + col * self.tile_size
        y = self.offset_y + row * self.tile_size
        return x, y

    def get_tile_center(self, col: int, row: int) -> tuple[int, int]:
        """Obtiene las coordenadas del centro de la casilla en píxeles."""
        px, py = self.tile_to_pixel(col, row)
        return px + self.tile_size // 2, py + self.tile_size // 2

    def pixel_to_tile(self, px: int, py: int) -> tuple[int, int] | None:
        """Convierte una coordenada del cursor (px, py) a coordenadas del tablero (col, row)."""
        rel_x = px - self.offset_x
        rel_y = py - self.offset_y
        if rel_x < 0 or rel_y < 0:
            return None

        col = rel_x // self.tile_size
        row = rel_y // self.tile_size

        if self.is_within_bounds(col, row):
            return col, row
        return None

    def render(self, surface: pygame.Surface, time_ms: int = 0) -> None:
        """Dibuja el marco de piedra rúnica y las losas de madera tallada en pixel art."""
        board_w = self.cols * self.tile_size
        board_h = self.rows * self.tile_size
        board_rect = pygame.Rect(self.offset_x, self.offset_y, board_w, board_h)

        # 1. Marco de piedra con runas nórdicas talladas y brillantes
        draw_stone_rune_border(surface, board_rect, thickness=20, time_ms=time_ms)

        # 2. Casillas de madera tallada (alternancia de losas claras y oscuras)
        for r in range(self.rows):
            for c in range(self.cols):
                tile_x, tile_y = self.tile_to_pixel(c, r)
                is_light = (c + r) % 2 == 0

                wood_surf = get_wood_tile(self.tile_size, is_light)
                surface.blit(wood_surf, (tile_x, tile_y))

                # Letras (A, B, C...) en la fila inferior
                if r == self.rows - 1:
                    col_letter = chr(ord('A') + c)
                    label = self.font.render(col_letter, True, COLOR_TEXT_MUTED)
                    surface.blit(label, (tile_x + self.tile_size - 13, tile_y + self.tile_size - 15))

                # Números (1, 2, 3...) en la columna izquierda
                if c == 0:
                    row_num = str(self.rows - r)
                    label = self.font.render(row_num, True, COLOR_TEXT_MUTED)
                    surface.blit(label, (tile_x + 3, tile_y + 3))
