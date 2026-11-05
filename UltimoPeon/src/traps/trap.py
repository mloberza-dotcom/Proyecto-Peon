"""Definición y comportamiento de las trampas ambientales."""
from dataclasses import dataclass
from enum import Enum, auto


class TrapType(Enum):
    BEAR_TRAP = auto()  # Trampa para osos
    VINES = auto()      # Enredadera
    LAVA = auto()       # Charco de lava


@dataclass
class Trap:
    """Representa una trampa activa en el tablero."""
    trap_type: TrapType
    tiles: list[tuple[int, int]]  # Casillas que ocupa (Lava puede ocupar más de una)
    duration_turns: int = 15       # Dura 15 turnos
    spawn_turn: int = 1

    @property
    def name(self) -> str:
        if self.trap_type == TrapType.BEAR_TRAP:
            return "Trampa de Oso"
        elif self.trap_type == TrapType.VINES:
            return "Enredadera"
        elif self.trap_type == TrapType.LAVA:
            return "Charco de Lava"
        return "Trampa"

    def is_expired(self, current_turn: int) -> bool:
        """Determina si la trampa superó su límite de 15 turnos."""
        return (current_turn - self.spawn_turn) >= self.duration_turns

    def occupies(self, col: int, row: int) -> bool:
        """Verifica si la casilla (col, row) está cubierta por esta trampa."""
        return (col, row) in self.tiles
