"""Sintetizador procedural de efectos de sonido y música medieval en memoria.
Genera audio PCM de 16 bits sin requerir archivos WAV/MP3 externos.
"""
import array
import math
import random
import pygame

SAMPLE_RATE = 22050


def _create_sound_from_samples(samples: list[float]) -> pygame.mixer.Sound:
    """Convierte una lista de muestras flotantes (-1.0 a 1.0) en un objeto Sound de Pygame."""
    clean_samples = []
    for s in samples:
        val = s.real if isinstance(s, complex) else s
        clamped = max(-1.0, min(1.0, float(val)))
        clean_samples.append(int(clamped * 32767))
    int_samples = array.array("h", clean_samples)
    return pygame.mixer.Sound(buffer=int_samples)


# =========================================================================
# GENERADORES DE EFECTOS DE SONIDO (SFX)
# =========================================================================

def synth_wooden_step() -> pygame.mixer.Sound:
    """Sonido de paso o clic de madera tallada."""
    duration = 0.07
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    freq = 180.0

    for i in range(num_samples):
        t = i / SAMPLE_RATE
        env = max(0.0, 1.0 - t / duration) ** 2
        val = (2.0 * abs(2.0 * ((t * freq) % 1.0) - 1.0) - 1.0) * 0.7
        val += (random.random() * 2.0 - 1.0) * 0.3
        samples.append(val * env * 0.6)

    return _create_sound_from_samples(samples)


def synth_capture_slash() -> pygame.mixer.Sound:
    """Sonido de corte / golpe de madera al capturar una pieza."""
    duration = 0.16
    num_samples = int(SAMPLE_RATE * duration)
    samples = []

    for i in range(num_samples):
        t = min(1.0, i / num_samples)
        env = max(0.0, 1.0 - t) ** 1.5
        freq = 380.0 - 240.0 * t
        saw = 2.0 * ((i * freq / SAMPLE_RATE) % 1.0) - 1.0
        noise = random.random() * 2.0 - 1.0
        samples.append((saw * 0.6 + noise * 0.4) * env * 0.7)

    return _create_sound_from_samples(samples)


def synth_enemy_attack() -> pygame.mixer.Sound:
    """Sonido grave de ataque enemigo / impacto contundente."""
    duration = 0.22
    num_samples = int(SAMPLE_RATE * duration)
    samples = []

    for i in range(num_samples):
        t = min(1.0, i / num_samples)
        env = max(0.0, 1.0 - t) ** 2
        freq = 120.0 - 70.0 * t
        wave = math.sin(2.0 * math.pi * freq * (i / SAMPLE_RATE))
        noise = (random.random() * 2.0 - 1.0) * max(0.0, 1.0 - t) * 0.3
        samples.append((wave * 0.7 + noise) * env * 0.8)

    return _create_sound_from_samples(samples)


def synth_bear_trap() -> pygame.mixer.Sound:
    """Sonido de cepo metálico cerrándose de golpe."""
    duration = 0.18
    num_samples = int(SAMPLE_RATE * duration)
    samples = []

    for i in range(num_samples):
        t = min(1.0, i / num_samples)
        env = max(0.0, 1.0 - t) ** 3
        noise = (random.random() * 2.0 - 1.0)
        ring = math.sin(2.0 * math.pi * 1200.0 * (i / SAMPLE_RATE)) * 0.4
        samples.append((noise * 0.7 + ring) * env * 0.9)

    return _create_sound_from_samples(samples)


def synth_lava_sizzle() -> pygame.mixer.Sound:
    """Sonido de ebullición / magma ardiente."""
    duration = 0.28
    num_samples = int(SAMPLE_RATE * duration)
    samples = []

    for i in range(num_samples):
        t = min(1.0, i / num_samples)
        env = max(0.0, math.sin(t * math.pi))
        bubble = math.sin(2.0 * math.pi * (80.0 + random.randint(-15, 15)) * (i / SAMPLE_RATE))
        noise = (random.random() * 2.0 - 1.0) * 0.5
        samples.append((bubble * 0.5 + noise * 0.5) * env * 0.7)

    return _create_sound_from_samples(samples)


