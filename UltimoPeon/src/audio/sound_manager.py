"""Gestor central de audio y música dinámica adaptativa para 'El Último Peón'."""
import pygame
from src.audio.sound_synthesizer import (
    synth_wooden_step,
    synth_capture_slash,
    synth_enemy_attack,
    synth_bear_trap,
    synth_lava_sizzle,
    synth_summon_horn,
    synth_black_hole_whoosh,
    synth_fireball_boom,
    synth_arrow_whistle,
    synth_ui_click,
    synth_shield_break,
    synth_boss_hit,
    synth_rift_shatter,
    synth_medieval_menu_track,
    synth_game_calm_track,
    synth_game_tense_track,
)


class SoundManager:
    """Controla la reproducción de efectos sonoros y música ambiental adaptativa por niveles."""

    def __init__(self):
        self.enabled = False
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.enabled = True
        except pygame.error:
            self.enabled = False

        self.music_volume: float = 0.65
        self.sfx_volume: float = 0.8
        self.current_track_name: str | None = None

        self.sfx_cache: dict[str, pygame.mixer.Sound] = {}
        self.music_cache: dict[str, pygame.mixer.Sound] = {}

        if self.enabled:
            self._load_sounds()
            # Canal 0 dedicado exclusivamente a la música en bucle
            self.music_channel = pygame.mixer.Channel(0)
        else:
            self.music_channel = None

    def _load_sounds(self) -> None:
        """Sintetiza y almacena en caché todos los efectos y temas musicales."""
        try:
            self.sfx_cache = {
                "step": synth_wooden_step(),
                "capture": synth_capture_slash(),
                "enemy_attack": synth_enemy_attack(),
                "bear_trap": synth_bear_trap(),
                "lava": synth_lava_sizzle(),
                "summon": synth_summon_horn(),
                "black_hole": synth_black_hole_whoosh(),
                "fireball": synth_fireball_boom(),
                "arrow": synth_arrow_whistle(),
                "click": synth_ui_click(),
                "shield_break": synth_shield_break(),
                "boss_hit": synth_boss_hit(),
                "rift": synth_rift_shatter(),
            }

            self.music_cache = {
                "menu": synth_medieval_menu_track(),
                "calm": synth_game_calm_track(),
                "tense": synth_game_tense_track(),
                "epic": synth_medieval_menu_track(),  # En niveles 8-10 suena el tema épico del castillo
            }
        except Exception:
            self.enabled = False

    def play_sfx(self, name: str) -> None:
        """Reproduce un efecto de sonido según el volumen de efectos configurado."""
        if not self.enabled or self.sfx_volume <= 0.01:
            return

        sound = self.sfx_cache.get(name)
        if sound:
            sound.set_volume(self.sfx_volume)
            sound.play()

    def play_music_for_level(self, level: int) -> None:
        """
        Selecciona y reproduce la pista musical adaptativa según el nivel del jugador:
        - Niveles 1 a 3: 'calm' (Música tranquila de arpa/laúd)
        - Niveles 4 a 7: 'tense' (Música de tensión medieval con bajo y pulso)
        - Niveles 8 a 10: 'epic' (Tema épico orquestal con tambores de guerra)
        """
        if level <= 3:
            track = "calm"
        elif level <= 7:
            track = "tense"
        else:
            track = "epic"

        self.play_music(track)

    def play_music(self, track_name: str) -> None:
        """Reproduce en bucle la pista indicada si no está ya activa."""
        if not self.enabled or not self.music_channel:
            return

        if self.current_track_name == track_name and self.music_channel.get_busy():
            return

        sound = self.music_cache.get(track_name)
        if sound:
            self.current_track_name = track_name
            self.music_channel.set_volume(self.music_volume)
            self.music_channel.play(sound, loops=-1)

    def set_music_volume(self, vol: float) -> None:
        """Ajusta el volumen de la música (0.0 a 1.0)."""
        self.music_volume = max(0.0, min(1.0, round(vol, 2)))
        if self.music_channel:
            self.music_channel.set_volume(self.music_volume)

    def set_sfx_volume(self, vol: float) -> None:
        """Ajusta el volumen de los efectos sonoros (0.0 a 1.0)."""
        self.sfx_volume = max(0.0, min(1.0, round(vol, 2)))

    def stop_music(self) -> None:
        """Detiene la música activa."""
        if self.music_channel:
            self.music_channel.stop()
        self.current_track_name = None
