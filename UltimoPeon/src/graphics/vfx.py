"""Sistema de Efectos Visuales (VFX) y Animaciones para poderes, combate y eventos."""
import math
import random
import pygame
from src.board.board import Board


class Particle:
    """Partícula individual con física, color y desvanecimiento."""

    def __init__(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        color: tuple[int, int, int],
        size: float,
        life_ms: float,
        decay_size: bool = True,
        gravity: float = 0.0,
    ):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.initial_size = size
        self.life_ms = life_ms
        self.max_life = life_ms
        self.decay_size = decay_size
        self.gravity = gravity

    def update(self, dt_ms: float) -> bool:
        self.life_ms -= dt_ms
        if self.life_ms <= 0:
            return False

        self.x += self.vx * (dt_ms / 1000.0)
        self.y += self.vy * (dt_ms / 1000.0)
        self.vy += self.gravity * (dt_ms / 1000.0)

        if self.decay_size:
            ratio = max(0.0, self.life_ms / self.max_life)
            self.size = max(1.0, self.initial_size * ratio)

        return True

    def render(self, surface: pygame.Surface) -> None:
        ratio = max(0.0, min(1.0, self.life_ms / self.max_life))
        alpha = int(255 * ratio)
        int_size = max(1, int(self.size))

        p_surf = pygame.Surface((int_size * 2 + 2, int_size * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(
            p_surf,
            (*self.color[:3], alpha),
            (int_size + 1, int_size + 1),
            int_size,
        )
        surface.blit(p_surf, (int(self.x - int_size - 1), int(self.y - int_size - 1)))


class FloatingText:
    """Texto flotante emergente para daño y efectos de estado."""

    def __init__(self, x: float, y: float, text: str, color: tuple[int, int, int], duration_ms: float = 700):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.life_ms = duration_ms
        self.max_life = duration_ms
        self.font = pygame.font.SysFont("georgia", 15, bold=True)

    def update(self, dt_ms: float) -> bool:
        self.life_ms -= dt_ms
        if self.life_ms <= 0:
            return False
        self.y -= 28 * (dt_ms / 1000.0)
        return True

    def render(self, surface: pygame.Surface) -> None:
        ratio = max(0.0, min(1.0, self.life_ms / self.max_life))
        alpha = int(255 * ratio)

        txt_surf = self.font.render(self.text, True, self.color)
        t_w, t_h = txt_surf.get_size()
        alpha_surf = pygame.Surface((t_w + 4, t_h + 4), pygame.SRCALPHA)

        # Sombra
        shadow_surf = self.font.render(self.text, True, (10, 10, 15))
        alpha_surf.blit(shadow_surf, (3, 3))
        alpha_surf.blit(txt_surf, (1, 1))
        alpha_surf.set_alpha(alpha)

        surface.blit(alpha_surf, (int(self.x - t_w // 2), int(self.y - t_h // 2)))


class FireballVFX:
    """Animación cinemática de Piroclasto de Magma (impacto 2x2, meteorito, onda expansiva y humo)."""

    def __init__(self, target_c: int, target_r: int, on_impact=None, on_finish=None):
        self.target_c = target_c
        self.target_r = target_r
        self.on_impact = on_impact
        self.on_finish = on_finish
        self.elapsed_ms = 0.0
        self.duration_ms = 520.0
        self.impact_time_ms = 180.0
        self.impact_triggered = False
        self.finish_triggered = False
        self.particles: list[Particle] = []
        self.is_blocking = True

    def update(self, dt_ms: float, board: Board, vfx_manager: "VFXManager") -> bool:
        self.elapsed_ms += dt_ms

        # Fase de impacto
        if self.elapsed_ms >= self.impact_time_ms and not self.impact_triggered:
            self.impact_triggered = True
            vfx_manager.trigger_screen_shake(duration_ms=280, intensity=6.0)

            # Generar lluvia y explosión de brasas
            cx, cy = self._get_center_pixel(board)
            palette = [
                (255, 255, 255),
                (255, 220, 80),
                (255, 140, 20),
                (220, 40, 20),
                (140, 20, 10),
                (50, 40, 45),
            ]
            for _ in range(50):
                angle = random.uniform(0, math.tau)
                speed = random.uniform(80, 280)
                vx = math.cos(angle) * speed
                vy = math.sin(angle) * speed - random.uniform(20, 80)
                col = random.choice(palette)
                sz = random.uniform(2.5, 6.5)
                life = random.uniform(250, 420)
                self.particles.append(Particle(cx, cy, vx, vy, col, sz, life, gravity=180.0))

            if self.on_impact:
                self.on_impact()

        # Actualizar partículas
        self.particles = [p for p in self.particles if p.update(dt_ms)]

        if self.elapsed_ms >= self.duration_ms:
            if not self.finish_triggered:
                self.finish_triggered = True
                if self.on_finish:
                    self.on_finish()
            return False

        return True

    def _get_center_pixel(self, board: Board) -> tuple[int, int]:
        p1 = board.get_tile_center(self.target_c, self.target_r)
        p2 = board.get_tile_center(
            min(board.cols - 1, self.target_c + 1),
            min(board.rows - 1, self.target_r + 1),
        )
        return (p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2

    def render(self, surface: pygame.Surface, board: Board) -> None:
        cx, cy = self._get_center_pixel(board)

        # 1. Fase de proyectil meteorito descendiendo
        if self.elapsed_ms < self.impact_time_ms:
            t = self.elapsed_ms / self.impact_time_ms
            curr_x = cx - (1.0 - t) * 80
            curr_y = cy - (1.0 - t) * 220

            # Estela de fuego
            for i in range(8):
                tail_t = max(0.0, t - i * 0.04)
                tx = cx - (1.0 - tail_t) * 80 + random.randint(-4, 4)
                ty = cy - (1.0 - tail_t) * 220 + random.randint(-4, 4)
                sz = max(2, int(10 * (1.0 - i * 0.12)))
                col = (255, 180 - i * 20, 30)
                pygame.draw.circle(surface, col, (int(tx), int(ty)), sz)

            # Cabeza del meteorito blanco-dorado
            pygame.draw.circle(surface, (255, 255, 230), (int(curr_x), int(curr_y)), 12)
            pygame.draw.circle(surface, (255, 140, 20), (int(curr_x), int(curr_y)), 16, 2)

        # 2. Onda expansiva tras impacto
        else:
            impact_elapsed = self.elapsed_ms - self.impact_time_ms
            ratio = impact_elapsed / (self.duration_ms - self.impact_time_ms)

            # Anillo de fuego expansivo
            radius = int(board.tile_size * 1.5 * ratio)
            alpha = int(220 * (1.0 - ratio))
            ring_surf = pygame.Surface((radius * 2 + 4, radius * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(
                ring_surf,
                (255, 120, 20, alpha),
                (radius + 2, radius + 2),
                radius,
                width=max(2, int(6 * (1.0 - ratio))),
            )
            surface.blit(ring_surf, (cx - radius - 2, cy - radius - 2))

            # Resplandor central de magma
            glow_rad = int(board.tile_size * (1.0 - ratio * 0.6))
            if glow_rad > 0:
                glow_surf = pygame.Surface((glow_rad * 2 + 4, glow_rad * 2 + 4), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (255, 240, 180, int(160 * (1.0 - ratio))), (glow_rad + 2, glow_rad + 2), glow_rad)
                surface.blit(glow_surf, (cx - glow_rad - 2, cy - glow_rad - 2))

        # 3. Renderizar partículas
        for p in self.particles:
            p.render(surface)


class BlackHoleVFX:
    """Animación de Vórtice Abisal / Agujero Negro con espirales cósmicas y partículas de singularidad."""

    def __init__(self, col: int, row: int, on_complete=None):
        self.col = col
        self.row = row
        self.on_complete = on_complete
        self.elapsed_ms = 0.0
        self.duration_ms = 480.0
        self.completed = False
        self.particles: list[Particle] = []
        self.is_blocking = True

    def update(self, dt_ms: float, board: Board, vfx_manager: "VFXManager") -> bool:
        self.elapsed_ms += dt_ms
        cx, cy = board.get_tile_center(self.col, self.row)

        # Generar partículas en espiral que son succionadas hacia el centro
        if self.elapsed_ms < self.duration_ms * 0.7:
            for _ in range(3):
                angle = random.uniform(0, math.tau)
                dist = random.uniform(board.tile_size * 0.5, board.tile_size * 1.1)
                px = cx + math.cos(angle) * dist
                py = cy + math.sin(angle) * dist
                # Velocidad hacia el centro con giro tangencial
                speed = random.uniform(140, 220)
                vx = -math.cos(angle) * speed - math.sin(angle) * (speed * 0.7)
                vy = -math.sin(angle) * speed + math.cos(angle) * (speed * 0.7)
                col = random.choice([(180, 80, 255), (120, 40, 220), (70, 220, 255), (255, 255, 255)])
                self.particles.append(Particle(px, py, vx, vy, col, size=random.uniform(2.0, 4.0), life_ms=260.0))

        self.particles = [p for p in self.particles if p.update(dt_ms)]

        if self.elapsed_ms >= self.duration_ms:
            if not self.completed:
                self.completed = True
                if self.on_complete:
                    self.on_complete()
            return False

        return True

    def render(self, surface: pygame.Surface, board: Board) -> None:
        cx, cy = board.get_tile_center(self.col, self.row)
        t = min(1.0, self.elapsed_ms / self.duration_ms)

        # Apertura, vórtice y colapso
        if t < 0.6:
            scale = math.sin((t / 0.6) * (math.pi / 2))
        else:
            scale = max(0.0, 1.0 - ((t - 0.6) / 0.4))

        radius = int(board.tile_size * 0.65 * scale)
        if radius > 2:
            # Disco de acreción giratorio
            rot = self.elapsed_ms * 0.012
            vortex_surf = pygame.Surface((radius * 2 + 8, radius * 2 + 8), pygame.SRCALPHA)
            vc = radius + 4

            # Anillos concéntricos espirales
            for r_ring in range(radius, 4, -4):
                alpha = int(180 * (r_ring / radius))
                col = (140, 60, 240, alpha) if (r_ring // 4) % 2 == 0 else (60, 200, 255, alpha)
                pygame.draw.circle(vortex_surf, col, (vc, vc), r_ring, width=2)

            # Singularidad central negra pura
            inner_r = max(2, int(radius * 0.45))
            pygame.draw.circle(vortex_surf, (12, 6, 18, 245), (vc, vc), inner_r)
            pygame.draw.circle(vortex_surf, (220, 140, 255, 200), (vc, vc), inner_r + 1, width=2)

            surface.blit(vortex_surf, (cx - vc, cy - vc))

        for p in self.particles:
            p.render(surface)


class ArrowVFX:
    """Animación de proyectil de Flecha Rúnica desde el peón blanco hasta el objetivo."""

    def __init__(self, start_c: int, start_r: int, target_c: int, target_r: int, on_impact=None, on_finish=None):
        self.start_c = start_c
        self.start_r = start_r
        self.target_c = target_c
        self.target_r = target_r
        self.on_impact = on_impact
        self.on_finish = on_finish
        self.elapsed_ms = 0.0
        self.flight_time_ms = 180.0
        self.duration_ms = 380.0
        self.impact_triggered = False
        self.finish_triggered = False
        self.particles: list[Particle] = []
        self.trail: list[tuple[float, float]] = []
        self.is_blocking = True

    def update(self, dt_ms: float, board: Board, vfx_manager: "VFXManager") -> bool:
        self.elapsed_ms += dt_ms
        p_start = board.get_tile_center(self.start_c, self.start_r)
        p_end = board.get_tile_center(self.target_c, self.target_r)

        if self.elapsed_ms < self.flight_time_ms:
            t = self.elapsed_ms / self.flight_time_ms
            curr_x = p_start[0] + (p_end[0] - p_start[0]) * t
            curr_y = p_start[1] + (p_end[1] - p_start[1]) * t
            self.trail.append((curr_x, curr_y))
            if len(self.trail) > 10:
                self.trail.pop(0)

            # Chispas en vuelo
            if random.random() < 0.6:
                self.particles.append(
                    Particle(
                        curr_x, curr_y,
                        vx=random.uniform(-30, 30), vy=random.uniform(-30, 30),
                        color=(120, 230, 255), size=random.uniform(1.5, 3.0), life_ms=160.0
                    )
                )

        elif not self.impact_triggered:
            self.impact_triggered = True
            vfx_manager.trigger_screen_shake(duration_ms=180, intensity=3.5)

            # Estallido de esquirlas rúnicas al impacto
            for _ in range(25):
                angle = random.uniform(0, math.tau)
                spd = random.uniform(60, 220)
                col = random.choice([(255, 240, 120), (100, 230, 255), (255, 255, 255)])
                self.particles.append(
                    Particle(
                        p_end[0], p_end[1],
                        vx=math.cos(angle) * spd, vy=math.sin(angle) * spd,
                        color=col, size=random.uniform(2.0, 5.0), life_ms=random.uniform(180, 300)
                    )
                )
            if self.on_impact:
                self.on_impact()

        self.particles = [p for p in self.particles if p.update(dt_ms)]

        if self.elapsed_ms >= self.duration_ms:
            if not self.finish_triggered:
                self.finish_triggered = True
                if self.on_finish:
                    self.on_finish()
            return False

        return True

    def render(self, surface: pygame.Surface, board: Board) -> None:
        p_start = board.get_tile_center(self.start_c, self.start_r)
        p_end = board.get_tile_center(self.target_c, self.target_r)

        # 1. Estela rúnica
        if self.trail:
            for i, (tx, ty) in enumerate(self.trail):
                alpha = int(255 * (i / len(self.trail)))
                sz = max(1, int(4 * (i / len(self.trail))))
                t_surf = pygame.Surface((sz * 2 + 2, sz * 2 + 2), pygame.SRCALPHA)
                pygame.draw.circle(t_surf, (80, 210, 255, alpha), (sz + 1, sz + 1), sz)
                surface.blit(t_surf, (int(tx - sz - 1), int(ty - sz - 1)))

        # 2. Flecha en vuelo
        if self.elapsed_ms < self.flight_time_ms:
            t = self.elapsed_ms / self.flight_time_ms
            curr_x = p_start[0] + (p_end[0] - p_start[0]) * t
            curr_y = p_start[1] + (p_end[1] - p_start[1]) * t

            angle = math.atan2(p_end[1] - p_start[1], p_end[0] - p_start[0])
            head_len = 16
            x_tip = curr_x + math.cos(angle) * head_len
            y_tip = curr_y + math.sin(angle) * head_len
            x_back = curr_x - math.cos(angle) * head_len
            y_back = curr_y - math.sin(angle) * head_len

            pygame.draw.line(surface, (255, 255, 255), (int(x_back), int(y_back)), (int(x_tip), int(y_tip)), 3)
            pygame.draw.circle(surface, (120, 240, 255), (int(x_tip), int(y_tip)), 5)

        # 3. Partículas de impacto
        for p in self.particles:
            p.render(surface)


class SummonVFX:
    """Animación de Invocación Rúnica (círculo mágico de runas y pilar de luz celestial)."""

    def __init__(self, col: int, row: int, on_complete=None):
        self.col = col
        self.row = row
        self.on_complete = on_complete
        self.elapsed_ms = 0.0
        self.duration_ms = 460.0
        self.completed = False
        self.particles: list[Particle] = []
        self.is_blocking = True

    def update(self, dt_ms: float, board: Board, vfx_manager: "VFXManager") -> bool:
        self.elapsed_ms += dt_ms
        cx, cy = board.get_tile_center(self.col, self.row)

        if self.elapsed_ms < self.duration_ms * 0.8:
            for _ in range(2):
                angle = random.uniform(0, math.tau)
                r = random.uniform(4, board.tile_size * 0.45)
                px = cx + math.cos(angle) * r
                py = cy + math.sin(angle) * r
                self.particles.append(
                    Particle(
                        px, py,
                        vx=random.uniform(-10, 10), vy=-random.uniform(60, 160),
                        color=(200, 240, 255), size=random.uniform(2.0, 4.5), life_ms=300.0
                    )
                )

        self.particles = [p for p in self.particles if p.update(dt_ms)]

        if self.elapsed_ms >= self.duration_ms:
            if not self.completed:
                self.completed = True
                if self.on_complete:
                    self.on_complete()
            return False

        return True

    def render(self, surface: pygame.Surface, board: Board) -> None:
        cx, cy = board.get_tile_center(self.col, self.row)
        t = min(1.0, self.elapsed_ms / self.duration_ms)

        # 1. Círculo de invocación en el suelo
        r_circ = int(board.tile_size * 0.46)
        circ_surf = pygame.Surface((r_circ * 2 + 4, r_circ * 2 + 4), pygame.SRCALPHA)
        alpha = int(220 * math.sin(t * math.pi))
        pygame.draw.circle(circ_surf, (80, 210, 255, alpha), (r_circ + 2, r_circ + 2), r_circ, width=2)
        pygame.draw.circle(circ_surf, (220, 245, 255, alpha), (r_circ + 2, r_circ + 2), max(2, r_circ - 6), width=1)
        surface.blit(circ_surf, (cx - r_circ - 2, cy - r_circ - 2))

        # 2. Pilar de luz vertical
        if 0.2 < t < 0.85:
            beam_t = (t - 0.2) / 0.65
            beam_alpha = int(180 * math.sin(beam_t * math.pi))
            beam_w = int(board.tile_size * 0.6)
            beam_h = int(board.tile_size * 2.2)
            beam_surf = pygame.Surface((beam_w, beam_h), pygame.SRCALPHA)
            beam_surf.fill((160, 230, 255, beam_alpha))
            surface.blit(beam_surf, (cx - beam_w // 2, cy - beam_h + 10))

        for p in self.particles:
            p.render(surface)


class ShieldBreakVFX:
    """Animación de fractura de escudo de energía (fragmentos celestes que se dispersan)."""

    def __init__(self, col: int, row: int):
        self.col = col
        self.row = row
        self.elapsed_ms = 0.0
        self.duration_ms = 350.0
        self.particles: list[Particle] = []
        self.is_blocking = False
        self.spawned = False

    def update(self, dt_ms: float, board: Board, vfx_manager: "VFXManager") -> bool:
        self.elapsed_ms += dt_ms
        if not self.spawned:
            self.spawned = True
            cx, cy = board.get_tile_center(self.col, self.row)
            # Fragmentos de escudo
            for _ in range(24):
                angle = random.uniform(0, math.tau)
                spd = random.uniform(70, 200)
                col = random.choice([(140, 230, 255), (80, 180, 255), (255, 255, 255)])
                self.particles.append(
                    Particle(
                        cx, cy,
                        vx=math.cos(angle) * spd, vy=math.sin(angle) * spd,
                        color=col, size=random.uniform(2.5, 5.0), life_ms=280.0
                    )
                )

        self.particles = [p for p in self.particles if p.update(dt_ms)]
        return self.elapsed_ms < self.duration_ms

    def render(self, surface: pygame.Surface, board: Board) -> None:
        for p in self.particles:
            p.render(surface)


class SlashVFX:
    """Corte de espada dinámico sobre una casilla al capturar o asestar un golpe letal."""

    def __init__(self, col: int, row: int, is_heavy: bool = False):
        self.col = col
        self.row = row
        self.is_heavy = is_heavy
        self.elapsed_ms = 0.0
        self.duration_ms = 220.0
        self.is_blocking = False

    def update(self, dt_ms: float, board: Board, vfx_manager: "VFXManager") -> bool:
        self.elapsed_ms += dt_ms
        return self.elapsed_ms < self.duration_ms

    def render(self, surface: pygame.Surface, board: Board) -> None:
        cx, cy = board.get_tile_center(self.col, self.row)
        sz = board.tile_size
        t = self.elapsed_ms / self.duration_ms
        alpha = int(255 * (1.0 - t))

        slash_surf = pygame.Surface((sz, sz), pygame.SRCALPHA)
        col = (255, 220, 120, alpha) if self.is_heavy else (255, 255, 255, alpha)
        width = 4 if self.is_heavy else 3

        # Línea de tajo diagonal
        m = int(sz * 0.18)
        pygame.draw.line(slash_surf, col, (m, sz - m), (sz - m, m), width)
        if self.is_heavy:
            pygame.draw.line(slash_surf, (255, 80, 60, alpha), (m, m), (sz - m, sz - m), 2)

        surface.blit(slash_surf, (cx - sz // 2, cy - sz // 2))


class VFXManager:
    """Coordinador central de efectos visuales, partículas, sacudida de pantalla y animaciones activas."""

    def __init__(self):
        self.effects: list = []
        self.floating_texts: list[FloatingText] = []
        self.shake_duration_ms: float = 0.0
        self.shake_intensity: float = 0.0

    def trigger_screen_shake(self, duration_ms: float = 250.0, intensity: float = 5.0) -> None:
        """Activa una sacudida de pantalla sísmica para impactos pesados."""
        self.shake_duration_ms = max(self.shake_duration_ms, duration_ms)
        self.shake_intensity = max(self.shake_intensity, intensity)

    def get_shake_offset(self) -> tuple[int, int]:
        """Devuelve el desplazamiento (dx, dy) en píxeles si hay sacudida activa."""
        if self.shake_duration_ms > 0:
            dx = random.randint(-int(self.shake_intensity), int(self.shake_intensity))
            dy = random.randint(-int(self.shake_intensity), int(self.shake_intensity))
            return dx, dy
        return 0, 0

    def add_floating_text(self, x: float, y: float, text: str, color: tuple[int, int, int] = (255, 220, 100)) -> None:
        self.floating_texts.append(FloatingText(x, y, text, color))

    def spawn_fireball(self, target_c: int, target_r: int, on_impact=None, on_finish=None) -> None:
        self.effects.append(FireballVFX(target_c, target_r, on_impact, on_finish))

    def spawn_black_hole(self, col: int, row: int, on_complete=None) -> None:
        self.effects.append(BlackHoleVFX(col, row, on_complete))

    def spawn_arrow(self, start_c: int, start_r: int, target_c: int, target_r: int, on_impact=None, on_finish=None) -> None:
        self.effects.append(ArrowVFX(start_c, start_r, target_c, target_r, on_impact, on_finish))

    def spawn_summon(self, col: int, row: int, on_complete=None) -> None:
        self.effects.append(SummonVFX(col, row, on_complete))

    def spawn_shield_break(self, col: int, row: int) -> None:
        self.effects.append(ShieldBreakVFX(col, row))

    def spawn_slash(self, col: int, row: int, is_heavy: bool = False) -> None:
        self.effects.append(SlashVFX(col, row, is_heavy))

    def is_blocking(self) -> bool:
        """Determina si hay alguna animación cinemática mayor que debe bloquear clics temporalmente."""
        return any(getattr(e, "is_blocking", False) for e in self.effects)

    def update(self, dt_ms: float, board: Board) -> None:
        """Actualiza todos los efectos y el temporizador de sacudida de pantalla."""
        if self.shake_duration_ms > 0:
            self.shake_duration_ms -= dt_ms
            if self.shake_duration_ms <= 0:
                self.shake_intensity = 0.0

        # Actualizar efectos
        active_effects = []
        for effect in self.effects:
            if effect.update(dt_ms, board, self):
                active_effects.append(effect)
        self.effects = active_effects

        # Actualizar textos flotantes
        self.floating_texts = [ft for ft in self.floating_texts if ft.update(dt_ms)]

    def render(self, surface: pygame.Surface, board: Board) -> None:
        """Renderiza todos los efectos visuales y textos flotantes sobre el tablero."""
        for effect in self.effects:
            effect.render(surface, board)
        for ft in self.floating_texts:
            ft.render(surface)

    def clear(self) -> None:
        self.effects.clear()
        self.floating_texts.clear()
        self.shake_duration_ms = 0.0
        self.shake_intensity = 0.0