def synth_summon_horn() -> pygame.mixer.Sound:
    """Sonido de trompeta / cuerno de guerra medieval al invocar al caballo."""
    duration = 0.45
    num_samples = int(SAMPLE_RATE * duration)
    samples = []

    notes = [261.63, 329.63, 392.00]
    for i in range(num_samples):
        t = min(1.0, i / num_samples)
        env = max(0.0, math.sin(t * math.pi * 0.8)) * max(0.0, 1.0 - t * 0.3)
        val = sum(math.sin(2.0 * math.pi * n * (i / SAMPLE_RATE)) for n in notes) / len(notes)
        samples.append(val * env * 0.7)

    return _create_sound_from_samples(samples)


def synth_black_hole_whoosh() -> pygame.mixer.Sound:
    """Sonido de vórtice cósmico abisal."""
    duration = 0.5
    num_samples = int(SAMPLE_RATE * duration)
    samples = []

    for i in range(num_samples):
        t = min(1.0, i / num_samples)
        env = max(0.0, math.sin(t * math.pi))
        freq = 300.0 * (1.0 - t * 0.6) + math.sin(t * 20.0) * 40.0
        wave = math.sin(2.0 * math.pi * freq * (i / SAMPLE_RATE))
        noise = (random.random() * 2.0 - 1.0) * 0.25
        samples.append((wave * 0.7 + noise) * env * 0.8)

    return _create_sound_from_samples(samples)


def synth_fireball_boom() -> pygame.mixer.Sound:
    """Sonido de explosión y llamarada de magma."""
    duration = 0.38
    num_samples = int(SAMPLE_RATE * duration)
    samples = []

    for i in range(num_samples):
        t = min(1.0, i / num_samples)
        env = max(0.0, 1.0 - t) ** 1.8
        freq = 150.0 - 90.0 * t
        wave = math.sin(2.0 * math.pi * freq * (i / SAMPLE_RATE))
        noise = (random.random() * 2.0 - 1.0) * 0.6
        samples.append((wave * 0.4 + noise * 0.6) * env * 0.8)

    return _create_sound_from_samples(samples)


def synth_arrow_whistle() -> pygame.mixer.Sound:
    """Silbido de flecha perforante en vuelo e impacto."""
    duration = 0.2
    num_samples = int(SAMPLE_RATE * duration)
    samples = []

    for i in range(num_samples):
        t = min(1.0, i / num_samples)
        env = max(0.0, 1.0 - t) ** 1.2
        freq = 450.0 + 350.0 * t
        wave = math.sin(2.0 * math.pi * freq * (i / SAMPLE_RATE))
        samples.append(wave * env * 0.6)

    return _create_sound_from_samples(samples)


def synth_ui_click() -> pygame.mixer.Sound:
    """Clic sutil para botones e interfaz."""
    duration = 0.04
    num_samples = int(SAMPLE_RATE * duration)
    samples = []

    for i in range(num_samples):
        t = min(1.0, i / num_samples)
        env = max(0.0, 1.0 - t)
        wave = math.sin(2.0 * math.pi * 700.0 * (i / SAMPLE_RATE))
        samples.append(wave * env * 0.5)

    return _create_sound_from_samples(samples)


# =========================================================================
# GENERADORES DE MÚSICA PROCEDURAL MEDIEVAL (BUCLES LOOPABLES)
# =========================================================================

