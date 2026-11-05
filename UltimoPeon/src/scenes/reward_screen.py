"""Pantalla de selección de recompensas entre niveles (Estilo Hades / 3 Tablillas de Madera)."""
import pygame
from src.config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_WOOD_DARK,
    COLOR_WOOD_BARK,
    COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED,
    COLOR_ACCENT,
    COLOR_RARITY_1,
    COLOR_RARITY_2,
    COLOR_RARITY_3,
)
from src.powers.power import Power
from src.graphics.pixel_art import draw_power_icon, draw_pixel_hatching


class RewardScreen:
    """Gestiona la elección entre 3 tablillas de madera talladas con poderes."""

    def __init__(self):
        self.font_title = pygame.font.SysFont("georgia", 26, bold=True)
        self.font_name = pygame.font.SysFont("georgia", 18, bold=True)
        self.font_rarity = pygame.font.SysFont("arial", 12, bold=True)
        self.font_desc = pygame.font.SysFont("arial", 13)

        self.options: list[Power] = []
        self.hovered_index: int = -1
        self.level_completed: int = 1

    def set_options(self, options: list[Power], level: int) -> None:
        """Establece las 3 opciones de bendición disponibles para este nivel."""
        self.options = options
        self.hovered_index = -1
        self.level_completed = level

    def get_plank_rects(self) -> list[pygame.Rect]:
        """Calcula las posiciones de las 3 tablas de madera en pantalla."""
        plank_w = 216
        plank_h = 320
        gap = 24
        total_w = len(self.options) * plank_w + (len(self.options) - 1) * gap
        start_x = (SCREEN_WIDTH - total_w) // 2
        start_y = 150

        rects = []
        for i in range(len(self.options)):
            rects.append(pygame.Rect(start_x + i * (plank_w + gap), start_y, plank_w, plank_h))
        return rects

    def handle_event(self, event: pygame.event.Event) -> Power | None:
        """Procesa eventos de ratón. Retorna el poder seleccionado o None."""
        rects = self.get_plank_rects()
        mouse_pos = pygame.mouse.get_pos()

        # Actualizar índice en hover
        self.hovered_index = -1
        for i, r in enumerate(rects):
            if r.collidepoint(mouse_pos):
                self.hovered_index = i
                break

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if 0 <= self.hovered_index < len(self.options):
                return self.options[self.hovered_index]

        return None

    def render(self, surface: pygame.Surface) -> None:
        """Dibuja el fondo de recompensa y las 3 tablas de madera tallada."""
        # Cortina oscura transparente
        dim_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dim_surf.fill((14, 12, 18, 220))
        surface.blit(dim_surf, (0, 0))

        # Título del Altar de Bendiciones
        title_surf = self.font_title.render(f"¡NIVEL {self.level_completed} SUPERADO!", True, COLOR_ACCENT)
        surface.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH // 2, 75)))

        sub_surf = self.font_desc.render(
            "Elige una bendición tallada para fortalecer tu incursión.",
            True,
            COLOR_TEXT_MAIN,
        )
        surface.blit(sub_surf, sub_surf.get_rect(center=(SCREEN_WIDTH // 2, 110)))

        # Dibujar las 3 tablas de madera
        rects = self.get_plank_rects()
        for i, (power, rect) in enumerate(zip(self.options, rects)):
            is_hov = (i == self.hovered_index)
            self._render_wooden_plank(surface, power, rect, is_hov)

    def _render_wooden_plank(
        self,
        surface: pygame.Surface,
        power: Power,
        rect: pygame.Rect,
        is_hovered: bool,
    ) -> None:
        """Renderiza una tablilla de madera tallada individual con su rareza, icono y descripción."""
        draw_rect = rect.copy()
        if is_hovered:
            draw_rect.y -= 8  # Elevación táctil al pasar el ratón

        # Sombra de la tabla en el suelo
        shadow_rect = pygame.Rect(draw_rect.x + 6, draw_rect.y + 10, draw_rect.width, draw_rect.height)
        pygame.draw.rect(surface, (0, 0, 0, 110), shadow_rect, border_radius=10)

        # 1. Base de madera oscura tallada
        pygame.draw.rect(surface, COLOR_WOOD_DARK, draw_rect, border_radius=10)

        # Vetas de madera en pixel art
        veta_area = pygame.Rect(draw_rect.x + 8, draw_rect.y + 8, draw_rect.width - 16, draw_rect.height - 16)
        draw_pixel_hatching(surface, veta_area, (110, 78, 50), spacing=5, cross=False)

        # Borde de corteza de madera / marco exterior
        border_col = COLOR_ACCENT if is_hovered else COLOR_WOOD_BARK
        border_w = 3 if is_hovered else 2
        pygame.draw.rect(surface, border_col, draw_rect, width=border_w, border_radius=10)

        # 2. Encabezado de RAREZA
        rarity_colors = {1: COLOR_RARITY_1, 2: COLOR_RARITY_2, 3: COLOR_RARITY_3}
        rarity_names = {1: "RAREZA 1 • COMÚN", 2: "RAREZA 2 • RARO", 3: "RAREZA 3 • MÍTICO"}
        r_col = rarity_colors.get(power.rarity, COLOR_RARITY_1)
        r_txt = rarity_names.get(power.rarity, "COMÚN")

        # Insignia de rareza
        badge_rect = pygame.Rect(draw_rect.centerx - 70, draw_rect.y + 14, 140, 22)
        pygame.draw.rect(surface, (20, 18, 25), badge_rect, border_radius=5)
        pygame.draw.rect(surface, r_col, badge_rect, width=1, border_radius=5)
        badge_surf = self.font_rarity.render(r_txt, True, r_col)
        surface.blit(badge_surf, badge_surf.get_rect(center=badge_rect.center))

        # 3. Marco e Icono del Poder
        icon_box = pygame.Rect(draw_rect.centerx - 30, draw_rect.y + 48, 60, 60)
        pygame.draw.rect(surface, (25, 22, 30), icon_box, border_radius=8)
        pygame.draw.rect(surface, r_col, icon_box, width=1, border_radius=8)
        draw_power_icon(surface, power.icon_id, icon_box.centerx, icon_box.centery, size=44)

        # 4. Nombre del Poder
        name_surf = self.font_name.render(power.name, True, COLOR_TEXT_MAIN)
        surface.blit(name_surf, name_surf.get_rect(center=(draw_rect.centerx, draw_rect.y + 128)))

        # Separador rúnico
        sep_y = draw_rect.y + 148
        pygame.draw.line(surface, r_col, (draw_rect.x + 24, sep_y), (draw_rect.right - 24, sep_y), 1)

        # 5. Descripción dividida en varias líneas legibles
        words = power.description.split(" ")
        lines = []
        curr_line = ""
        for w in words:
            test_line = f"{curr_line} {w}".strip()
            if len(test_line) <= 24:
                curr_line = test_line
            else:
                lines.append(curr_line)
                curr_line = w
        if curr_line:
            lines.append(curr_line)

        start_text_y = draw_rect.y + 162
        for line_str in lines:
            line_surf = self.font_desc.render(line_str, True, COLOR_TEXT_MAIN if is_hovered else COLOR_TEXT_MUTED)
            surface.blit(line_surf, line_surf.get_rect(center=(draw_rect.centerx, start_text_y)))
            start_text_y += 18

        # 6. Indicador de clic al pie
        click_prompt = "[ HAZ CLIC PARA ELEGIR ]" if is_hovered else "Elegir"
        click_col = COLOR_ACCENT if is_hovered else (150, 140, 130)
        prompt_surf = self.font_rarity.render(click_prompt, True, click_col)
        surface.blit(prompt_surf, prompt_surf.get_rect(center=(draw_rect.centerx, draw_rect.bottom - 22)))
