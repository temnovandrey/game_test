"""
Утилита для генерации звуковых эффектов.
Запустите один раз для создания аудио-ассетов.
"""
import wave
import struct
import math
import os

SAMPLE_RATE = 44100


def generate_tone(filename: str, frequency: float, duration: float = 0.15,
                  sample_rate: int = SAMPLE_RATE, amplitude: float = 0.5,
                  wave_type: str = "sine"):
    """Генерирует один тон в WAV файл."""
    num_samples = int(sample_rate * duration)
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        for i in range(num_samples):
            t = i / sample_rate
            if wave_type == "sine":
                value = int(amplitude * 32767 * math.sin(2 * math.pi * frequency * t))
            elif wave_type == "square":
                value = int(amplitude * 32767 * (1 if math.sin(2 * math.pi * frequency * t) >= 0 else -1))
            else:
                value = int(amplitude * 32767 * math.sin(2 * math.pi * frequency * t))
            # Clamp value
            value = max(-32768, min(32767, value))
            data = struct.pack('<h', value)
            wav_file.writeframes(data)


def generate_coin():
    """Короткий высокий звук 'динь' для сбора монеты."""
    generate_tone("assets/sounds/coin.wav", 880, 0.12, amplitude=0.6)


def generate_hit():
    """Низкий звук удара."""
    generate_tone("assets/sounds/hit.wav", 150, 0.25, amplitude=0.8, wave_type="square")


def generate_win():
    """Восходящая арпеджио для победы."""
    notes = [(523.25, 0.08), (659.25, 0.08), (783.99, 0.08), (1046.50, 0.15)]
    with wave.open("assets/sounds/win.wav", 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        for freq, dur in notes:
            num_samples = int(SAMPLE_RATE * dur)
            for i in range(num_samples):
                t = i / SAMPLE_RATE
                value = int(0.5 * 32767 * math.sin(2 * math.pi * freq * t))
                value = max(-32768, min(32767, value))
                data = struct.pack('<h', value)
                wav_file.writeframes(data)


def generate_lose():
    """Нисходящие тона для поражения."""
    notes = [(523.25, 0.1), (440.00, 0.1), (349.23, 0.1), (261.63, 0.2)]
    with wave.open("assets/sounds/lose.wav", 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        for freq, dur in notes:
            num_samples = int(SAMPLE_RATE * dur)
            for i in range(num_samples):
                t = i / SAMPLE_RATE
                value = int(0.5 * 32767 * math.sin(2 * math.pi * freq * t))
                value = max(-32768, min(32767, value))
                data = struct.pack('<h', value)
                wav_file.writeframes(data)


def generate_menu_select():
    """Короткий клик для выбора в меню."""
    generate_tone("assets/sounds/menu_select.wav", 1000, 0.04, amplitude=0.3)


def generate_background():
    """Фоновая ambient музыка — тихий низкий тон."""
    duration = 5.0
    num_samples = int(SAMPLE_RATE * duration)
    with wave.open("assets/music/background.wav", 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            # Низкая синусоида с лёгкой модуляцией
            freq = 60 + 10 * math.sin(2 * math.pi * 0.2 * t)
            value = int(0.15 * 32767 * math.sin(2 * math.pi * freq * t))
            value = max(-32768, min(32767, value))
            data = struct.pack('<h', value)
            wav_file.writeframes(data)


def main():
    os.makedirs("assets/sounds", exist_ok=True)
    os.makedirs("assets/music", exist_ok=True)

    print("Генерация звуковых эффектов...")
    generate_coin()
    print("  coin.wav")
    generate_hit()
    print("  hit.wav")
    generate_win()
    print("  win.wav")
    generate_lose()
    print("  lose.wav")
    generate_menu_select()
    print("  menu_select.wav")
    generate_background()
    print("  background.wav")
    print("Все звуки сгенерированы!")


if __name__ == "__main__":
    main()
