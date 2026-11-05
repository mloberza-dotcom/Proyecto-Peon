"""Panel de inspección táctica: muestra información detallada de la entidad o casilla bajo el cursor."""
import pygame
from src.board.board import Board
from src.config import (
    COLOR_PANEL,
    COLOR_BORDER,
    COLOR_ACCENT,
    COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED,
)
from src.graphics.pixel_art import (
    draw_pixel_pawn,
    draw_pixel_knight,
    draw_pixel_enemy_piece,
    draw_trap_sprite,
    get_wood_tile,
)


class InspectorPanel:
    """Cuadro exterior a la izquierda del tablero que describe piezas, trampas y casillas."""

    def __init__(self):
        self.font_header = pygame.font.SysFont("georgia", 10, bold=True)
        self.font_title = pygame.font.SysFont("georgia", 13, bold=True)
        self.font_tag = pygame.font.SysFont("arial", 10, bold=True)
        self.font_desc = pygame.font.SysFont("arial", 11)
        self.font_tip = pygame.font.SysFont("arial", 10, italic=True)

        self.last_info: dict | None = None

    def _wrap_text(self, text: str, max_width: int) -> list[str]:
        words = text.split(" ")
        lines = []
        current = ""
        for w in words:
            candidate = f"{current} {w}".strip()
            if self.font_desc.size(candidate)[0] <= max_width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = w
        if current:
            lines.append(current)
        return lines

    def inspect_tile(
        self,
        tile: tuple[int, int] | None,
        board: Board,
        player,
        enemies: list,
        allies: list,
        trap_manager,
        split_rows: list[int],
        valid_moves: list[tuple[int, int]],
        power_manager=None,
    ) -> dict | None:
        """Determina los datos descriptivos de lo que está bajo la casilla del cursor."""
        if not tile or not board.is_within_bounds(tile[0], tile[1]):
            return None

        c, r = tile

        # 1. Peón Blanco (Jugador)
        if player.alive and player.col == c and player.row == r:
            passives = []
            if power_manager:
                if power_manager.has_range_move:
                    passives.append("Paso Ligero (+1 mov)")
                if power_manager.has_range_kill:
                    passives.append("Alcance Letal (+1 matar)")
                if power_manager.has_kill_rook:
                    passives.append("Poder de Torre (línea recta)")
                if power_manager.has_kill_bishop:
                    passives.append("Poder de Alfil (diagonales)")

            passives_str = f"Bendiciones: {', '.join(passives)}." if passives else "Sin bendiciones activas."
            stun_str = f" ¡INMOVILIZADO ({player.immobilized_turns}t)!" if player.immobilized_turns > 0 else ""

            return {
                "kind": "player",
                "title": "PEÓN BLANCO",
                "tag": "TÚ • HÉROE",
                "tag_color": (255, 215, 80),
                "desc": (
                    f"Avanza 1 casilla en cruz (ortogonal). Come peones y al Rey Gigante como un Rey (8 casillas adyacentes). "
                    f"A otras piezas sólo las come en diagonal.{stun_str} {passives_str}"
                ),
                "tip": "Consejo: Usa tu captura de Rey contra peones rivales.",
            }

        # 2. Caballo Blanco Aliado
        ally = next((a for a in allies if a.alive and a.col == c and a.row == r), None)
        if ally:
            return {
                "kind": "ally_knight",
                "title": "CABALLO ALIADO",
                "tag": f"INVOCACIÓN • {ally.duration_turns}t",
                "tag_color": (120, 220, 255),
                "desc": (
                    f"Invocación sagrada que lucha a tu lado. Se desplaza y captura en 'L' (2x1) "
                    f"saltando piezas. Le restan {ally.duration_turns} turno(s) de vida."
                ),
                "tip": "Aliado: Ataca automáticamente a piezas cercanas.",
            }

        # 3. Pieza Enemiga
        enemy = next((e for e in enemies if e.alive and e.col == c and e.row == r), None)
        if enemy:
            role = enemy.piece_role
            stun_txt = f" [ATURDIDO {enemy.immobilized_turns}t]" if enemy.immobilized_turns > 0 else ""

            if enemy.is_boss:
                return {
                    "kind": "enemy",
                    "role": role,
                    "is_boss": True,
                    "title": "EL REY TIRANO",
                    "tag": f"JEFE FINAL • {enemy.hp}/{enemy.max_hp} HP{stun_txt}",
                    "tag_color": (255, 70, 70),
                    "desc": (
                        "Monarca colosal. Se mueve 1 casilla en 8 direcciones. Divide el tablero a 2/3 y 1/3 de vida, "
                        "siembra trampas cada 3 turnos e invoca guardias. Cada golpe que recibe lo hace retroceder."
                    ),
                    "tip": "Peligro: Golpéalo como un Rey o con tus poderes rúnicos.",
                }
            elif role == "pawn":
                if enemy.has_shield:
                    return {
                        "kind": "enemy",
                        "role": role,
                        "has_shield": True,
                        "title": "PEÓN CON ESCUDO",
                        "tag": f"GUARDIA ACORAZADO{stun_txt}",
                        "tag_color": (140, 220, 255),
                        "desc": (
                            "Posee escudo rúnico (2 vidas). El primer impacto rompe su escudo y lo repele 2 casillas. "
                            "Avanza verticalmente y captura en diagonal. Ciego a trampas."
                        ),
                        "tip": "Táctica: Rompe su escudo para dejarlo vulnerable.",
                    }
                else:
                    return {
                        "kind": "enemy",
                        "role": role,
                        "has_shield": False,
                        "title": "PEÓN NEGRO",
                        "tag": f"INFANTERÍA OSCURA{stun_txt}",
                        "tag_color": (220, 90, 90),
                        "desc": (
                            "Avanza 1 casilla hacia adelante o hacia atrás. Captura únicamente en diagonal a 1 casilla. "
                            "Ciego a trampas (morirá al pisar lava o trampa de osos)."
                        ),
                        "tip": "Debilidad: Puedes comerlo como un Rey.",
                    }
            elif role == "knight":
                return {
                    "kind": "enemy",
                    "role": role,
                    "title": "CABALLO NEGRO",
                    "tag": f"JINETE ÁGIL{stun_txt}",
                    "tag_color": (200, 140, 255),
                    "desc": (
                        "Salta obstáculos en patrón de 'L' (2x1). Es astuto: esquiva las trampas mortales "
                        "siempre que tenga una ruta alternativa segura."
                    ),
                    "tip": "Alerta: No te coloques a tiro de su salto en L.",
                }
            elif role == "bishop":
                return {
                    "kind": "enemy",
                    "role": role,
                    "title": "ALFIL NEGRO",
                    "tag": f"FRANCOTIRADOR{stun_txt}",
                    "tag_color": (230, 160, 90),
                    "desc": (
                        "Dispara y captura en rayos diagonales a distancia ilimitada si el camino está libre. "
                        "Ciego a las trampas: las pisará sin esquivarlas."
                    ),
                    "tip": "Peligro: Nunca permanezcas en su línea diagonal.",
                }
            elif role == "rook":
                return {
                    "kind": "enemy",
                    "role": role,
                    "title": "TORRE NEGRA",
                    "tag": f"BASTIÓN PESADO{stun_txt}",
                    "tag_color": (210, 110, 110),
                    "desc": (
                        "Embestida devastadora en línea recta ortogonal a cualquier distancia. "
                        "El Piroclasto no la destruye: la empuja a casillas limítrofes. Ciega a trampas."
                    ),
                    "tip": "Amenaza: No te alinees en su fila o columna.",
                }
            elif role == "queen":
                return {
                    "kind": "enemy",
                    "role": role,
                    "title": "REINA NEGRA",
                    "tag": f"SOBERANA LETAL{stun_txt}",
                    "tag_color": (240, 80, 160),
                    "desc": (
                        "La pieza más peligrosa: alcance infinito en las 8 direcciones (ortogonal y diagonal). "
                        "Astuta frente a trampas. Inmune a la muerte por Piroclasto."
                    ),
                    "tip": "Máxima alerta: Mantenla acorralada o elimínala rápido.",
                }

        # 4. Trampas en el suelo
        trap = trap_manager.get_trap_at(c, r)
        if trap:
            tname = trap.name.upper()
            ttype = trap.trap_type.name
            rem = max(1, 15 - (trap_manager.turn_count - trap.spawn_turn) if hasattr(trap_manager, "turn_count") else 15)

            if "LAVA" in ttype:
                return {
                    "kind": "trap",
                    "trap_type": trap.trap_type,
                    "title": "CHARCO DE LAVA",
                    "tag": "TRAMPA LETAL",
                    "tag_color": (255, 120, 30),
                    "desc": (
                        "Falla volcánica de magma ardiente. ¡Muerte instantánea para cualquier peón, enemigo o jugador! "
                        "Inflige 3 de daño si el Rey Gigante cae en ella."
                    ),
                    "tip": "¡Cuidado! Prohibido pisar bajo cualquier concepto.",
                }
            elif "BEAR" in ttype or "OSO" in tname:
                return {
                    "kind": "trap",
                    "trap_type": trap.trap_type,
                    "title": "TRAMPA DE OSO",
                    "tag": "CEPO MECÁNICO",
                    "tag_color": (220, 160, 60),
                    "desc": (
                        "Mata a cualquier peón que la pise. Inmoviliza a otras piezas rivales durante 2 turnos. "
                        "Si la pisas tú, te inmoviliza 1 turno."
                    ),
                    "tip": "Táctica: Atrae peones enemigos hacia ella.",
                }
            elif "VINE" in ttype or "ENREDADERA" in tname:
                return {
                    "kind": "trap",
                    "trap_type": trap.trap_type,
                    "title": "ENREDADERA",
                    "tag": "MALEZA RÚNICA",
                    "tag_color": (110, 210, 120),
                    "desc": (
                        "Raíces espinosas vivientes. Cualquiera que las pise (jugador o enemigos) "
                        "pierde su turno completamente inmovilizado."
                    ),
                    "tip": "Útil: Inmoviliza piezas peligrosas temporalmente.",
                }

        # 5. Fractura del Tablero (Fisura del Rey)
        if r in split_rows:
            bridge_cols = {2, 5} if board.cols >= 6 else {1, 3}
            if c not in bridge_cols:
                return {
                    "kind": "fissure",
                    "title": "ABISMO RÚNICO",
                    "tag": "FRACTURA DEL REY",
                    "tag_color": (255, 90, 40),
                    "desc": (
                        "Grieta ardiente creada por el Rey Tirano al fragmentar el tablero en dos. "
                        "Es infranqueable: cruza únicamente a través de los puentes de piedra."
                    ),
                    "tip": "Atención: Los puentes son casillas seguras para cruzar.",
                }

        # 6. Casilla alcanzable / válida
        if (c, r) in valid_moves:
            return {
                "kind": "valid_move",
                "title": "MOVIMIENTO",
                "tag": "CASILLA VÁLIDA",
                "tag_color": (120, 240, 120),
                "desc": "Haz clic con el botón izquierdo del ratón para desplazar a tu Peón Blanco a esta posición.",
                "tip": "Destino libre de peligros inmediatos.",
            }

        # 7. Casilla de Madera Rúnica (vacía)
        is_light = (c + r) % 2 == 0
        shade = "Clara" if is_light else "Oscura"
        col_letter = chr(ord('A') + c)
        row_num = str(board.rows - r)
        return {
            "kind": "wood_tile",
            "title": f"CASILLA {col_letter}{row_num}",
            "tag": f"MADERA ({shade})",
            "tag_color": (180, 160, 140),
            "desc": "Losa de roble tallado protegida con vetas rúnicas. Casilla libre actualmente desocupada.",
            "tip": "Coordina tus movimientos con paciencia.",
        }

    def render(
        self,
        surface: pygame.Surface,
        board: Board,
        player,
        enemies: list,
        allies: list,
        trap_manager,
        split_rows: list[int],
        valid_moves: list[tuple[int, int]],
        hovered_tile: tuple[int, int] | None,
        power_manager=None,
    ) -> None:
        """Renderiza la tarjeta informativa en el costado izquierdo exterior del tablero."""
        info = self.inspect_tile(
            hovered_tile,
            board,
            player,
            enemies,
            allies,
            trap_manager,
            split_rows,
            valid_moves,
            power_manager,
        )

        if info:
            self.last_info = info
        elif self.last_info is None:
            # Info por defecto de bienvenida táctica
            self.last_info = {
                "kind": "idle",
                "title": "INSPECTOR RÚNICO",
                "tag": "INFORMACIÓN",
                "tag_color": COLOR_ACCENT,
                "desc": "Pasa el cursor del ratón sobre cualquier casilla, pieza enemiga o trampa del tablero para conocer sus tácticas, alcance y debilidades.",
                "tip": "Consejo: Conoce a tu rival antes de avanzar.",
            }

        data = self.last_info

        # Medidas y posición (afuera del tablero a la izquierda)
        panel_w = 152
        panel_h = 360
        panel_x = 12
        panel_y = 66
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

        # Fondo rúnico
        pygame.draw.rect(surface, COLOR_PANEL, panel_rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_BORDER, panel_rect, width=1, border_radius=8)

        # 1. Cabecera pequeña
        header_surf = self.font_header.render("INSPECTOR TÁCTICO", True, COLOR_ACCENT)
        surface.blit(header_surf, header_surf.get_rect(center=(panel_x + panel_w // 2, panel_y + 14)))

        # Línea separadora decorativa
        sep_y = panel_y + 26
        pygame.draw.line(surface, COLOR_BORDER, (panel_x + 10, sep_y), (panel_x + panel_w - 10, sep_y), 1)

        # 2. Preview gráfica en pixel art (caja 44x44)
        box_sz = 44
        box_x = panel_x + (panel_w - box_sz) // 2
        box_y = panel_y + 34
        box_rect = pygame.Rect(box_x, box_y, box_sz, box_sz)
        pygame.draw.rect(surface, (25, 18, 20), box_rect, border_radius=6)
        pygame.draw.rect(surface, (70, 55, 60), box_rect, width=1, border_radius=6)

        cx, cy = box_rect.center
        kind = data.get("kind", "idle")

        if kind == "player":
            draw_pixel_pawn(surface, cx, cy, size=38, is_white=True)
        elif kind == "ally_knight":
            draw_pixel_knight(surface, cx, cy, size=38, is_ally=True)
        elif kind == "enemy":
            draw_pixel_enemy_piece(
                surface, cx, cy, size=38,
                piece_role=data.get("role", "pawn"),
                has_shield=data.get("has_shield", False),
                is_boss=data.get("is_boss", False),
            )
        elif kind == "trap":
            draw_trap_sprite(surface, cx, cy, size=36, trap_type=data.get("trap_type"))
        elif kind == "fissure":
            # Mini magma rift
            pygame.draw.rect(surface, (220, 60, 20), (cx - 16, cy - 6, 32, 12), border_radius=3)
            pygame.draw.line(surface, (255, 220, 80), (cx - 14, cy), (cx + 14, cy), 2)
        elif kind == "valid_move":
            pygame.draw.circle(surface, (80, 220, 80), (cx, cy), 14, width=2)
            pygame.draw.circle(surface, (120, 255, 120), (cx, cy), 5)
        elif kind == "wood_tile":
            mini_wood = get_wood_tile(36, True)
            surface.blit(mini_wood, (cx - 18, cy - 18))
        else:
            # Icono de ojo / runa de inspección
            pygame.draw.circle(surface, COLOR_ACCENT, (cx, cy), 12, width=1)
            pygame.draw.circle(surface, (255, 230, 160), (cx, cy), 4)

        # 3. Título de la entidad
        title_surf = self.font_title.render(data.get("title", ""), True, COLOR_TEXT_MAIN)
        surface.blit(title_surf, title_surf.get_rect(center=(panel_x + panel_w // 2, panel_y + 92)))

        # 4. Etiqueta / Tag de rol
        tag_txt = data.get("tag", "")
        tag_col = data.get("tag_color", COLOR_ACCENT)
        tag_surf = self.font_tag.render(tag_txt, True, tag_col)
        t_rect = tag_surf.get_rect(center=(panel_x + panel_w // 2, panel_y + 110))
        pill_rect = t_rect.inflate(14, 5)
        pygame.draw.rect(surface, (30, 20, 24), pill_rect, border_radius=4)
        pygame.draw.rect(surface, tag_col, pill_rect, width=1, border_radius=4)
        surface.blit(tag_surf, t_rect)

        # Separador medio
        pygame.draw.line(surface, (55, 45, 50), (panel_x + 12, panel_y + 126), (panel_x + panel_w - 12, panel_y + 126), 1)

        # 5. Descripción formateada con ajuste de línea
        desc_lines = self._wrap_text(data.get("desc", ""), max_width=panel_w - 20)
        curr_y = panel_y + 134
        for line in desc_lines[:9]:  # Máximo 9 líneas para que quepa holgadamente
            l_surf = self.font_desc.render(line, True, (215, 210, 210))
            surface.blit(l_surf, (panel_x + 10, curr_y))
            curr_y += 15

        # 6. Consejo táctico al pie de la tarjeta
        tip_text = data.get("tip", "")
        if tip_text:
            tip_lines = self._wrap_text(tip_text, max_width=panel_w - 20)
            tip_y = panel_y + panel_h - 12 - len(tip_lines) * 13
            for line in tip_lines:
                t_surf = self.font_tip.render(line, True, COLOR_ACCENT)
                surface.blit(t_surf, (panel_x + 10, tip_y))
                tip_y += 13
