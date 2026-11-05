"""Gestor de ciclo de vida, aparición y efectos de trampas ambientales."""
import random
import pygame
from src.board.board import Board
from src.traps.trap import Trap, TrapType
from src.graphics.pixel_art import draw_trap_sprite


class TrapManager:
    """Controla la aparición cada 5 turnos, expiración (15 turnos) y resolución de trampas."""

    def __init__(self):
        self.traps: list[Trap] = []
        self.last_spawn_turn: int = 0

    def reset(self) -> None:
        """Limpia todas las trampas al iniciar un nuevo nivel o partida."""
        self.traps.clear()
        self.last_spawn_turn = 0

    def check_turn_start_spawn(
        self,
        current_turn: int,
        board: Board,
        level: int,
        forbidden_tiles: set[tuple[int, int]],
    ) -> Trap | None:
        """
        Debe ejecutarse AL COMIENZO del turno (antes de cualquier movimiento).
        Aparece una trampa al azar cada 5 turnos y dura 15 turnos.
        """
        # Eliminar trampas que hayan alcanzado los 15 turnos
        self.traps = [t for t in self.traps if not t.is_expired(current_turn)]

        # Comprobar si corresponde spawn en este turno (múltiplo de 5 y no generado ya)
        if current_turn % 5 == 0 and current_turn != self.last_spawn_turn:
            self.last_spawn_turn = current_turn
            trap = self._spawn_random_trap(board, level, current_turn, forbidden_tiles)
            if trap:
                self.traps.append(trap)
                return trap
        return None

    def _spawn_random_trap(
        self,
        board: Board,
        level: int,
        current_turn: int,
        forbidden_tiles: set[tuple[int, int]],
    ) -> Trap | None:
        """Crea una trampa de tipo aleatorio respetando las casillas ocupadas."""
        trap_type = random.choice([TrapType.BEAR_TRAP, TrapType.VINES, TrapType.LAVA])

        # Tamaño del charco de lava según el nivel
        if trap_type == TrapType.LAVA:
            if level <= 2:
                num_tiles = 1
            elif level <= 6:
                num_tiles = 2
            elif level <= 12:
                num_tiles = random.choice([3, 4])
            else:
                num_tiles = random.choice([4, 5])
        else:
            num_tiles = 1

        # Todas las casillas ocupadas por trampas existentes
        existing_trap_tiles = {tile for t in self.traps for tile in t.tiles}
        unavailable = forbidden_tiles | existing_trap_tiles

        available_tiles = [
            (c, r)
            for c in range(board.cols)
            for r in range(board.rows)
            if (c, r) not in unavailable
        ]

        if not available_tiles:
            return None

        # Casilla inicial
        first_tile = random.choice(available_tiles)
        selected_tiles = [first_tile]

        # Para lava de múltiples casillas, buscamos casillas contiguas
        for _ in range(num_tiles - 1):
            curr_c, curr_r = selected_tiles[-1]
            neighbors = [
                (curr_c + dx, curr_r + dy)
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]
                if board.is_within_bounds(curr_c + dx, curr_r + dy)
                and (curr_c + dx, curr_r + dy) not in unavailable
                and (curr_c + dx, curr_r + dy) not in selected_tiles
            ]
            if neighbors:
                selected_tiles.append(random.choice(neighbors))
            else:
                break

        return Trap(
            trap_type=trap_type,
            tiles=selected_tiles,
            duration_turns=15,
            spawn_turn=current_turn,
        )

    def trigger_trap_at(
        self,
        col: int,
        row: int,
        piece_role: str,  # 'player', 'pawn', 'knight', 'bishop', 'rook', etc.
    ) -> tuple[str, int, str]:
        """
        Determina las consecuencias de que una pieza caiga en una trampa:
        Retorna (efecto, turnos_inmovilizado, nombre_trampa)
        - 'kill': la pieza muere inmediatamente
        - 'immobilize': la pieza queda aturdida / congelada por X turnos
        - 'none': no hay trampa
        """
        for trap in self.traps:
            if trap.occupies(col, row):
                # 1. CHARCO DE LAVA: Si lo pisas mueres (jugador y enemigos)
                if trap.trap_type == TrapType.LAVA:
                    return "kill", 0, trap.name

                # 2. TRAMPA PARA OSOS:
                # - Si es un peón rival: MUERE
                # - Si es otro enemigo: se queda quieto 2 turnos
                # - Si eres tú: te quedas quieto 1 turno
                elif trap.trap_type == TrapType.BEAR_TRAP:
                    if piece_role == "player":
                        return "immobilize", 1, trap.name
                    elif piece_role == "pawn":
                        return "kill", 0, trap.name
                    else:
                        return "immobilize", 2, trap.name

                # 3. ENREDADERA: Cualquiera que la pise se queda quieto en su turno
                elif trap.trap_type == TrapType.VINES:
                    return "immobilize", 1, trap.name

        return "none", 0, ""

    def get_trap_at(self, col: int, row: int) -> Trap | None:
        """Devuelve la trampa que cubre la casilla (si existe)."""
        for trap in self.traps:
            if trap.occupies(col, row):
                return trap
        return None

    def render(self, surface: pygame.Surface, board: Board, time_ms: int = 0) -> None:
        """Dibuja todas las trampas activas sobre el tablero."""
        for trap in self.traps:
            for c, r in trap.tiles:
                cx, cy = board.get_tile_center(c, r)
                if trap.trap_type == TrapType.BEAR_TRAP:
                    t_name = "bear_trap"
                elif trap.trap_type == TrapType.VINES:
                    t_name = "vines"
                else:
                    t_name = "lava"
                draw_trap_sprite(surface, t_name, cx, cy, board.tile_size, time_ms)
