"""Controlador principal del juego 'El Último Peón' en Pixel Art con Piedra Rúnica, Madera y Audio."""
from enum import Enum, auto
import random
import pygame
from src.config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    WINDOW_TITLE,
    COLOR_BG,
    COLOR_PANEL,
    COLOR_BORDER,
    COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED,
    COLOR_ACCENT,
    COLOR_VALID_MOVE,
    COLOR_VALID_MOVE_HOVER,
    COLOR_VALID_BORDER,
    COLOR_ATTACK_MOVE,
)
from src.board.board import Board
from src.entities.player import Player
from src.entities.enemy import EnemyPawn
from src.entities.ally import AllyKnight
from src.core.turn_manager import TurnManager, TurnPhase
from src.traps.trap_manager import TrapManager
from src.traps.trap import Trap, TrapType
from src.powers.power_manager import PowerManager
from src.powers.power import Power
from src.scenes.reward_screen import RewardScreen
from src.scenes.cinematic_scene import VictoryCinematicScene
from src.graphics.menu_background import MenuBackground
from src.graphics.pixel_art import draw_boss_health_bar, draw_board_fissure
from src.ui.button import Button
from src.ui.inspector import InspectorPanel
from src.graphics.vfx import VFXManager
from src.audio.sound_manager import SoundManager
from src.core.enemy_spawner import spawn_enemies_for_level


class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    LEVEL_REWARD = auto()
    OPTIONS = auto()
    GAME_OVER = auto()
    VICTORY_CINEMATIC = auto()


class TargetingMode(Enum):
    NONE = auto()
    SUMMON_KNIGHT = auto()
    BLACK_HOLE = auto()
    BLACK_HOLE_TELEPORT = auto()
    FIREBALL = auto()
    ARROW = auto()
    PLACE_TRAP = auto()


