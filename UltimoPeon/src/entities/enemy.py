"""Módulo de enemigos del juego: Peones, Caballos, Alfiles, Torres y Reinas."""
from typing import TYPE_CHECKING
import pygame
from src.board.board import Board
from src.graphics.pixel_art import draw_pixel_enemy_piece

if TYPE_CHECKING:
    from src.entities.player import Player
    from src.traps.trap_manager import TrapManager


class EnemyPawn:
    """
    Entidad de pieza enemiga. Soporta:
    - 'pawn' (Peón): avance vertical y captura diagonal (ciego a trampas). Puede portar escudo.
    - 'knight' (Caballo): salto en L y captura en L (esquiva trampas).
    - 'bishop' (Alfil): rayos diagonales a distancia (ciego a trampas).
    - 'rook' (Torre): rayos ortogonales a distancia (ciego a trampas).
    - 'queen' (Reina): rayos en 8 direcciones a distancia (esquiva trampas).
    - 'king' (Rey / Jefe Final): movimiento en 8 direcciones a 1 casilla, barra de vida y habilidades.
    """

    def __init__(
        self,
        col: int,
        row: int,
        piece_role: str = "pawn",
        has_shield: bool = False,
        is_boss: bool = False,
        hp: int = 1,
    ):
        self.col = col
        self.row = row
        self.piece_role = piece_role
        self.has_shield = has_shield
        self.is_boss = is_boss
        self.max_hp = hp
        self.hp = hp
        self.alive: bool = True
        self.direction: int = 1         # 1 = abajo, -1 = arriba (para peones)
        self.immobilized_turns: int = 0 # Turnos aturdido por trampa

    def is_smart_against_traps(self) -> bool:
        """Determina si la pieza tiene la inteligencia para esquivar trampas (Caballos, Reina, Rey)."""
        return self.piece_role in ("knight", "queen", "king")

    def hit_damage(
        self,
        damage: int,
        board: Board,
        player: "Player",
        other_enemies: list["EnemyPawn"],
    ) -> str:
        """
        Aplica daño a la pieza:
        - Si tiene escudo: rompe el escudo y retrocede 2 casillas (o 2 a los lados al azar).
        - Si es el jefe: resta HP.
        - Si es pieza normal: muere.
        """
        import random

        if self.has_shield:
            self.has_shield = False
            occupied = {(e.col, e.row) for e in other_enemies if e.alive and e != self} | {(player.col, player.row)}

            def is_valid_and_fair(c, r):
                if not board.is_within_bounds(c, r):
                    return False
                if (c, r) in occupied:
                    return False
                # No quedar inmediatamente en diagonal al jugador (posición injusta)
                if abs(c - player.col) == 1 and abs(r - player.row) == 1:
                    return False
                return True

            # 1. Retroceder 2 casillas
            back_2 = (self.col, self.row - 2)
            if is_valid_and_fair(*back_2):
                self.col, self.row = back_2
                return "shield_broken"

            # 2. Desplazarse 2 casillas a los lados (al azar si ambas están disponibles)
            side_candidates = []
            for dc in (-2, 2):
                sc = (self.col + dc, self.row)
                if is_valid_and_fair(*sc):
                    side_candidates.append(sc)

            if side_candidates:
                chosen = random.choice(side_candidates)
                self.col, self.row = chosen
                return "shield_broken"

            # 3. Fallback seguro: retroceder 1 casilla
            back_1 = (self.col, self.row - 1)
            if is_valid_and_fair(*back_1):
                self.col, self.row = back_1
                return "shield_broken"

            # 4. Fallback lateral 1 casilla
            side_1 = []
            for dc in (-1, 1):
                sc = (self.col + dc, self.row)
                if is_valid_and_fair(*sc):
                    side_1.append(sc)
            if side_1:
                self.col, self.row = random.choice(side_1)
                return "shield_broken"

            # 5. Fallback a cualquier casilla libre de la retaguardia
            free_safe = [
                (c, r) for c in range(board.cols) for r in range(0, min(3, board.rows))
                if is_valid_and_fair(c, r)
            ]
            if free_safe:
                self.col, self.row = random.choice(free_safe)
                return "shield_broken"

            return "shield_broken"

        if self.is_boss:
            self.hp -= damage
            if self.hp <= 0:
                self.alive = False
                return "boss_killed"
            return "boss_damaged"

        self.alive = False
        return "killed"

    def take_turn(
        self,
        board: Board,
        player: "Player",
        other_enemies: list["EnemyPawn"],
        trap_manager: "TrapManager",
    ) -> tuple[str, tuple[int, int] | None]:
        """Calcula y ejecuta el turno de la pieza enemiga según sus patrones clásicos de ajedrez."""
        if not self.alive:
            return "stay", None

        if self.immobilized_turns > 0:
            self.immobilized_turns -= 1
            return "stunned", (self.col, self.row)

        occupied_enemies = {(e.col, e.row) for e in other_enemies if e.alive and e != self}

        # 1. COMPORTAMIENTO: PEÓN
        if self.piece_role == "pawn":
            return self._take_pawn_turn(board, player, occupied_enemies, trap_manager)

        # 2. COMPORTAMIENTO: CABALLO
        elif self.piece_role == "knight":
            return self._take_knight_turn(board, player, occupied_enemies, trap_manager)

        # 3. COMPORTAMIENTO: ALFIL
        elif self.piece_role == "bishop":
            return self._take_ray_turn(board, player, occupied_enemies, trap_manager, diag_only=True)

        # 4. COMPORTAMIENTO: TORRE
        elif self.piece_role == "rook":
            return self._take_ray_turn(board, player, occupied_enemies, trap_manager, ortho_only=True)

        # 5. COMPORTAMIENTO: REINA
        elif self.piece_role == "queen":
            return self._take_ray_turn(board, player, occupied_enemies, trap_manager, all_dirs=True)

        # 6. COMPORTAMIENTO: REY (JEFE FINAL)
        elif self.piece_role == "king":
            return self._take_king_turn(board, player, occupied_enemies, trap_manager)

        return "stay", None

    # =========================================================================
    # LÓGICA ESPECÍFICA POR PIEZA
    # =========================================================================

    def _take_pawn_turn(self, board, player, occupied_enemies, trap_manager):
        # Ataque diagonal
        diag_offsets = [(-1, 1), (1, 1), (-1, -1), (1, -1)]
        for dx, dy in diag_offsets:
            nc, nr = self.col + dx, self.row + dy
            if player.col == nc and player.row == nr:
                self.col, self.row = nc, nr
                return "attack", (nc, nr)

        forward_row = self.row + self.direction
        backward_row = self.row - self.direction

        if board.is_within_bounds(self.col, forward_row):
            if (self.col, forward_row) not in occupied_enemies and not (player.col == self.col and player.row == forward_row):
                self.row = forward_row
                self._check_trap_trigger(self.col, self.row, trap_manager)
                return "move", (self.col, forward_row)

        self.direction = -self.direction
        if board.is_within_bounds(self.col, backward_row):
            if (self.col, backward_row) not in occupied_enemies and not (player.col == self.col and player.row == backward_row):
                self.row = backward_row
                self._check_trap_trigger(self.col, self.row, trap_manager)
                return "move", (self.col, backward_row)

        return "stay", None

    def _take_knight_turn(self, board, player, occupied_enemies, trap_manager):
        l_offsets = [
            (1, 2), (2, 1), (-1, 2), (-2, 1),
            (1, -2), (2, -1), (-1, -2), (-2, -1),
        ]
        valid_moves = []
        for dx, dy in l_offsets:
            nc, nr = self.col + dx, self.row + dy
            if board.is_within_bounds(nc, nr) and (nc, nr) not in occupied_enemies:
                valid_moves.append((nc, nr))

        if not valid_moves:
            return "stay", None

        # Prioridad 1: Atacar al jugador si está a tiro de L
        if (player.col, player.row) in valid_moves:
            self.col, self.row = player.col, player.row
            return "attack", (player.col, player.row)

        # Prioridad 2: Moverse acercándose al jugador evitando trampas (IA inteligente)
        safe_moves = [m for m in valid_moves if trap_manager.get_trap_at(m[0], m[1]) is None]
        candidates = safe_moves if safe_moves else valid_moves

        best = min(candidates, key=lambda m: abs(m[0] - player.col) + abs(m[1] - player.row))
        self.col, self.row = best
        self._check_trap_trigger(self.col, self.row, trap_manager)
        return "move", best

    def _take_ray_turn(self, board, player, occupied_enemies, trap_manager, diag_only=False, ortho_only=False, all_dirs=False):
        directions = []
        if diag_only or all_dirs:
            directions += [(-1, -1), (1, -1), (-1, 1), (1, 1)]
        if ortho_only or all_dirs:
            directions += [(0, -1), (0, 1), (-1, 0), (1, 0)]

        valid_moves = []
        # Buscar rayos
        for dx, dy in directions:
            for dist in range(1, max(board.cols, board.rows)):
                nc = self.col + dx * dist
                nr = self.row + dy * dist
                if not board.is_within_bounds(nc, nr):
                    break
                # Si el jugador está en la línea de visión, ataque letal
                if player.col == nc and player.row == nr:
                    self.col, self.row = nc, nr
                    return "attack", (nc, nr)
                # Si hay otra pieza enemiga, se bloquea la línea
                if (nc, nr) in occupied_enemies:
                    break
                valid_moves.append((nc, nr))

        if not valid_moves:
            return "stay", None

        # Si es la Reina, esquiva trampas en lo posible
        if self.is_smart_against_traps():
            safe_moves = [m for m in valid_moves if trap_manager.get_trap_at(m[0], m[1]) is None]
            candidates = safe_moves if safe_moves else valid_moves
        else:
            candidates = valid_moves

        # Acercarse al jugador
        best = min(candidates, key=lambda m: abs(m[0] - player.col) + abs(m[1] - player.row))
        self.col, self.row = best
        self._check_trap_trigger(self.col, self.row, trap_manager)
        return "move", best

    def _take_king_turn(self, board, player, occupied_enemies, trap_manager):
        """Movimiento del Rey en las 8 direcciones adyacentes a distancia 1."""
        king_offsets = [
            (-1, -1), (0, -1), (1, -1),
            (-1,  0),          (1,  0),
            (-1,  1), (0,  1), (1,  1),
        ]
        valid_moves = []
        for dx, dy in king_offsets:
            nc, nr = self.col + dx, self.row + dy
            if board.is_within_bounds(nc, nr) and (nc, nr) not in occupied_enemies:
                # Comprobar si ataca al jugador
                if player.col == nc and player.row == nr:
                    self.col, self.row = nc, nr
                    return "attack", (nc, nr)
                valid_moves.append((nc, nr))

        if not valid_moves:
            return "stay", None

        # El Rey evita pisar trampas mortales
        safe_moves = [m for m in valid_moves if trap_manager.get_trap_at(m[0], m[1]) is None]
        candidates = safe_moves if safe_moves else valid_moves

        # Movimiento táctico acercándose al jugador
        best = min(candidates, key=lambda m: abs(m[0] - player.col) + abs(m[1] - player.row))
        self.col, self.row = best
        self._check_trap_trigger(self.col, self.row, trap_manager)
        return "move", best

    def _check_trap_trigger(self, col: int, row: int, trap_manager: "TrapManager") -> None:
        effect, turns, _ = trap_manager.trigger_trap_at(col, row, self.piece_role)
        if effect == "kill":
            if self.is_boss:
                # El jefe recibe daño pero no muere de un golpe
                self.hp -= 3
                if self.hp <= 0:
                    self.alive = False
            else:
                self.alive = False
        elif effect == "immobilize":
            self.immobilized_turns = turns

    def render(self, surface: pygame.Surface, board: Board, is_hovered: bool = False) -> None:
        if not self.alive:
            return
        cx, cy = board.get_tile_center(self.col, self.row)
        draw_pixel_enemy_piece(
            surface=surface,
            cx=cx,
            cy=cy,
            size=board.tile_size,
            piece_role=self.piece_role,
            is_hovered=is_hovered,
            is_immobilized=(self.immobilized_turns > 0),
            has_shield=self.has_shield,
            is_boss=self.is_boss,
        )
