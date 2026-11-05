"""Módulo del Caballo aliado invocado por el jugador."""
import pygame
from src.board.board import Board
from src.graphics.pixel_art import draw_pixel_knight
from src.traps.trap_manager import TrapManager


class AllyKnight:
    """Caballo aliado que lucha junto al Peón blanco durante 15 turnos."""

    def __init__(self, col: int, row: int, duration_turns: int = 15):
        self.col = col
        self.row = row
        self.turns_left: int = duration_turns
        self.alive: bool = True

    def get_valid_knight_moves(self, board: Board, occupied_allies: set[tuple[int, int]]) -> list[tuple[int, int]]:
        """Calcula los movimientos y saltos en L clásicos del caballo de ajedrez."""
        l_offsets = [
            (1, 2), (2, 1), (-1, 2), (-2, 1),
            (1, -2), (2, -1), (-1, -2), (-2, -1),
        ]
        valid = []
        for dx, dy in l_offsets:
            nc = self.col + dx
            nr = self.row + dy
            if board.is_within_bounds(nc, nr) and (nc, nr) not in occupied_allies:
                valid.append((nc, nr))
        return valid

    def take_turn(
        self,
        board: Board,
        enemies: list,
        trap_manager: TrapManager,
        occupied_allies: set[tuple[int, int]],
    ) -> tuple[str, tuple[int, int] | None]:
        """
        Turno del caballo aliado:
        1. Prioridad: Capturar a un enemigo al alcance de su salto en L (evitando trampas si es posible).
        2. Si no, avanza hacia el enemigo más cercano esquivando trampas deliberadamente.
        """
        if not self.alive:
            return "stay", None

        self.turns_left -= 1
        if self.turns_left <= 0:
            self.alive = False
            return "despawn", None

        valid_moves = self.get_valid_knight_moves(board, occupied_allies)
        if not valid_moves:
            return "stay", None

        alive_enemies = [e for e in enemies if e.alive]
        enemy_positions = {(e.col, e.row): e for e in alive_enemies}

        # 1. Comprobar si puede capturar a un enemigo
        for move in valid_moves:
            if move in enemy_positions:
                target_enemy = enemy_positions[move]
                target_enemy.alive = False
                self.col, self.row = move
                return "attack", move

        # 2. Movimiento: Salto táctico evitando trampas (el Caballo es inteligente)
        safe_moves = [m for m in valid_moves if trap_manager.get_trap_at(m[0], m[1]) is None]
        candidate_moves = safe_moves if safe_moves else valid_moves

        if alive_enemies:
            # Acercarse al enemigo más cercano
            best_move = min(
                candidate_moves,
                key=lambda m: min(abs(m[0] - e.col) + abs(m[1] - e.row) for e in alive_enemies),
            )
            self.col, self.row = best_move
            return "move", best_move

        return "stay", None

    def render(self, surface: pygame.Surface, board: Board, is_hovered: bool = False) -> None:
        """Dibuja al corcel aliado en pixel art con sus turnos restantes."""
        if not self.alive:
            return
        cx, cy = board.get_tile_center(self.col, self.row)
        draw_pixel_knight(surface, cx, cy, board.tile_size, is_ally=True, is_hovered=is_hovered, turns_left=self.turns_left)
