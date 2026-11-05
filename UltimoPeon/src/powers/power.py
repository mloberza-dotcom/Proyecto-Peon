"""Definición y catálogo de poderes y bendiciones (estilo Hades)."""
from dataclasses import dataclass
from enum import Enum, auto


class PowerType(Enum):
    PASSIVE = auto()
    ACTIVE = auto()


@dataclass
class Power:
    """Representa una bendición o mejora para la incursión."""
    id: str
    name: str
    rarity: int                  # 1 = Común, 2 = Raro, 3 = Mítico
    power_type: PowerType
    icon_id: str
    description: str
    used_in_level: bool = False  # Para poderes activos (1 uso por nivel)
    hotkey_num: int = 0          # Número 1, 2, 3 asignado para el hotbar
    tier: int = 1                # Nivel de mejora del poder (ej. I, II)
    max_tier: int = 1            # Nivel máximo alcanzable


# Catálogo oficial de poderes
ALL_POWERS: dict[str, Power] = {
    "range_kill": Power(
        id="range_kill",
        name="Alcance Letal",
        rarity=1,
        power_type=PowerType.PASSIVE,
        icon_id="range_kill",
        description="Aumenta tu alcance de ataque en diagonal a 2 casillas de distancia.",
    ),
    "range_move": Power(
        id="range_move",
        name="Paso Ligero",
        rarity=1,
        power_type=PowerType.PASSIVE,
        icon_id="range_move",
        description="Permite avanzar hasta 2 casillas en línea recta si el camino está libre.",
    ),
    "kill_rook": Power(
        id="kill_rook",
        name="Furia de la Torre",
        rarity=2,
        power_type=PowerType.PASSIVE,
        icon_id="kill_rook",
        description="Puedes atacar y capturar enemigos en línea recta ortogonal como una Torre.",
    ),
    "kill_bishop": Power(
        id="kill_bishop",
        name="Veredicto del Alfil",
        rarity=2,
        power_type=PowerType.PASSIVE,
        icon_id="kill_bishop",
        description="Puedes atacar y capturar enemigos en diagonal a cualquier distancia como un Alfil.",
    ),
    "summon_knight": Power(
        id="summon_knight",
        name="Espíritu del Caballo",
        rarity=2,
        power_type=PowerType.ACTIVE,
        icon_id="summon_knight",
        description="Clic derecho para invocar un Caballo aliado (dura 15 turnos) detrás de tu posición.",
    ),
    "black_hole": Power(
        id="black_hole",
        name="Vórtice Abisal",
        rarity=3,
        power_type=PowerType.ACTIVE,
        icon_id="black_hole",
        description="1 uso/nivel: Aniquila Peones, Caballos y Alfiles. Contra Torres, Reina o Rey los teletransporta a la mitad rival.",
    ),
    "fireball": Power(
        id="fireball",
        name="Piroclasto de Magma",
        rarity=3,
        power_type=PowerType.ACTIVE,
        icon_id="fireball",
        description="1 uso/nivel: Bombardea una zona de 2x2 casillas eliminando enemigos de menor rango.",
    ),
    "arrow": Power(
        id="arrow",
        name="Flecha Rúnica",
        rarity=2,
        power_type=PowerType.ACTIVE,
        icon_id="arrow",
        description="1 uso/nivel: Disparo a distancia que elimina Peones o Caballos enemigos (no daña Alfiles ni superiores).",
    ),
    "place_trap": Power(
        id="place_trap",
        name="Artilugio Trampa [I]",
        rarity=3,
        power_type=PowerType.ACTIVE,
        icon_id="place_trap",
        description="1 uso/nivel: Despliega una trampa al azar en cualquier casilla del mapa. Mejorable a Nivel II.",
        tier=1,
        max_tier=2,
    ),
}
