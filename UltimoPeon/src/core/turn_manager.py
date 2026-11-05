"""Gestor de turnos y fases del juego."""
from enum import Enum, auto


class TurnPhase(Enum):
    """Fases posibles dentro del ciclo de un turno."""
    PLAYER = auto()
    ENEMY = auto()


class TurnManager:
    """Controla el flujo de turnos por pasos discretos."""

    def __init__(self):
        self.turn_count: int = 1
        self.phase: TurnPhase = TurnPhase.PLAYER

    def to_enemy_phase(self) -> None:
        """Pasa el control a la fase del enemigo."""
        self.phase = TurnPhase.ENEMY

    def to_player_phase(self) -> None:
        """Regresa el control al jugador e incrementa el contador de turnos."""
        self.phase = TurnPhase.PLAYER
        self.turn_count += 1

    def reset(self) -> None:
        """Reinicia el contador al comenzar una nueva partida."""
        self.turn_count = 1
        self.phase = TurnPhase.PLAYER