class Game:
    """Coordinador general del ciclo de juego, renderizado, trampas, poderes, audio y jefe final."""

    def __init__(self):
        pygame.init()
        pygame.font.init()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        self.state: GameState = GameState.MENU
        self.level: int = 1

        # Tipografías
        self.font_logo = pygame.font.SysFont("georgia", 42, bold=True)
        self.font_title = pygame.font.SysFont("georgia", 24, bold=True)
        self.font_btn = pygame.font.SysFont("georgia", 18, bold=True)
        self.font_ui = pygame.font.SysFont("arial", 15, bold=True)
        self.font_small = pygame.font.SysFont("arial", 13)

        # Módulos de audio, fondo y lógica
        self.sound_manager = SoundManager()
        self.menu_bg = MenuBackground()
        self.board = Board(cols=5, rows=5)
        self.player = Player(col=2, row=4)
        self.enemies: list[EnemyPawn] = []
        self.allies: list[AllyKnight] = []

        self.turn_manager = TurnManager()
        self.trap_manager = TrapManager()
        self.power_manager = PowerManager()
        self.reward_screen = RewardScreen()
        self.cinematic_scene = VictoryCinematicScene(on_return_to_menu=lambda: self.set_state(GameState.MENU))
        self.inspector = InspectorPanel()
        self.vfx_manager = VFXManager()

        # Mecánicas del Jefe Final (Rey Gigante)
        self.split_rows: list[int] = []
        self.boss_phase_1_split: bool = False
        self.boss_phase_2_split: bool = False

        # Apuntado activo
        self.targeting_mode: TargetingMode = TargetingMode.NONE
        self.black_hole_target_enemy: EnemyPawn | None = None
        self.hovered_tile: tuple[int, int] | None = None
        self.status_message: str = "Haz clic en una casilla roja para moverte o comer."
        self.death_reason: str = ""

        # Inicialización de botones
        self._init_buttons()

        # Iniciar música del menú
        self.sound_manager.play_music("menu")

    def _safe_set_cursor(self, cursor: int) -> None:
        try:
            pygame.mouse.set_cursor(cursor)
        except pygame.error:
            pass

    def _init_buttons(self) -> None:
        btn_w, btn_h = 250, 50
        cx = (SCREEN_WIDTH - btn_w) // 2
        start_y = 310
        gap = 68

        # Menú principal simplificado (Tienda descartada)
        self.menu_buttons = [
            Button(pygame.Rect(cx, start_y, btn_w, btn_h), "JUGAR INCURSIÓN", self.font_btn, on_click=self.start_new_run),
            Button(pygame.Rect(cx, start_y + gap, btn_w, btn_h), "OPCIONES", self.font_btn, on_click=lambda: self.set_state(GameState.OPTIONS)),
        ]

        self.back_button = Button(
            pygame.Rect((SCREEN_WIDTH - 200) // 2, SCREEN_HEIGHT - 75, 200, 42),
            "VOLVER AL MENÚ",
            self.font_btn,
            on_click=lambda: self.set_state(GameState.MENU),
        )

        self.in_game_menu_btn = Button(
            pygame.Rect(20, 16, 110, 36),
            "← MENÚ",
            self.font_ui,
            on_click=lambda: self.set_state(GameState.MENU),
        )

        self.game_over_buttons = [
            Button(pygame.Rect(cx, 305, btn_w, 44), "REINTENTAR", self.font_btn, on_click=self.start_new_run),
            Button(pygame.Rect(cx, 360, btn_w, 44), "MENÚ PRINCIPAL", self.font_btn, on_click=lambda: self.set_state(GameState.MENU)),
        ]

        # Botones de ajuste de volumen en la pantalla de opciones
        btn_vol_w, btn_vol_h = 44, 34
        self.btn_mus_down = Button(pygame.Rect(SCREEN_WIDTH // 2 + 100, 168, btn_vol_w, btn_vol_h), "◀", self.font_ui, on_click=lambda: self._adj_music(-0.1))
        self.btn_mus_up = Button(pygame.Rect(SCREEN_WIDTH // 2 + 200, 168, btn_vol_w, btn_vol_h), "▶", self.font_ui, on_click=lambda: self._adj_music(0.1))
        self.btn_sfx_down = Button(pygame.Rect(SCREEN_WIDTH // 2 + 100, 214, btn_vol_w, btn_vol_h), "◀", self.font_ui, on_click=lambda: self._adj_sfx(-0.1))
        self.btn_sfx_up = Button(pygame.Rect(SCREEN_WIDTH // 2 + 200, 214, btn_vol_w, btn_vol_h), "▶", self.font_ui, on_click=lambda: self._adj_sfx(0.1))
        self.option_vol_buttons = [self.btn_mus_down, self.btn_mus_up, self.btn_sfx_down, self.btn_sfx_up]

    def _adj_music(self, delta: float) -> None:
        self.sound_manager.set_music_volume(self.sound_manager.music_volume + delta)
        self.sound_manager.play_sfx("click")

    def _adj_sfx(self, delta: float) -> None:
        self.sound_manager.set_sfx_volume(self.sound_manager.sfx_volume + delta)
        self.sound_manager.play_sfx("click")

    def set_state(self, new_state: GameState) -> None:
        self.state = new_state
        self.targeting_mode = TargetingMode.NONE
        self.black_hole_target_enemy = None
        self._safe_set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        # Transición de música adaptativa
        if new_state in (GameState.MENU, GameState.OPTIONS, GameState.VICTORY_CINEMATIC):
            self.sound_manager.play_music("menu")
        elif new_state == GameState.PLAYING:
            self.sound_manager.play_music_for_level(self.level)

    def start_new_run(self) -> None:
        self.sound_manager.play_sfx("click")
        self.death_reason = ""
        self.level = 1
        self.power_manager.reset_run()
        self.start_level(self.level)

    def start_level(self, level: int) -> None:
        """Inicia el nivel dimensionando el mapa y generando los enemigos según las reglas."""
        self.level = level

        # Escalado dinámico cada 2 niveles hasta 8x8
        if level <= 2:
            board_size = 5
        elif level <= 4:
            board_size = 6
        elif level <= 6:
            board_size = 7
        else:
            board_size = 8

        self.board.set_dimensions(board_size, board_size)

        start_col = board_size // 2
        start_row = board_size - 1
        self.player = Player(col=start_col, row=start_row)

        # Generador de enemigos según las reglas (Nivel 11: Rey Gigante)
        self.enemies = spawn_enemies_for_level(level, self.board)

        self.allies.clear()
        self.trap_manager.reset()
        self.turn_manager.reset()
        self.power_manager.reset_level_charges()
        self.split_rows.clear()
        self.boss_phase_1_split = False
        self.boss_phase_2_split = False

        if level >= 11:
            self.status_message = "¡BATALLA FINAL: DERROTA AL REY TIRANO!"
        else:
            self.status_message = f"Nivel {level} ({board_size}x{board_size}): ¡Elimina a las piezas rivales!"

        self.set_state(GameState.PLAYING)
        self.sound_manager.play_music_for_level(level)

    # =========================================================================
    # MECÁNICAS DEL JEFE FINAL (DIVISIÓN DE TABLERO E INVOCACIONES)
    # =========================================================================

    def _check_boss_fissure_trigger(self, boss: EnemyPawn) -> None:
        """Divide el tablero en dos según la barra de vida del Rey Gigante (a 2/3 y a 1/3 de HP)."""
        if not boss.is_boss:
            return

        # 1. Primera división de tablero a 2/3 de HP (<= 8 de 12 HP)
        if boss.hp <= 8 and not self.boss_phase_1_split:
            self.boss_phase_1_split = True
            split_r = self.board.rows // 2 - 1  # Fila 3 en 8x8
            self._split_board_at_row(split_r)
            self.sound_manager.play_sfx("rift")
            self.status_message = "¡EL REY TIRANO HA FRACTURADO EL TABLERO EN DOS (Fase 1/2)!"

        # 2. Segunda división de tablero a 1/3 de HP (<= 4 de 12 HP)
        if boss.hp <= 4 and not self.boss_phase_2_split:
            self.boss_phase_2_split = True
            split_r = self.board.rows // 2 + 1  # Fila 5 en 8x8
            self._split_board_at_row(split_r)
            self.sound_manager.play_sfx("rift")
            self.status_message = "¡EL REY TIRANO HA DIVIDIDO EL TABLERO POR SEGUNDA VEZ (Fase 2/2)!"

    def _split_board_at_row(self, split_r: int) -> None:
        """Crea una falla de lava ardiente a través de una fila dejando 2 puentes transitables."""
        if split_r not in self.split_rows:
            self.split_rows.append(split_r)

        # Dejar siempre 2 casillas puente para que el jugador y piezas puedan cruzar estratégicamente
        bridge_cols = {2, 5} if self.board.cols >= 6 else {1, 3}
        fissure_tiles = []
        for c in range(self.board.cols):
            if c not in bridge_cols:
                fissure_tiles.append((c, split_r))

        if fissure_tiles:
            self.trap_manager.traps.append(
                Trap(
                    trap_type=TrapType.LAVA,
                    tiles=fissure_tiles,
                    duration_turns=999,
                    spawn_turn=self.turn_manager.turn_count,
                )
            )

        # Si el jugador estaba en una casilla fracturada, reubicarlo al puente más cercano para evitar muerte injusta
        if (self.player.col, self.player.row) in fissure_tiles:
            closest_bridge = min(bridge_cols, key=lambda bc: abs(bc - self.player.col))
            self.player.col = closest_bridge

    def _boss_spawn_pawns(self, boss: EnemyPawn) -> None:
        """El Rey convoca peones (uno con escudo) en casillas donde NO puedan comer al peón blanco."""
        occupied = {(e.col, e.row) for e in self.enemies if e.alive} | {(self.player.col, self.player.row)}
        candidate_tiles = []

        for r in range(0, min(self.board.rows - 2, 4)):
            for c in range(self.board.cols):
                if (c, r) in occupied or self.trap_manager.get_trap_at(c, r):
                    continue
                # REGLA: no pueden aparecer en una zona en la cual puedan comer al peón blanco
                # (ni diagonal inmediata ni adyacente que amenace instantáneamente)
                if abs(c - self.player.col) <= 1 and abs(r - self.player.row) <= 1:
                    continue
                candidate_tiles.append((c, r))

        if candidate_tiles:
            random.shuffle(candidate_tiles)
            spawn_count = min(2, len(candidate_tiles))
            for i in range(spawn_count):
                sc, sr = candidate_tiles[i]
                # El primer peón invocado cuenta con escudo rúnico
                has_sh = (i == 0)
                new_p = EnemyPawn(col=sc, row=sr, piece_role="pawn", has_shield=has_sh)
                self.enemies.append(new_p)

            self.sound_manager.play_sfx("summon")
            self.status_message = "¡El Rey Tirano ha invocado peones con escudo!"

    def _trigger_boss_victory(self) -> None:
        """Activa la cinemática final de victoria al derrotar al Rey."""
        self.sound_manager.play_music("menu")
        self.set_state(GameState.VICTORY_CINEMATIC)

    # =========================================================================
    # ENRUTAMIENTO DE EVENTOS
    # =========================================================================

    def handle_events(self) -> None:
        mouse_pos = pygame.mouse.get_pos()
        self.hovered_tile = self.board.pixel_to_tile(mouse_pos[0], mouse_pos[1])
        any_hover = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if self.state == GameState.MENU:
                for btn in self.menu_buttons:
                    btn.handle_event(event)

            elif self.state == GameState.PLAYING:
                self.in_game_menu_btn.handle_event(event)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.targeting_mode != TargetingMode.NONE:
                            self.targeting_mode = TargetingMode.NONE
                            self.black_hole_target_enemy = None
                            self.status_message = "Apuntado cancelado."
                            self.sound_manager.play_sfx("click")
                        else:
                            self.set_state(GameState.MENU)
                        return

                    # Teclas numéricas para hotbar (1, 2, 3...)
                    if event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                        num = event.key - pygame.K_0
                        chosen_power = self.power_manager.handle_hotkey(num)
                        if chosen_power:
                            self._set_targeting_for_power(chosen_power)
                            self.sound_manager.play_sfx("click")
                        else:
                            self.targeting_mode = TargetingMode.NONE
                            self.black_hole_target_enemy = None

                # Clic derecho: invocar caballo o cancelar apuntado
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                    if self.targeting_mode != TargetingMode.NONE:
                        self.targeting_mode = TargetingMode.NONE
                        self.black_hole_target_enemy = None
                        self.status_message = "Acción cancelada."
                        self.sound_manager.play_sfx("click")
                    elif self.power_manager.has_summon_knight:
                        if not any(a.alive for a in self.allies):
                            self.targeting_mode = TargetingMode.SUMMON_KNIGHT
                            self.status_message = "Clic izquierdo en una casilla detrás de tu Peón para colocar al Caballo."
                            self.sound_manager.play_sfx("click")
                        else:
                            self.status_message = "Tu Caballo aliado ya está combatiendo."

                # Clic izquierdo
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    hotbar_slots = self.power_manager.render_hotbar(self.screen)
                    slot_clicked = False
                    for s_rect, s_power in hotbar_slots:
                        if s_rect.collidepoint(event.pos):
                            if not s_power.used_in_level:
                                self._set_targeting_for_power(s_power)
                                self.sound_manager.play_sfx("click")
                            slot_clicked = True
                            break

                    if not slot_clicked and self.turn_manager.phase == TurnPhase.PLAYER:
                        if self.hovered_tile:
                            self._handle_board_left_click(self.hovered_tile)

            elif self.state == GameState.LEVEL_REWARD:
                selected_power = self.reward_screen.handle_event(event)
                if selected_power:
                    self.sound_manager.play_sfx("click")
                    self.power_manager.add_power(selected_power.id)
                    self.start_level(self.level + 1)

            elif self.state == GameState.OPTIONS:
                self.back_button.handle_event(event)
                for b in self.option_vol_buttons:
                    b.handle_event(event)

                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.set_state(GameState.MENU)
                    return

            elif self.state == GameState.GAME_OVER:
                for btn in self.game_over_buttons:
                    btn.handle_event(event)

            elif self.state == GameState.VICTORY_CINEMATIC:
                self.cinematic_scene.handle_event(event)

        # Hover
        if self.state == GameState.MENU:
            for btn in self.menu_buttons:
                btn.update(mouse_pos)
                if btn.is_hovered:
                    any_hover = True

        elif self.state == GameState.PLAYING:
            self.in_game_menu_btn.update(mouse_pos)
            if self.in_game_menu_btn.is_hovered:
                any_hover = True
            elif self.hovered_tile and self.turn_manager.phase == TurnPhase.PLAYER:
                if self.targeting_mode != TargetingMode.NONE:
                    any_hover = True
                else:
                    valid_moves = self.player.get_valid_moves(self.board, self.enemies, self.power_manager)
                    if self.hovered_tile in valid_moves:
                        any_hover = True

        elif self.state == GameState.OPTIONS:
            self.back_button.update(mouse_pos)
            for b in self.option_vol_buttons:
                b.update(mouse_pos)
                if b.is_hovered:
                    any_hover = True
            if self.back_button.is_hovered:
                any_hover = True

        elif self.state == GameState.GAME_OVER:
            for btn in self.game_over_buttons:
                btn.update(mouse_pos)
                if btn.is_hovered:
                    any_hover = True

        elif self.state == GameState.VICTORY_CINEMATIC:
            if self.cinematic_scene.menu_button.rect.collidepoint(mouse_pos):
                any_hover = True

        cursor = pygame.SYSTEM_CURSOR_HAND if any_hover else pygame.SYSTEM_CURSOR_ARROW
        self._safe_set_cursor(cursor)

    def _set_targeting_for_power(self, power: Power) -> None:
        """Activa el modo de objetivo para un poder activo."""
        if power.id == "black_hole":
            self.targeting_mode = TargetingMode.BLACK_HOLE
            self.black_hole_target_enemy = None
            self.status_message = "VÓRTICE: Clic en Peón/Caballo/Alfil para matar, o Torre/Reina/Rey para teletransportar."
        elif power.id == "fireball":
            self.targeting_mode = TargetingMode.FIREBALL
            self.status_message = "PIROCLASTO: Clic en el área 2x2 a bombardear (mueve piezas pesadas a casillas limítrofes)."
        elif power.id == "arrow":
            self.targeting_mode = TargetingMode.ARROW
            self.status_message = "FLECHA: Clic en un Peón o Caballo enemigo para eliminarlo."
        elif power.id == "place_trap":
            self.targeting_mode = TargetingMode.PLACE_TRAP
            self.status_message = f"ARTILUGIO TRAMPA [{power.name}]: Clic en cualquier casilla libre para desplegar una trampa al azar."

    def _handle_board_left_click(self, tile: tuple[int, int]) -> None:
        """Procesa un clic en el tablero según el modo actual."""
        tc, tr = tile

        # 1. Invocar Caballo aliado
        if self.targeting_mode == TargetingMode.SUMMON_KNIGHT:
            if tr >= self.player.row:
                is_occupied = (
                    (tc == self.player.col and tr == self.player.row)
                    or any(e.alive and e.col == tc and e.row == tr for e in self.enemies)
                )
                if not is_occupied:
                    self.allies.append(AllyKnight(col=tc, row=tr, duration_turns=15))
                    self.vfx_manager.spawn_summon(tc, tr)
                    cx, cy = self.board.get_tile_center(tc, tr)
                    self.vfx_manager.add_floating_text(cx, cy - 20, "¡INVOCACIÓN!", (120, 240, 255))
                    self.sound_manager.play_sfx("summon")
                    self.targeting_mode = TargetingMode.NONE
                    self.status_message = "¡Caballo aliado invocado! Luchará durante 15 turnos."
                    self.execute_turn_cycle(player_moved=False)
                    return
            self.status_message = "Coloca el Caballo en una casilla libre detrás o al nivel de tu Peón."
            return

        # 2. Agujero Negro (Fase 1: Seleccionar pieza objetivo)
        elif self.targeting_mode == TargetingMode.BLACK_HOLE:
            target = next((e for e in self.enemies if e.alive and e.col == tc and e.row == tr), None)
            if target:
                if target.piece_role in ("pawn", "knight", "bishop") and not target.is_boss:
                    target.alive = False
                    p = self.power_manager.get_power("black_hole")
                    if p:
                        p.used_in_level = True
                    self.vfx_manager.spawn_black_hole(tc, tr)
                    cx, cy = self.board.get_tile_center(tc, tr)
                    self.vfx_manager.add_floating_text(cx, cy - 20, "¡VÓRTICE ABISAL!", (190, 100, 255))
                    self.sound_manager.play_sfx("black_hole")
                    self.targeting_mode = TargetingMode.NONE
                    self.status_message = "¡El Vórtice Abisal ha tragado al enemigo!"
                    self._check_level_cleared_or_continue()
                    return
                elif target.piece_role in ("rook", "queen", "king"):
                    self.black_hole_target_enemy = target
                    self.targeting_mode = TargetingMode.BLACK_HOLE_TELEPORT
                    self.sound_manager.play_sfx("black_hole")
                    self.status_message = f"VÓRTICE: Selecciona una casilla libre en la mitad rival (filas superiores) para enviar a {target.piece_role.capitalize()}."
                    return

        # 2b. Agujero Negro (Fase 2: Teletransportar pieza mayor a la mitad rival)
        elif self.targeting_mode == TargetingMode.BLACK_HOLE_TELEPORT:
            half_boundary = max(1, self.board.rows // 2)
            if tr < half_boundary:
                is_occupied = (
                    (tc == self.player.col and tr == self.player.row)
                    or any(e.alive and e.col == tc and e.row == tr for e in self.enemies)
                    or any(a.alive and a.col == tc and a.row == tr for a in self.allies)
                )
                if not is_occupied and self.black_hole_target_enemy:
                    piece_name = self.black_hole_target_enemy.piece_role.capitalize()
                    self.black_hole_target_enemy.col = tc
                    self.black_hole_target_enemy.row = tr
                    self.black_hole_target_enemy.immobilized_turns = 1

                    # Si es el Rey Jefe, el vórtice le inflige 3 de daño
                    if self.black_hole_target_enemy.is_boss:
                        res = self.black_hole_target_enemy.hit_damage(3, self.board, self.player, self.enemies)
                        self.sound_manager.play_sfx("boss_hit")
                        if res == "boss_killed":
                            self._trigger_boss_victory()
                            return
                        self._check_boss_fissure_trigger(self.black_hole_target_enemy)

                    p = self.power_manager.get_power("black_hole")
                    if p:
                        p.used_in_level = True

                    self.sound_manager.play_sfx("black_hole")
                    self.black_hole_target_enemy._check_trap_trigger(tc, tr, self.trap_manager)

                    self.targeting_mode = TargetingMode.NONE
                    self.black_hole_target_enemy = None
                    self.status_message = f"¡{piece_name} teletransportado a la mitad rival del tablero!"
                    self.execute_turn_cycle(player_moved=False)
                    return
            self.status_message = f"Inválido: Debes seleccionar una casilla libre en la mitad rival (filas 0 a {half_boundary - 1})."
            return

        # 3. Bola de Fuego (Área 2x2: Mata piezas menores; a torres, rey y reina los mueve a casilla limítrofe)
        elif self.targeting_mode == TargetingMode.FIREBALL:
            fire_tiles = {(tc + dx, tr + dy) for dx in range(2) for dy in range(2)}
            killed = 0
            displaced = 0

            for enemy in list(self.enemies):
                if not enemy.alive or (enemy.col, enemy.row) not in fire_tiles:
                    continue

                if enemy.piece_role in ("pawn", "knight", "bishop") and not enemy.is_boss:
                    res = enemy.hit_damage(2, self.board, self.player, self.enemies)
                    if res == "shield_broken":
                        self.sound_manager.play_sfx("shield_break")
                    else:
                        killed += 1

                elif enemy.piece_role in ("rook", "queen", "king"):
                    # Si es el Rey Jefe, recibe daño
                    if enemy.is_boss:
                        res = enemy.hit_damage(2, self.board, self.player, self.enemies)
                        self.sound_manager.play_sfx("boss_hit")
                        if res == "boss_killed":
                            self._trigger_boss_victory()
                            return
                        self._check_boss_fissure_trigger(enemy)

                    # Buscar casilla limítrofe con la zona seleccionada de fuego
                    occupied_all = (
                        {(e.col, e.row) for e in self.enemies if e.alive and e != enemy}
                        | {(self.player.col, self.player.row)}
                        | {(a.col, a.row) for a in self.allies if a.alive}
                    )
                    border_candidates = []
                    for bc in range(tc - 1, tc + 3):
                        for br in range(tr - 1, tr + 3):
                            if (bc, br) in fire_tiles:
                                continue
                            if not self.board.is_within_bounds(bc, br):
                                continue
                            if (bc, br) not in occupied_all:
                                border_candidates.append((bc, br))

                    if border_candidates:
                        new_pos = random.choice(border_candidates)
                        enemy.col, enemy.row = new_pos
                        enemy._check_trap_trigger(new_pos[0], new_pos[1], self.trap_manager)
                        displaced += 1

            p = self.power_manager.get_power("fireball")
            if p:
                p.used_in_level = True
            self.vfx_manager.spawn_fireball(tc, tr)
            cx, cy = self.board.get_tile_center(tc, tr)
            self.vfx_manager.add_floating_text(cx, cy - 20, "¡PIROCLASTO!", (255, 140, 40))
            self.sound_manager.play_sfx("fireball")
            self.targeting_mode = TargetingMode.NONE
            self.status_message = f"¡Piroclasto de Magma impactó! {killed} eliminado(s), {displaced} pieza(s) desplazada(s)."
            self._check_level_cleared_or_continue()
            return

        # 4. Flecha Rúnica
        elif self.targeting_mode == TargetingMode.ARROW:
            target = next((e for e in self.enemies if e.alive and e.col == tc and e.row == tr), None)
            if target:
                if target.is_boss:
                    res = target.hit_damage(2, self.board, self.player, self.enemies)
                    self.sound_manager.play_sfx("boss_hit")
                    if res == "boss_killed":
                        self._trigger_boss_victory()
                        return
                    self._check_boss_fissure_trigger(target)
                elif target.piece_role in ("pawn", "knight"):
                    res = target.hit_damage(2, self.board, self.player, self.enemies)
                    if res == "shield_broken":
                        self.sound_manager.play_sfx("shield_break")

                p = self.power_manager.get_power("arrow")
                if p:
                    p.used_in_level = True
                self.vfx_manager.spawn_arrow(self.player.col, self.player.row, tc, tr)
                cx, cy = self.board.get_tile_center(tc, tr)
                self.vfx_manager.add_floating_text(cx, cy - 20, "¡FLECHA RÚNICA!", (100, 230, 255))
                self.sound_manager.play_sfx("arrow")
                self.targeting_mode = TargetingMode.NONE
                self.status_message = "¡Flecha certera disparada!"
                self._check_level_cleared_or_continue()
                return

        # 5. Desplegar Trampa al azar (según nivel I o II)
        elif self.targeting_mode == TargetingMode.PLACE_TRAP:
            if not self.trap_manager.get_trap_at(tc, tr):
                trap_power = self.power_manager.get_power("place_trap")
                tier = trap_power.tier if trap_power else 1

                if tier == 1:
                    chosen_type = random.choice([TrapType.BEAR_TRAP, TrapType.VINES, TrapType.LAVA])
                else:
                    chosen_type = random.choices(
                        [TrapType.LAVA, TrapType.BEAR_TRAP, TrapType.VINES],
                        weights=[60, 30, 10],
                        k=1,
                    )[0]

                new_trap = Trap(
                    trap_type=chosen_type,
                    tiles=[(tc, tr)],
                    duration_turns=15,
                    spawn_turn=self.turn_manager.turn_count,
                )
                self.trap_manager.traps.append(new_trap)

                if trap_power:
                    trap_power.used_in_level = True

                self.sound_manager.play_sfx("click")
                self.targeting_mode = TargetingMode.NONE
                self.status_message = f"¡Desplegaste una {new_trap.name} [Nivel {tier}] al azar!"
                return

        # 6. Movimiento y Ataque Táctico
        else:
            valid_moves = self.player.get_valid_moves(self.board, self.enemies, self.power_manager)
            if tile in valid_moves:
                enemy_at_tile = next((e for e in self.enemies if e.alive and e.col == tc and e.row == tr), None)
                if enemy_at_tile:
                    # Caso A: Peón con Escudo
                    if enemy_at_tile.has_shield:
                        enemy_at_tile.hit_damage(1, self.board, self.player, self.enemies)
                        self.vfx_manager.spawn_shield_break(enemy_at_tile.col, enemy_at_tile.row)
                        cx, cy = self.board.get_tile_center(enemy_at_tile.col, enemy_at_tile.row)
                        self.vfx_manager.add_floating_text(cx, cy - 20, "¡ESCUDO ROTO!", (140, 220, 255))
                        self.sound_manager.play_sfx("shield_break")
                        self.status_message = "¡Rompiste el escudo del peón! Ha retrocedido."
                        # Sólo avanzar si el peón liberó la casilla objetivo
                        if (enemy_at_tile.col, enemy_at_tile.row) != (tc, tr):
                            self.player.move_to(tc, tr)
                            if abs(enemy_at_tile.col - tc) <= 1 and abs(enemy_at_tile.row - tr) <= 1:
                                enemy_at_tile.immobilized_turns = 1
                        else:
                            enemy_at_tile.immobilized_turns = 1
                        self.execute_turn_cycle(player_moved=True)
                        return

                    # Caso B: Rey Gigante (Jefe Final)
                    elif enemy_at_tile.is_boss:
                        res = enemy_at_tile.hit_damage(3, self.board, self.player, self.enemies)
                        self.vfx_manager.spawn_slash(tc, tr, is_heavy=True)
                        self.vfx_manager.trigger_screen_shake(duration_ms=250, intensity=5.5)
                        cx, cy = self.board.get_tile_center(tc, tr)
                        self.vfx_manager.add_floating_text(cx, cy - 20, "-3 HP", (255, 80, 80))
                        self.sound_manager.play_sfx("boss_hit")
                        if res == "boss_killed":
                            self.player.move_to(tc, tr)
                            self._trigger_boss_victory()
                            return

                        self._check_boss_fissure_trigger(enemy_at_tile)

                        # --- RETROCESO Y REPELSIÓN DEL REY GIGANTE TRAS EL GOLPE ---
                        p_col, p_row = self.player.col, self.player.row
                        dc = tc - p_col
                        dr = tr - p_row
                        step_c = 1 if dc > 0 else (-1 if dc < 0 else 0)
                        step_r = 1 if dr > 0 else (-1 if dr < 0 else 0)

                        occupied = (
                            {(e.col, e.row) for e in self.enemies if e.alive and e != enemy_at_tile}
                            | {(p_col, p_row)}
                            | {(tc, tr)}
                        )

                        def is_valid_boss_dest(c: int, r: int) -> bool:
                            if not self.board.is_within_bounds(c, r):
                                return False
                            if (c, r) in occupied:
                                return False
                            trap = self.trap_manager.get_trap_at(c, r)
                            if trap and trap.trap_type == TrapType.LAVA:
                                return False
                            return True

                        boss_dest = None
                        direct_2 = (tc + step_c * 2, tr + step_r * 2)
                        direct_1 = (tc + step_c, tr + step_r)

                        # Priorizar retroceso a 2 casillas para un combate táctico justo
                        if is_valid_boss_dest(*direct_2):
                            boss_dest = direct_2
                        elif is_valid_boss_dest(*direct_1):
                            boss_dest = direct_1
                        else:
                            # Buscar casillas libres ordenadas por mayor distancia a la posición del jugador
                            cands = [
                                (c, r) for c in range(self.board.cols) for r in range(self.board.rows)
                                if is_valid_boss_dest(c, r)
                            ]
                            if cands:
                                cands.sort(key=lambda pos: max(abs(pos[0] - tc), abs(pos[1] - tr)), reverse=True)
                                boss_dest = cands[0]

                        if boss_dest:
                            enemy_at_tile.col, enemy_at_tile.row = boss_dest
                            enemy_at_tile._check_trap_trigger(boss_dest[0], boss_dest[1], self.trap_manager)
                            self.player.move_to(tc, tr)
                            # Si quedó a tiro inmediato (distancia <= 1), aturdirlo 1 turno para evitar muerte injusta instantánea
                            if max(abs(boss_dest[0] - tc), abs(boss_dest[1] - tr)) <= 1:
                                enemy_at_tile.immobilized_turns = 1
                                self.status_message = f"¡Golpeaste al Rey Tirano! Le quedan {enemy_at_tile.hp} HP. ¡Aturdido contra el obstáculo!"
                            else:
                                self.status_message = f"¡Golpeaste al Rey Tirano! Le quedan {enemy_at_tile.hp} HP. ¡Retrocedió bajo tu embestida!"
                        else:
                            # Si el jefe está completamente acorralado sin escape, el jugador golpea sin moverse y aturde 1 turno
                            enemy_at_tile.immobilized_turns = 1
                            self.status_message = f"¡Golpeaste al Rey Tirano! Le quedan {enemy_at_tile.hp} HP (está acorralado y aturdido)."

                        self.execute_turn_cycle(player_moved=True)
                        return

                    # Caso C: Pieza normal
                    else:
                        enemy_at_tile.alive = False
                        self.vfx_manager.spawn_slash(tc, tr, is_heavy=False)
                        self.sound_manager.play_sfx("capture")
                        if enemy_at_tile.piece_role == "pawn":
                            self.status_message = "¡Eliminaste a un peón enemigo con ataque de Rey!"
                        else:
                            self.status_message = f"¡Capturaste a un {enemy_at_tile.piece_role.capitalize()} enemigo!"
                else:
                    self.sound_manager.play_sfx("step")
                    self.status_message = "Avanzaste una casilla."

                self.player.move_to(tc, tr)

                # Comprobar trampa pisada por el jugador
                eff, turns, tname = self.trap_manager.trigger_trap_at(tc, tr, "player")
                if eff == "kill":
                    self.sound_manager.play_sfx("lava")
                    self.player.alive = False
                    self.death_reason = f"Charco de Lava ardiente ({tname})"
                    self.set_state(GameState.GAME_OVER)
                    return
                elif eff == "immobilize":
                    if "Oso" in tname:
                        self.sound_manager.play_sfx("bear_trap")
                    else:
                        self.sound_manager.play_sfx("step")
                    self.player.immobilized_turns = turns
                    self.status_message = f"¡Caíste en {tname}! Inmovilizado {turns} turno(s)."

                self._check_level_cleared_or_continue()

    def _check_level_cleared_or_continue(self) -> None:
        alive_enemies = [e for e in self.enemies if e.alive]
        if not alive_enemies:
            # Si era la batalla final contra el Rey (Nivel 11), victoria cinemática definitiva
            if self.level >= 11:
                self._trigger_boss_victory()
                return

            reward_options = self.power_manager.get_reward_options(3)
            self.reward_screen.set_options(reward_options, self.level)
            self.set_state(GameState.LEVEL_REWARD)
            return

        self.execute_turn_cycle(player_moved=True)

    def execute_turn_cycle(self, player_moved: bool) -> None:
        self.turn_manager.to_enemy_phase()

        # 1. Turno de los aliados (Caballo)
        for ally in self.allies:
            if ally.alive:
                occupied_allies = {(self.player.col, self.player.row)}
                act, _ = ally.take_turn(self.board, self.enemies, self.trap_manager, occupied_allies)
                if act == "attack":
                    self.sound_manager.play_sfx("capture")

        if not any(e.alive for e in self.enemies):
            if self.level >= 11:
                self._trigger_boss_victory()
                return
            reward_options = self.power_manager.get_reward_options(3)
            self.reward_screen.set_options(reward_options, self.level)
            self.set_state(GameState.LEVEL_REWARD)
            return

        # 2. Turno de los enemigos
        alive_enemies = [e for e in self.enemies if e.alive]
        for enemy in alive_enemies:
            action, dest = enemy.take_turn(self.board, self.player, self.enemies, self.trap_manager)
            if action == "attack":
                self.sound_manager.play_sfx("enemy_attack")
                self.player.alive = False
                if enemy.is_boss:
                    self.death_reason = "El Rey Gigante (Jefe Final)"
                elif enemy.piece_role == "queen":
                    self.death_reason = "La Reina Negra"
                elif enemy.piece_role == "rook":
                    self.death_reason = "Una Torre rival"
                elif enemy.piece_role == "bishop":
                    self.death_reason = "Un Alfil rival"
                elif enemy.piece_role == "knight":
                    self.death_reason = "Un Caballo rival"
                elif enemy.piece_role == "pawn":
                    if enemy.has_shield:
                        self.death_reason = "Un Peón rival con Escudo"
                    else:
                        self.death_reason = "Un Peón rival"
                else:
                    self.death_reason = f"{enemy.piece_role.capitalize()} rival"
                self.set_state(GameState.GAME_OVER)
                return

        # 3. Acciones especiales del Jefe Final (Rey Gigante)
        boss = next((e for e in self.enemies if e.alive and e.is_boss), None)
        if boss:
            # Plantar trampa cada 3 turnos
            if self.turn_manager.turn_count % 3 == 0:
                free_tiles = [
                    (c, r) for c in range(self.board.cols) for r in range(self.board.rows)
                    if (c, r) != (self.player.col, self.player.row)
                    and not any(e.alive and e.col == c and e.row == r for e in self.enemies)
                    and not self.trap_manager.get_trap_at(c, r)
                ]
                if free_tiles:
                    tc, tr = random.choice(free_tiles)
                    self.trap_manager.traps.append(
                        Trap(
                            trap_type=random.choice([TrapType.BEAR_TRAP, TrapType.LAVA]),
                            tiles=[(tc, tr)],
                            duration_turns=15,
                            spawn_turn=self.turn_manager.turn_count,
                        )
                    )

            # Invocar peones cada 4 turnos (con escudo)
            if self.turn_manager.turn_count % 4 == 0 and len([e for e in self.enemies if e.alive]) < 7:
                self._boss_spawn_pawns(boss)

        # 4. Regreso a fase del jugador
        self.turn_manager.to_player_phase()

        if self.player.immobilized_turns > 0 and player_moved:
            self.player.immobilized_turns -= 1

        # 5. Trampas ambientales cada 5 turnos
        forbidden = {(self.player.col, self.player.row)}
        new_trap = self.trap_manager.check_turn_start_spawn(
            current_turn=self.turn_manager.turn_count,
            board=self.board,
            level=self.level,
            forbidden_tiles=forbidden,
        )
        if new_trap:
            if new_trap.trap_type == TrapType.LAVA:
                self.sound_manager.play_sfx("lava")
            elif new_trap.trap_type == TrapType.BEAR_TRAP:
                self.sound_manager.play_sfx("bear_trap")
            self.status_message = f"¡Peligro! Ha aparecido una {new_trap.name} en el tablero."

    def update(self) -> None:
        dt_ms = self.clock.get_time()
        if self.state == GameState.MENU:
            self.menu_bg.update()
        elif self.state == GameState.PLAYING:
            self.vfx_manager.update(dt_ms, self.board)
        elif self.state == GameState.VICTORY_CINEMATIC:
            self.cinematic_scene.update()

    # =========================================================================
    # RENDERIZADO
    # =========================================================================

    def render(self) -> None:
        self.screen.fill(COLOR_BG)
        time_ms = pygame.time.get_ticks()

        if self.state == GameState.MENU:
            self.render_menu()
        elif self.state == GameState.PLAYING:
            self.render_playing(time_ms)
        elif self.state == GameState.LEVEL_REWARD:
            self.reward_screen.render(self.screen)
        elif self.state == GameState.OPTIONS:
            self.render_options()
        elif self.state == GameState.GAME_OVER:
            self.render_game_over(time_ms)
        elif self.state == GameState.VICTORY_CINEMATIC:
            self.cinematic_scene.render(self.screen)

        pygame.display.flip()

    def render_menu(self) -> None:
        self.menu_bg.render(self.screen)

        title_surf = self.font_logo.render("EL ÚLTIMO PEÓN", True, COLOR_ACCENT)
        self.screen.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH // 2, 90)))

        sub_surf = self.font_ui.render("Incursión Táctica en Pixel Art • Piedra y Madera", True, COLOR_TEXT_MAIN)
        self.screen.blit(sub_surf, sub_surf.get_rect(center=(SCREEN_WIDTH // 2, 135)))

        for btn in self.menu_buttons:
            btn.render(self.screen)

        v_surf = self.font_small.render("v0.7.0 • Jefe Final Rey Gigante • Cinemática de Victoria", True, COLOR_TEXT_MUTED)
        self.screen.blit(v_surf, (SCREEN_WIDTH // 2 - v_surf.get_width() // 2, SCREEN_HEIGHT - 28))

    def render_playing(self, time_ms: int) -> None:
        # 1. Sacudida de pantalla sísmica si hay impacto activo
        shake_x, shake_y = self.vfx_manager.get_shake_offset()
        if shake_x != 0 or shake_y != 0:
            self.board.offset_x += shake_x
            self.board.offset_y += shake_y

        self.board.render(self.screen, time_ms=time_ms)
        self.trap_manager.render(self.screen, self.board, time_ms=time_ms)

        # Dibujar fracturas de tablero en batalla contra el Rey
        if self.split_rows:
            draw_board_fissure(self.screen, self.board, self.split_rows, time_ms=time_ms)

        if self.turn_manager.phase == TurnPhase.PLAYER and self.player.alive:
            if self.targeting_mode == TargetingMode.NONE:
                valid_moves = self.player.get_valid_moves(self.board, self.enemies, self.power_manager)
                self._render_valid_moves_highlight(valid_moves)
            elif self.targeting_mode == TargetingMode.SUMMON_KNIGHT:
                self._render_summon_highlight()
            elif self.targeting_mode == TargetingMode.BLACK_HOLE_TELEPORT:
                self._render_teleport_highlight()
            elif self.targeting_mode == TargetingMode.FIREBALL and self.hovered_tile:
                self._render_fireball_highlight(self.hovered_tile)

        for enemy in self.enemies:
            if enemy.alive:
                is_hov = self.hovered_tile == (enemy.col, enemy.row)
                enemy.render(self.screen, self.board, is_hovered=is_hov)

        for ally in self.allies:
            if ally.alive:
                is_hov = self.hovered_tile == (ally.col, ally.row)
                ally.render(self.screen, self.board, is_hovered=is_hov)

        is_p_hov = self.hovered_tile == (self.player.col, self.player.row)
        self.player.render(self.screen, self.board, is_hovered=is_p_hov)

        # Efectos visuales de poderes (Piroclasto, Vórtice, Flecha, Invocación, Chispas)
        self.vfx_manager.render(self.screen, self.board)

        # Restaurar offset de tablero tras sacudida
        if shake_x != 0 or shake_y != 0:
            self.board.offset_x -= shake_x
            self.board.offset_y -= shake_y

        self.in_game_menu_btn.render(self.screen)

        # Panel de inspección rúnico a la izquierda del tablero (describe lo que está bajo el cursor)
        valid_moves_for_inspect = (
            self.player.get_valid_moves(self.board, self.enemies, self.power_manager)
            if (self.turn_manager.phase == TurnPhase.PLAYER and self.player.alive)
            else []
        )
        self.inspector.render(
            surface=self.screen,
            board=self.board,
            player=self.player,
            enemies=self.enemies,
            allies=self.allies,
            trap_manager=self.trap_manager,
            split_rows=self.split_rows,
            valid_moves=valid_moves_for_inspect,
            hovered_tile=self.hovered_tile,
            power_manager=self.power_manager,
        )

        # Si el jefe está presente, renderizar su barra de vida monumental arriba
        boss = next((e for e in self.enemies if e.alive and e.is_boss), None)
        if boss:
            draw_boss_health_bar(self.screen, boss.hp, boss.max_hp, name="EL REY TIRANO • JEFE FINAL")
        else:
            alive_count = sum(1 for e in self.enemies if e.alive)
            badge_w, badge_h = 160, 38
            badge_x = SCREEN_WIDTH - badge_w - 24
            badge_y = 16
            badge_rect = pygame.Rect(badge_x, badge_y, badge_w, badge_h)
            pygame.draw.rect(self.screen, COLOR_PANEL, badge_rect, border_radius=6)
            pygame.draw.rect(self.screen, COLOR_BORDER, badge_rect, width=1, border_radius=6)
            enemy_lbl = self.font_small.render(f"ENEMIGOS: {alive_count}", True, COLOR_ACCENT)
            self.screen.blit(enemy_lbl, enemy_lbl.get_rect(center=badge_rect.center))

            lvl_rect = pygame.Rect(badge_x - 170, badge_y, 155, badge_h)
            pygame.draw.rect(self.screen, COLOR_PANEL, lvl_rect, border_radius=6)
            pygame.draw.rect(self.screen, COLOR_BORDER, lvl_rect, width=1, border_radius=6)
            lvl_lbl = self.font_small.render(f"NIVEL {self.level} • TURNO {self.turn_manager.turn_count}", True, COLOR_TEXT_MAIN)
            self.screen.blit(lvl_lbl, lvl_lbl.get_rect(center=lvl_rect.center))

        self.power_manager.render_hotbar(self.screen)

        status_surf = self.font_small.render(self.status_message, True, COLOR_TEXT_MAIN)
        self.screen.blit(status_surf, status_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20)))

    def _render_valid_moves_highlight(self, valid_moves: list[tuple[int, int]]) -> None:
        enemy_positions = {(e.col, e.row) for e in self.enemies if e.alive}
        tile_size = self.board.tile_size

        for col, row in valid_moves:
            tx, ty = self.board.tile_to_pixel(col, row)
            is_enemy_tile = (col, row) in enemy_positions
            is_hover = (col, row) == self.hovered_tile

            overlay = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
            fill_col = COLOR_VALID_MOVE_HOVER if is_hover else (COLOR_ATTACK_MOVE if is_enemy_tile else COLOR_VALID_MOVE)
            overlay.fill(fill_col)
            pygame.draw.rect(overlay, COLOR_VALID_BORDER, (0, 0, tile_size, tile_size), 2)

            if is_enemy_tile:
                margin = int(tile_size * 0.22)
                pygame.draw.line(overlay, (255, 255, 255, 240), (margin, margin), (tile_size - margin, tile_size - margin), 3)
                pygame.draw.line(overlay, (255, 255, 255, 240), (tile_size - margin, margin), (margin, tile_size - margin), 3)
            else:
                pygame.draw.circle(overlay, (255, 130, 130, 200), (tile_size // 2, tile_size // 2), 5)

            self.screen.blit(overlay, (tx, ty))

    def _render_summon_highlight(self) -> None:
        tile_size = self.board.tile_size
        occupied = {(e.col, e.row) for e in self.enemies if e.alive} | {(self.player.col, self.player.row)}

        for r in range(self.player.row, self.board.rows):
            for c in range(self.board.cols):
                if (c, r) not in occupied:
                    tx, ty = self.board.tile_to_pixel(c, r)
                    overlay = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
                    overlay.fill((80, 200, 255, 95))
                    pygame.draw.rect(overlay, (120, 230, 255), (0, 0, tile_size, tile_size), 2)
                    self.screen.blit(overlay, (tx, ty))

    def _render_teleport_highlight(self) -> None:
        tile_size = self.board.tile_size
        half_boundary = max(1, self.board.rows // 2)
        occupied = (
            {(e.col, e.row) for e in self.enemies if e.alive}
            | {(self.player.col, self.player.row)}
            | {(a.col, a.row) for a in self.allies if a.alive}
        )

        for r in range(half_boundary):
            for c in range(self.board.cols):
                tx, ty = self.board.tile_to_pixel(c, r)
                overlay = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
                if (c, r) not in occupied:
                    overlay.fill((160, 80, 255, 110))
                    pygame.draw.rect(overlay, (210, 140, 255), (0, 0, tile_size, tile_size), 2)
                else:
                    overlay.fill((80, 40, 110, 60))
                self.screen.blit(overlay, (tx, ty))

    def _render_fireball_highlight(self, center_tile: tuple[int, int]) -> None:
        c, r = center_tile
        tile_size = self.board.tile_size
        for dx in range(2):
            for dy in range(2):
                tc, tr = c + dx, r + dy
                if self.board.is_within_bounds(tc, tr):
                    tx, ty = self.board.tile_to_pixel(tc, tr)
                    overlay = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
                    overlay.fill((255, 90, 30, 140))
                    pygame.draw.rect(overlay, (255, 200, 40), (0, 0, tile_size, tile_size), 2)
                    self.screen.blit(overlay, (tx, ty))

    def render_game_over(self, time_ms: int) -> None:
        self.render_playing(time_ms)

        dim_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dim_surf.fill((18, 10, 14, 225))
        self.screen.blit(dim_surf, (0, 0))

        panel_w, panel_h = 480, 390
        panel_rect = pygame.Rect((SCREEN_WIDTH - panel_w) // 2, 70, panel_w, panel_h)
        pygame.draw.rect(self.screen, COLOR_PANEL, panel_rect, border_radius=12)
        pygame.draw.rect(self.screen, (220, 45, 45), panel_rect, 2, border_radius=12)

        title_surf = self.font_logo.render("DERROTA", True, (240, 50, 50))
        self.screen.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH // 2, 120)))

        sub_surf = self.font_title.render("EL PEÓN BLANCO HA CAÍDO", True, COLOR_TEXT_MAIN)
        self.screen.blit(sub_surf, sub_surf.get_rect(center=(SCREEN_WIDTH // 2, 168)))

        # Placa destacada: Quién te mató
        killer_text = f"Te mató: {self.death_reason}" if self.death_reason else "Causa de muerte desconocida"
        killer_surf = self.font_ui.render(killer_text, True, (255, 130, 130))
        killer_rect = killer_surf.get_rect(center=(SCREEN_WIDTH // 2, 215))
        badge_rect = killer_rect.inflate(30, 14)
        pygame.draw.rect(self.screen, (45, 14, 18), badge_rect, border_radius=8)
        pygame.draw.rect(self.screen, (200, 45, 45), badge_rect, 1, border_radius=8)
        self.screen.blit(killer_surf, killer_rect)

        msg_surf = self.font_small.render(
            f"Llegaste hasta el Nivel {self.level} tras {self.turn_manager.turn_count} turnos.",
            True,
            COLOR_TEXT_MUTED,
        )
        self.screen.blit(msg_surf, msg_surf.get_rect(center=(SCREEN_WIDTH // 2, 260)))

        for btn in self.game_over_buttons:
            btn.render(self.screen)

    def render_options(self) -> None:
        """Pantalla de opciones con controles interactivos de volumen en tiempo real."""
        title_surf = self.font_title.render("OPCIONES Y AJUSTES DE AUDIO", True, COLOR_TEXT_MAIN)
        self.screen.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH // 2, 70)))

        panel_w, panel_h = 580, 350
        panel_rect = pygame.Rect((SCREEN_WIDTH - panel_w) // 2, 120, panel_w, panel_h)
        pygame.draw.rect(self.screen, COLOR_PANEL, panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, COLOR_BORDER, panel_rect, width=1, border_radius=10)

        lbl_mus = self.font_ui.render("Volumen Música:", True, COLOR_TEXT_MAIN)
        self.screen.blit(lbl_mus, (panel_rect.x + 35, 175))
        pct_mus = int(self.sound_manager.music_volume * 100)
        val_mus = self.font_ui.render(f"{pct_mus}%", True, COLOR_ACCENT)
        self.screen.blit(val_mus, val_mus.get_rect(center=(SCREEN_WIDTH // 2 + 172, 185)))

        lbl_sfx = self.font_ui.render("Volumen Efectos (SFX):", True, COLOR_TEXT_MAIN)
        self.screen.blit(lbl_sfx, (panel_rect.x + 35, 222))
        pct_sfx = int(self.sound_manager.sfx_volume * 100)
        val_sfx = self.font_ui.render(f"{pct_sfx}%", True, COLOR_ACCENT)
        self.screen.blit(val_sfx, val_sfx.get_rect(center=(SCREEN_WIDTH // 2 + 172, 230)))

        for b in self.option_vol_buttons:
            b.render(self.screen)

        controls = [
            ("Combate", "Mata peones como Rey; resto solo en diagonal"),
            ("Invocar Caballo", "Clic derecho (detrás de tu Peón)"),
            ("Habilidades Activas", "Teclas [ 1, 2, 3... ] o clic en hotbar"),
            ("Cancelar Apuntado", "[ Clic Derecho ] o [ ESC ]"),
        ]

        curr_y = 265
        for label, val in controls:
            lbl_surf = self.font_small.render(label, True, COLOR_TEXT_MUTED)
            self.screen.blit(lbl_surf, (panel_rect.x + 35, curr_y))
            val_surf = self.font_small.render(val, True, COLOR_TEXT_MAIN)
            val_rect = val_surf.get_rect(right=panel_rect.right - 35, centery=curr_y + 8)
            self.screen.blit(val_surf, val_rect)
            curr_y += 24

        self.back_button.render(self.screen)

    def run(self) -> None:
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)

        self.sound_manager.stop_music()
        pygame.quit()
