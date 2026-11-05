"""Configuración global, constantes y definiciones del juego 'El Último Peón'."""
import pygame

# --- Configuración de Pantalla y Ventana ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
WINDOW_TITLE = "El Último Peón - Roguelike Táctico"

# --- Dimensiones del Tablero ---
DEFAULT_BOARD_COLS = 5
DEFAULT_BOARD_ROWS = 5
MAX_BOARD_SIZE = 8

# --- Paleta Pixel Art: Piedra Rúnica, Madera y Tinta ---
# Fondos y Piedra
COLOR_BG = (18, 17, 24)
COLOR_STONE_DARK = (28, 30, 38)
COLOR_STONE_LIGHT = (48, 52, 66)
COLOR_STONE_BORDER = (68, 74, 92)
COLOR_BORDER = COLOR_STONE_BORDER
COLOR_PANEL = (32, 34, 44)
COLOR_PANEL_BORDER = (75, 80, 100)

# Botones
COLOR_BTN_DEFAULT = (36, 40, 52)
COLOR_BTN_HOVER = (50, 56, 74)
COLOR_BTN_BORDER = (65, 72, 92)
COLOR_BTN_BORDER_HOVER = (245, 185, 45)

# Runas Mágicas Talladas
COLOR_RUNE_GLOW = (88, 225, 255)
COLOR_RUNE_DARK = (45, 120, 150)
COLOR_RUNE_PURPLE = (205, 115, 255)

# Madera Tallada (Casillas del Tablero y Tablillas de Poder)
COLOR_WOOD_LIGHT = (196, 154, 108)     # Madera clara tallada
COLOR_WOOD_LIGHT_ALT = (180, 140, 96) # Veta clara
COLOR_WOOD_DARK = (130, 92, 60)        # Madera oscura tallada
COLOR_WOOD_DARK_ALT = (112, 78, 50)   # Veta oscura
COLOR_WOOD_BARK = (68, 46, 30)         # Borde corteza

# Piezas de Madera Tallada
COLOR_PIECE_WHITE = (245, 235, 215)
COLOR_PIECE_WHITE_SHADE = (185, 170, 145)
COLOR_PIECE_BLACK = (42, 38, 48)
COLOR_PIECE_BLACK_SHADE = (24, 22, 28)
COLOR_PIECE_BLACK_HIGHLIGHT = (85, 80, 95)
COLOR_PIECE_OUTLINE = (18, 16, 22)

# Resaltados e Interfaz
COLOR_VALID_MOVE = (235, 45, 55, 115)
COLOR_VALID_MOVE_HOVER = (255, 70, 75, 170)
COLOR_VALID_BORDER = (255, 65, 75, 235)
COLOR_ATTACK_MOVE = (210, 25, 35, 160)

COLOR_TEXT_MAIN = (245, 242, 235)
COLOR_TEXT_MUTED = (155, 155, 170)
COLOR_ACCENT = (245, 185, 45)          # Oro rúnico
COLOR_ACCENT_HOVER = (255, 210, 85)

# Rarezas de Poderes
COLOR_RARITY_1 = (130, 205, 95)        # Común / Verde
COLOR_RARITY_2 = (75, 165, 255)        # Raro / Azul
COLOR_RARITY_3 = (245, 175, 45)        # Mítico / Dorado-Naranja

# Trampas
COLOR_LAVA = (240, 75, 25)
COLOR_VINES = (45, 145, 60)
COLOR_BEAR_TRAP = (140, 140, 150)
