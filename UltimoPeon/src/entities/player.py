"""Módulo del Peón Blanco (Jugador) con mecánica de combate de Rey contra peones."""
from typing import TYPE_CHECKING
import pygame
from src.board.board import Board
from src.graphics.pixel_art import draw_pixel_pawn

if TYPE_CHECKING:
    from src.entities.enemy import EnemyPawn
    from src.powers.power_manager import PowerManager


class Player:
    """Entidad del Peón Blanco controlado por el usuario."""

    def __init__(self, col: int, row: int):
        self.col = col
        self.row = row
        self.alive: bool = True
        self.immobilized_turns: int = 0

    def get_valid_moves(
        self,
        board: Board,
        enemies: list["EnemyPawn"],
        power_manager: "PowerManager | None" = None,
    ) -> list[tuple[int, int]]:
        """
        Calcula las casillas legales:
        - Movimiento a casillas vacías: ortogonal (1 casilla, o 2 con 'Paso Ligero').
        - REGLA DE COMBATE:
          * Contra PEONES: El peón blanco mata como un REY (en las 8 direcciones adyacentes a 1 casilla).
          * Contra OTROS ENEMIGOS: Sólo mata en diagonal (a no ser que tenga bendiciones como Torre/Alfil).
        """
        if not self.alive or self.immobilized_turns > 0:
            return []

        enemy_map = {(e.col, e.row): e for e in enemies if e.alive}
        enemy_positions = set(enemy_map.keys())
        valid_destinations: set[tuple[int, int]] = set()

        # =====================================================================
        # 1. MOVIMIENTO A CASILLAS VACÍAS (Ortogonal)
        # =====================================================================
        max_move_range = 2 if (power_manager and power_manager.has_range_move) else 1
        ortho_dirs = [(0, -1), (0, 1), (-1, 0), (1, 0)]

        for dx, dy in ortho_dirs:
            for dist in range(1, max_move_range + 1):
                nc = self.col + dx * dist
                nr = self.row + dy * dist
                if not board.is_within_bounds(nc, nr):
                    break
                if (nc, nr) in enemy_positions:
                    break
                valid_destinations.add((nc, nr))

        # =====================================================================
        # 2. CAPTURA Y COMBATE:
        # =====================================================================
        king_dirs = [
            (0, -1), (0, 1), (-1, 0), (1, 0),    # Ortogonal
            (-1, -1), (1, -1), (-1, 1), (1, 1),  # Diagonal
        ]
        diag_dirs = [(-1, -1), (1, -1), (-1, 1), (1, 1)]

        for enemy in enemies:
            if not enemy.alive:
                continue

            ec, er = enemy.col, enemy.row
            dx = ec - self.col
            dy = er - self.row

            if enemy.piece_role == "pawn" or enemy.is_boss:
                # --- CONTRA PEONES Y JEFE FINAL (REY): ATACA/COME COMO UN REY (8 direcciones adyacentes) ---
                if (dx, dy) in king_dirs:
                    valid_destinations.add((ec, er))
                # Alcance letal (+1 en diagonal)
                elif power_manager and power_manager.has_range_kill and (abs(dx) == 2 and abs(dy) == 2):
                    mid_c = self.col + dx // 2
                    mid_r = self.row + dy // 2
                    if (mid_c, mid_r) not in enemy_positions:
                        valid_destinations.add((ec, er))

            else:
                # --- CONTRA OTROS ENEMIGOS: ÚNICAMENTE EN DIAGONAL ---
                if (dx, dy) in diag_dirs:
                    valid_destinations.add((ec, er))
                elif power_manager and power_manager.has_range_kill and (abs(dx) == 2 and abs(dy) == 2):
                    mid_c = self.col + dx // 2
                    mid_r = self.row + dy // 2
                    if (mid_c, mid_r) not in enemy_positions:
                        valid_destinations.add((ec, er))

        # =====================================================================
        # 3. PODER: MATAR COMO TORRE (Ortogonal a distancia contra cualquier enemigo)
        # =====================================================================
        if power_manager and power_manager.has_kill_rook:
            for dx, dy in ortho_dirs:
                for dist in range(1, max(board.cols, board.rows)):
                    nc = self.col + dx * dist
                    nr = self.row + dy * dist
                    if not board.is_within_bounds(nc, nr):
                        break
                    if (nc, nr) in enemy_positions:
                        valid_destinations.add((nc, nr))
                        break

        # =====================================================================
        # 4. PODER: MATAR COMO ALFIL (Diagonal ilimitada contra cualquier enemigo)
        # =====================================================================
        if power_manager and power_manager.has_kill_bishop:
            for dx, dy in diag_dirs:
                for dist in range(1, max(board.cols, board.rows)):
                    nc = self.col + dx * dist
                    nr = self.row + dy * dist
                    if not board.is_within_bounds(nc, nr):
                        break
                    if (nc, nr) in enemy_positions:
                        valid_destinations.add((nc, nr))
                        break

        return list(valid_destinations)

    def move_to(self, col: int, row: int) -> None:
        self.col = col
        self.row = row

    def render(self, surface: pygame.Surface, board: Board, is_hovered: bool = False) -> None:
        if not self.alive:
            return
        cx, cy = board.get_tile_center(self.col, self.row)
        draw_pixel_pawn(
            surface,
            cx,
            cy,
            board.tile_size,
            is_white=True,
            is_hovered=is_hovered,
            is_immobilized=(self.immobilized_turns > 0),
        )
