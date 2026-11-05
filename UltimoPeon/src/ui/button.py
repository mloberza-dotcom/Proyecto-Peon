"""Componente visual interactivo de botón para la interfaz de usuario."""
from typing import Callable, Optional
import pygame
from src.config import (
    COLOR_BTN_DEFAULT,
    COLOR_BTN_HOVER,
    COLOR_BTN_BORDER,
    COLOR_BTN_BORDER_HOVER,
    COLOR_TEXT_MAIN,
    COLOR_ACCENT,
)


class Button:
    """Botón con detección de cursor (hover), estilo táctico y respuesta a clics."""

    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        font: pygame.font.Font,
        on_click: Optional[Callable[[], None]] = None,
        border_radius: int = 8,
    ):
        self.rect = rect
        self.text = text
        self.font = font
        self.on_click = on_click
        self.border_radius = border_radius

        self.is_hovered: bool = False
        self.is_pressed: bool = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Procesa eventos de ratón.
        Retorna True si el botón fue clickeado con el botón izquierdo.
        """
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_pressed = True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_pressed and self.rect.collidepoint(event.pos):
                self.is_pressed = False
                if self.on_click:
                    self.on_click()
                return True
            self.is_pressed = False

        return False

    def update(self, mouse_pos: tuple[int, int]) -> None:
        """Actualiza el estado de hover según la posición actual del cursor."""
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def render(self, surface: pygame.Surface) -> None:
        """Dibuja el botón con animación de hover y borde iluminado."""
        bg_color = COLOR_BTN_HOVER if self.is_hovered else COLOR_BTN_DEFAULT
        border_color = COLOR_BTN_BORDER_HOVER if self.is_hovered else COLOR_BTN_BORDER
        text_color = COLOR_ACCENT if self.is_hovered else COLOR_TEXT_MAIN

        # Si está presionado, desplazamos ligeramente hacia abajo para efecto táctil
        draw_rect = self.rect.copy()
        if self.is_pressed:
            draw_rect.y += 2

        # Fondo del botón
        pygame.draw.rect(surface, bg_color, draw_rect, border_radius=self.border_radius)

        # Borde
        border_width = 2 if self.is_hovered else 1
        pygame.draw.rect(surface, border_color, draw_rect, width=border_width, border_radius=self.border_radius)

        # Texto centrado
        text_surf = self.font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=draw_rect.center)
        surface.blit(text_surf, text_rect)
