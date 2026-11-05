"""Gestor de inventario de poderes, mejoras progresivas y barra de habilidades activas."""
import copy
import random
import pygame
from src.config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_PANEL,
    COLOR_BORDER,
    COLOR_ACCENT,
)
from src.powers.power import Power, PowerType, ALL_POWERS
from src.graphics.pixel_art import draw_power_icon


class PowerManager:
    """Administra las mejoras activas y pasivas del jugador y su árbol de subida de nivel."""

    def __init__(self):
        self.acquired_powers: list[Power] = []
        self.active_powers: list[Power] = []
        self.selected_active_power: Power | None = None
        self.font_hotkey = pygame.font.SysFont("arial", 13, bold=True)

    def reset_run(self) -> None:
        """Reinicia los poderes al comenzar una nueva incursión."""
        self.acquired_powers.clear()
        self.active_powers.clear()
        self.selected_active_power = None

    def reset_level_charges(self) -> None:
        """Restaura los usos de habilidades activas (1 uso por nivel)."""
        for p in self.active_powers:
            p.used_in_level = False
        self.selected_active_power = None

    def add_power(self, power_id: str) -> Power:
        """Añade o mejora un poder existente en el inventario."""
        # Comprobar si ya existe y es mejorable (ej. place_trap)
        existing = next((p for p in self.acquired_powers if p.id == power_id), None)
        if existing and existing.tier < existing.max_tier:
            existing.tier += 1
            if existing.id == "place_trap" and existing.tier == 2:
                existing.name = "Artilugio Trampa [II]"
                existing.description = "1 uso/nivel: Despliega una trampa al azar con alta probabilidad de Lava (60%) o Trampa de Oso (30%). Nivel II."
            return existing

        # Si no lo tiene, lo añade como nuevo poder
        power_template = ALL_POWERS[power_id]
        power = copy.deepcopy(power_template)
        self.acquired_powers.append(power)

        if power.power_type == PowerType.ACTIVE and power.id != "summon_knight":
            next_num = len(self.active_powers) + 1
            power.hotkey_num = next_num
            self.active_powers.append(power)

        return power

    def get_reward_options(self, count: int = 3) -> list[Power]:
        """
        Genera 3 opciones aleatorias entre los poderes que el jugador aún no posee
        o mejoras de nivel para poderes mejorables que ya posea (ej. Artilugio Trampa [II]).
        """
        options: list[Power] = []

        # 1. Comprobar si califica para mejoras de nivel (Tier II)
        trap_power = next((p for p in self.acquired_powers if p.id == "place_trap"), None)
        can_upgrade_trap = trap_power and trap_power.tier < trap_power.max_tier

        # Poderes no adquiridos aún
        owned_ids = {p.id for p in self.acquired_powers}
        available_ids = [pid for pid in ALL_POWERS if pid not in owned_ids]

        # Si se puede mejorar la trampa a nivel 2, la agregamos como opción de mejora
        if can_upgrade_trap:
            upgrade_trap = copy.deepcopy(trap_power)
            upgrade_trap.tier = 2
            upgrade_trap.name = "Artilugio Trampa [II]"
            upgrade_trap.description = "1 uso/nivel: Despliega una trampa con alta probabilidad de Lava (60%) o Trampa de Oso (30%). Nivel II."
            options.append(upgrade_trap)

        # Rellenar con poderes aún no adquiridos
        sample_pool = [pid for pid in available_ids if not (can_upgrade_trap and pid == "place_trap")]
        needed = count - len(options)

        if len(sample_pool) >= needed:
            chosen_ids = random.sample(sample_pool, needed)
            for cid in chosen_ids:
                options.append(copy.deepcopy(ALL_POWERS[cid]))
        else:
            for cid in sample_pool:
                options.append(copy.deepcopy(ALL_POWERS[cid]))
            # Si no quedan suficientes poderes únicos, permitir pasivos
            while len(options) < count:
                options.append(copy.deepcopy(ALL_POWERS["range_kill"]))

        return options[:count]

    # Consultas de poderes pasivos
    def has_power(self, power_id: str) -> bool:
        return any(p.id == power_id for p in self.acquired_powers)

    def get_power(self, power_id: str) -> Power | None:
        return next((p for p in self.acquired_powers if p.id == power_id), None)

    @property
    def has_range_kill(self) -> bool:
        return self.has_power("range_kill")

    @property
    def has_range_move(self) -> bool:
        return self.has_power("range_move")

    @property
    def has_kill_rook(self) -> bool:
        return self.has_power("kill_rook")

    @property
    def has_kill_bishop(self) -> bool:
        return self.has_power("kill_bishop")

    @property
    def has_summon_knight(self) -> bool:
        return self.has_power("summon_knight")

    def handle_hotkey(self, key_num: int) -> Power | None:
        """Activa o desactiva el apuntado de una habilidad activa según su número asignado."""
        for p in self.active_powers:
            if p.hotkey_num == key_num and not p.used_in_level:
                if self.selected_active_power == p:
                    self.selected_active_power = None
                else:
                    self.selected_active_power = p
                return self.selected_active_power
        return None

    def render_hotbar(self, surface: pygame.Surface) -> list[tuple[pygame.Rect, Power]]:
        """Dibuja los cuadritos de poderes activos abajo a la derecha de la pantalla."""
        clickable_slots: list[tuple[pygame.Rect, Power]] = []
        if not self.active_powers:
            return clickable_slots

        slot_size = 48
        gap = 10
        total_w = len(self.active_powers) * (slot_size + gap) - gap
        start_x = SCREEN_WIDTH - total_w - 24
        start_y = SCREEN_HEIGHT - slot_size - 18

        for i, power in enumerate(self.active_powers):
            sx = start_x + i * (slot_size + gap)
            slot_rect = pygame.Rect(sx, start_y, slot_size, slot_size)
            clickable_slots.append((slot_rect, power))

            is_selected = self.selected_active_power == power
            bg_col = (50, 55, 70) if is_selected else COLOR_PANEL
            border_col = COLOR_ACCENT if is_selected else COLOR_BORDER

            pygame.draw.rect(surface, bg_col, slot_rect, border_radius=6)
            pygame.draw.rect(surface, border_col, slot_rect, width=2 if is_selected else 1, border_radius=6)

            cx, cy = slot_rect.center
            draw_power_icon(surface, power.icon_id, cx, cy - 2, size=32)

            # Si el poder es de nivel 2 (ej. Artilugio Trampa II), mostrar insignia II
            if power.tier > 1:
                tier_badge = self.font_hotkey.render("II", True, (255, 215, 60))
                surface.blit(tier_badge, (sx + slot_size - 14, start_y + 3))

            if power.used_in_level:
                dim_surf = pygame.Surface((slot_size, slot_size), pygame.SRCALPHA)
                dim_surf.fill((10, 10, 15, 175))
                surface.blit(dim_surf, (sx, start_y))

            num_surf = self.font_hotkey.render(str(power.hotkey_num), True, COLOR_ACCENT)
            surface.blit(num_surf, (sx + 5, start_y + slot_size - 16))

        return clickable_slots