def synth_medieval_menu_track() -> pygame.mixer.Sound:
    """Pista épica medieval para el Menú: progresión menor con percusión rítmica."""
    duration = 9.6
    num_samples = int(SAMPLE_RATE * duration)
    samples = [0.0] * num_samples

    chord_bass = [146.83, 116.54, 130.81, 110.00]
    melody_notes = [
        (293.66, 0.0, 0.6), (349.23, 0.6, 0.6), (440.00, 1.2, 1.2),
        (466.16, 2.4, 0.6), (440.00, 3.0, 0.6), (349.23, 3.6, 1.2),
        (392.00, 4.8, 0.6), (349.23, 5.4, 0.6), (329.63, 6.0, 1.2),
        (293.66, 7.2, 0.6), (261.63, 7.8, 0.6), (293.66, 8.4, 1.2),
    ]

    # 1. Bajo rítmico continuo
    bar_duration = 2.4
    for bar in range(4):
        base_freq = chord_bass[bar]
        bar_start = int(bar * bar_duration * SAMPLE_RATE)
        bar_len = int(bar_duration * SAMPLE_RATE)

        for i in range(bar_len):
            idx = bar_start + i
            if idx >= num_samples:
                break
            t = i / SAMPLE_RATE
            env = 0.5 + 0.3 * math.sin(t * math.pi * 4)
            bass_val = math.sin(2.0 * math.pi * base_freq * t)
            samples[idx] += bass_val * env * 0.25

    # 2. Percusión de tambor de guerra en cada tiempo (cada 0.6s)
    beat_step = 0.6
    num_beats = int(duration / beat_step)
    for b in range(num_beats):
        b_start = int(b * beat_step * SAMPLE_RATE)
        drum_len = int(0.12 * SAMPLE_RATE)
        for i in range(drum_len):
            idx = b_start + i
            if idx >= num_samples:
                break
            t = i / drum_len
            drum_env = max(0.0, 1.0 - t) ** 3
            drum_val = (math.sin(2.0 * math.pi * (80.0 - 40.0 * t) * (i / SAMPLE_RATE)) * 0.7
                        + (random.random() * 2.0 - 1.0) * 0.3)
            samples[idx] += drum_val * drum_env * 0.35

    # 3. Melodía medieval
    for freq, start_sec, dur_sec in melody_notes:
        start_idx = int(start_sec * SAMPLE_RATE)
        len_idx = int(dur_sec * SAMPLE_RATE)
        for i in range(len_idx):
            idx = start_idx + i
            if idx >= num_samples:
                break
            t = i / len_idx
            env = max(0.0, math.sin(t * math.pi)) * 0.8
            mel_val = (
                math.sin(2.0 * math.pi * freq * (i / SAMPLE_RATE)) * 0.6
                + math.sin(2.0 * math.pi * (freq * 2) * (i / SAMPLE_RATE)) * 0.25
                + math.sin(2.0 * math.pi * (freq * 3) * (i / SAMPLE_RATE)) * 0.15
            )
            samples[idx] += mel_val * env * 0.3

    return _create_sound_from_samples(samples)


def synth_shield_break() -> pygame.mixer.Sound:
    """Sonido metálico de escudo rúnico al quebrarse."""
    duration = 0.25
    num_samples = int(SAMPLE_RATE * duration)
    samples = []

    for i in range(num_samples):
        t = min(1.0, i / num_samples)
        env = max(0.0, 1.0 - t) ** 2.2
        # Frecuencias disonantes de metal quebrado
        chime1 = math.sin(2.0 * math.pi * 980.0 * (i / SAMPLE_RATE)) * 0.4
        chime2 = math.sin(2.0 * math.pi * 1420.0 * (i / SAMPLE_RATE)) * 0.3
        chime3 = math.sin(2.0 * math.pi * 560.0 * (i / SAMPLE_RATE)) * 0.3
        crack = (random.random() * 2.0 - 1.0) * max(0.0, 1.0 - t * 3.0) * 0.6
        samples.append((chime1 + chime2 + chime3 + crack) * env * 0.8)

    return _create_sound_from_samples(samples)


