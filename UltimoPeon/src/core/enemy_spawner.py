"""Generador de hordas enemigas y reglas de aparición por nivel (Niveles 1 a 10)."""
import random
from src.board.board import Board
from src.entities.enemy import EnemyPawn


def spawn_enemies_for_level(level: int, board: Board) -> list[EnemyPawn]:
    """
    Genera la composición de enemigos y los ubica en las filas superiores según las reglas:
    - Filas 0 y 1 para todas las piezas.
    - Si hay más de 8 enemigos, los peones excedentes pueden ubicarse en la fila 2.
    - REGLA ESTRICTA: NUNCA pueden aparecer 2 caballos juntos en ningún nivel (máximo 1 caballo).
    """
    roles_to_spawn: list[str] = []

    if level == 1:
        # Nivel 1: Siempre 2 peones
        roles_to_spawn = ["pawn", "pawn"]

    elif level == 2:
        # Nivel 2: 2 peones y 1 caballo O de 4 a 6 peones
        if random.random() < 0.5:
            roles_to_spawn = ["pawn", "pawn", "knight"]
        else:
            pawn_count = random.randint(4, 6)
            roles_to_spawn = ["pawn"] * pawn_count

    elif level in (3, 4):
        # Niveles 3 y 4: (3 peones + 1 caballo) O (5 peones) O (7 peones) [Eliminada opción de 2 caballos]
        choice = random.choice(["pawn_knight", "five_pawns", "seven_pawns"])
        if choice == "pawn_knight":
            roles_to_spawn = ["pawn", "pawn", "pawn", "knight"]
        elif choice == "five_pawns":
            roles_to_spawn = ["pawn"] * 5
        else:
            roles_to_spawn = ["pawn"] * 7

    elif level == 5:
        # Nivel 5: (4 peones + 1 caballo) O (2 peones + 1 alfil) O (1 caballo + 1 alfil)
        choice = random.choice(["4p_1k", "2p_1b", "1k_1b"])
        if choice == "4p_1k":
            roles_to_spawn = ["pawn"] * 4 + ["knight"]
        elif choice == "2p_1b":
            roles_to_spawn = ["pawn"] * 2 + ["bishop"]
        else:
            roles_to_spawn = ["knight", "bishop"]

    elif level == 6:
        # Nivel 6: Lo mismo que el 5 pero en los que aparecen peones sumar +1
        choice = random.choice(["5p_1k", "3p_1b", "1k_1b"])
        if choice == "5p_1k":
            roles_to_spawn = ["pawn"] * 5 + ["knight"]
        elif choice == "3p_1b":
            roles_to_spawn = ["pawn"] * 3 + ["bishop"]
        else:
            roles_to_spawn = ["knight", "bishop"]

    elif level == 7:
        # Nivel 7: (5 peones + 1 caballo) O (3 peones + 1 alfil) O (1 caballo + 1 alfil + 2 peones) [Sin 2 caballos]
        choice = random.choice(["5p_1k", "3p_1b", "1k_1b_2p"])
        if choice == "5p_1k":
            roles_to_spawn = ["pawn"] * 5 + ["knight"]
        elif choice == "3p_1b":
            roles_to_spawn = ["pawn"] * 3 + ["bishop"]
        else:
            roles_to_spawn = ["knight", "bishop", "pawn", "pawn"]

    elif level in (8, 9):
        # Niveles 8 y 9: (2 torres) O (5 peones + 2 alfiles) O (1 torre + 1 alfil + 1 caballo + 1 peón) [Sin 2 caballos]
        choice = random.choice(["2_rooks", "5p_2b", "1r_1b_1k_1p"])
        if choice == "2_rooks":
            roles_to_spawn = ["rook", "rook"]
        elif choice == "5p_2b":
            roles_to_spawn = ["pawn"] * 5 + ["bishop", "bishop"]
        else:
            roles_to_spawn = ["rook", "bishop", "knight", "pawn"]

    elif level == 10:
        # Nivel 10: 2 Reinas
        roles_to_spawn = ["queen", "queen"]

    elif level >= 11:
        # Nivel 11: JEFE FINAL - EL REY GIGANTE
        boss_col = board.cols // 2
        boss_king = EnemyPawn(col=boss_col, row=0, piece_role="king", is_boss=True, hp=12)
        guard_left = EnemyPawn(col=1, row=1, piece_role="pawn", has_shield=True)
        guard_right = EnemyPawn(col=max(2, board.cols - 2), row=1, piece_role="pawn", has_shield=False)
        return [boss_king, guard_left, guard_right]

    # Seguro estricto: garantizar que NUNCA haya más de 1 caballo
    if roles_to_spawn.count("knight") > 1:
        first_k = False
        fixed_roles = []
        for r in roles_to_spawn:
            if r == "knight":
                if not first_k:
                    fixed_roles.append("knight")
                    first_k = True
                else:
                    fixed_roles.append("pawn")
            else:
                fixed_roles.append(r)
        roles_to_spawn = fixed_roles

    # 2. Separar piezas mayores de peones para respetar la regla de filas
    major_pieces = [r for r in roles_to_spawn if r != "pawn"]
    pawn_pieces = [r for r in roles_to_spawn if r == "pawn"]

    # Casillas disponibles en filas 0 y 1
    front_rows_tiles = [(c, r) for r in (0, 1) for c in range(board.cols)]
    random.shuffle(front_rows_tiles)

    # Casillas para fila 2 (sólo si hay más de 8 enemigos en total)
    allow_row_2_for_pawns = len(roles_to_spawn) > 8
    row_2_tiles = [(c, 2) for c in range(board.cols)] if allow_row_2_for_pawns else []
    random.shuffle(row_2_tiles)

    enemies: list[EnemyPawn] = []
    used_tiles: set[tuple[int, int]] = set()

    # Ubicar primero las piezas mayores (siempre en filas 0 y 1)
    for role in major_pieces:
        tile = next((t for t in front_rows_tiles if t not in used_tiles), None)
        if tile:
            used_tiles.add(tile)
            enemies.append(EnemyPawn(col=tile[0], row=tile[1], piece_role=role))

    # Ubicar los peones
    for role in pawn_pieces:
        tile = next((t for t in front_rows_tiles if t not in used_tiles), None)
        if not tile and allow_row_2_for_pawns:
            tile = next((t for t in row_2_tiles if t not in used_tiles), None)

        if tile:
            used_tiles.add(tile)
            enemies.append(EnemyPawn(col=tile[0], row=tile[1], piece_role=role))

    return enemies