def synth_boss_hit() -> pygame.mixer.Sound:
    """Sonido de impacto demoledor contra el Rey Gigante."""
    duration = 0.35
    num_samples = int(SAMPLE_RATE * duration)
    samples = []

    for i in range(num_samples):
        t = min(1.0, i / num_samples)
        env = max(0.0, 1.0 - t) ** 1.8
        freq = 95.0 - 45.0 * t
        bass = math.sin(2.0 * math.pi * freq * (i / SAMPLE_RATE)) * 0.7
        gong = math.sin(2.0 * math.pi * 210.0 * (i / SAMPLE_RATE)) * 0.3 * math.exp(-t * 4.0)
        noise = (random.random() * 2.0 - 1.0) * max(0.0, 1.0 - t * 2.0) * 0.4
        samples.append((bass + gong + noise) * env * 0.85)

    return _create_sound_from_samples(samples)


def synth_rift_shatter() -> pygame.mixer.Sound:
    """Sonido de fractura del tablero al dividirse en dos."""
    duration = 0.45
    num_samples = int(SAMPLE_RATE * duration)
    samples = []

    for i in range(num_samples):
        t = min(1.0, i / num_samples)
        env = max(0.0, 1.0 - t) ** 1.4
        quake = math.sin(2.0 * math.pi * (65.0 - 25.0 * t) * (i / SAMPLE_RATE)) * 0.6
        rock_crack = (random.random() * 2.0 - 1.0) * 0.5
        samples.append((quake + rock_crack) * env * 0.8)

    return _create_sound_from_samples(samples)


def synth_game_calm_track() -> pygame.mixer.Sound:
    """Pista medieval rica y atmosférica para los primeros niveles (Niveles 1 a 3), variada y no repetitiva."""
    duration = 19.2  # 8 compases de 2.4s cada uno
    num_samples = int(SAMPLE_RATE * duration)
    samples = [0.0] * num_samples

    # Progresión armónica:
    # Compás 1-2: Re menor (Dm)
    # Compás 3-4: Sib mayor (Bb) -> Do mayor (C)
    # Compás 5-6: Fa mayor (F) -> La menor (Am)
    # Compás 7-8: Sol menor (Gm) -> Re menor (Dm)
    chords = [
        # (Bajo Hz, notas de arpegio Hz)
        (146.83, [146.83, 220.00, 293.66, 349.23, 440.00, 349.23, 293.66, 220.00]),  # Dm
        (146.83, [220.00, 293.66, 349.23, 440.00, 523.25, 440.00, 349.23, 293.66]),  # Dm variation
        (116.54, [116.54, 174.61, 233.08, 293.66, 349.23, 293.66, 233.08, 174.61]),  # Bb
        (130.81, [130.81, 164.81, 196.00, 261.63, 329.63, 261.63, 196.00, 164.81]),  # C
        (174.61, [174.61, 220.00, 261.63, 349.23, 440.00, 349.23, 261.63, 220.00]),  # F
        (110.00, [110.00, 164.81, 220.00, 261.63, 329.63, 261.63, 220.00, 164.81]),  # Am
        (98.00,  [98.00,  146.83, 196.00, 233.08, 293.66, 233.08, 196.00, 146.83]),  # Gm
        (146.83, [146.83, 220.00, 293.66, 349.23, 440.00, 349.23, 293.66, 220.00]),  # Dm resolucion
    ]

    bar_sec = 2.4

    # 1. Capa de arpa y laúd con bajo cálido
    for bar_idx, (bass_freq, arp_notes) in enumerate(chords):
        bar_start_sample = int(bar_idx * bar_sec * SAMPLE_RATE)

        # Bajo sostenido con caída lenta tipo violonchelo medieval
        bar_len = int(bar_sec * SAMPLE_RATE)
        for i in range(bar_len):
            idx = bar_start_sample + i
            if idx >= num_samples:
                break
            t = i / SAMPLE_RATE
            bass_env = math.exp(-t * 0.8) * 0.18
            # Armónicos suaves
            bass_wave = (
                math.sin(2.0 * math.pi * bass_freq * t) * 0.75
                + math.sin(2.0 * math.pi * (bass_freq * 2) * t) * 0.25
            )
            samples[idx] += bass_wave * bass_env

        # 8 pulsos de arpegio por compás
        note_step = bar_sec / len(arp_notes)
        for note_idx, note_f in enumerate(arp_notes):
            n_start = bar_start_sample + int(note_idx * note_step * SAMPLE_RATE)
            n_len = int(0.7 * SAMPLE_RATE)
            for j in range(n_len):
                idx = n_start + j
                if idx >= num_samples:
                    break
                t_n = j / SAMPLE_RATE
                env_arp = math.exp(-t_n * 3.2) * 0.20
                arp_wave = (
                    math.sin(2.0 * math.pi * note_f * t_n) * 0.8
                    + math.sin(2.0 * math.pi * (note_f * 2) * t_n) * 0.2
                )
                samples[idx] += arp_wave * env_arp

    # 2. Capa melódica de flauta / zanfoña medieval lírica que entra a partir del segundo tercio
    flute_notes = [
        # (Frecuencia Hz, inicio en seg, duración seg)
        (440.00, 4.8, 1.2),  # La
        (466.16, 6.0, 0.6),  # Sib
        (523.25, 6.6, 0.6),  # Do
        (440.00, 7.2, 1.8),  # La sostenido
        (349.23, 9.6, 1.0),  # Fa
        (392.00, 10.8, 0.8), # Sol
        (440.00, 11.6, 0.8), # La
        (329.63, 12.4, 1.6), # Mi
        (392.00, 14.4, 1.0), # Sol
        (349.23, 15.6, 0.8), # Fa
        (329.63, 16.4, 0.8), # Mi
        (293.66, 17.2, 2.0), # Re (cierre sereno y místico)
    ]

    for f_freq, f_start_sec, f_dur_sec in flute_notes:
        f_start_idx = int(f_start_sec * SAMPLE_RATE)
        f_len_idx = int(f_dur_sec * SAMPLE_RATE)
        for k in range(f_len_idx):
            idx = f_start_idx + k
            if idx >= num_samples:
                break
            t_f = k / f_len_idx
            # Envolvente suave con leve vibrato humano
            env_f = math.sin(t_f * math.pi) * 0.22
            vibrato = 1.0 + 0.012 * math.sin(t_f * 28.0)
            flute_wave = (
                math.sin(2.0 * math.pi * (f_freq * vibrato) * (k / SAMPLE_RATE)) * 0.75
                + math.sin(2.0 * math.pi * (f_freq * 2 * vibrato) * (k / SAMPLE_RATE)) * 0.18
                + math.sin(2.0 * math.pi * (f_freq * 3 * vibrato) * (k / SAMPLE_RATE)) * 0.07
            )
            samples[idx] += flute_wave * env_f

    return _create_sound_from_samples(samples)


def synth_game_tense_track() -> pygame.mixer.Sound:
    """Pista de tensión media con arpegios y pulso rítmico (Niveles 4 a 7)."""
    duration = 8.0
    num_samples = int(SAMPLE_RATE * duration)
    samples = [0.0] * num_samples

    bass_freq = 110.0
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        pulse = 0.5 + 0.5 * math.sin(t * math.pi * 3)
        samples[i] += math.sin(2.0 * math.pi * bass_freq * t) * pulse * 0.22

    notes = [220.00, 261.63, 293.66, 329.63, 349.23, 293.66]
    note_step = 0.45
    for idx, f in enumerate(notes * 3):
        start_i = int(idx * note_step * SAMPLE_RATE)
        note_len = int(0.5 * SAMPLE_RATE)
        for i in range(note_len):
            target_idx = start_i + i
            if target_idx >= num_samples:
                break
            t = i / note_len
            env = max(0.0, 1.0 - t) ** 1.5
            val = math.sin(2.0 * math.pi * f * (i / SAMPLE_RATE))
            samples[target_idx] += val * env * 0.22

    return _create_sound_from_samples(samples)
