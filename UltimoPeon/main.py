"""Punto de entrada principal para 'El Último Peón'.

Ejecuta este archivo para iniciar el juego:
    python main.py
"""
import sys
from src.core.game import Game


def main():
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"Error durante la ejecución del juego: {e}", file=sys.stderr)
        raise e


if __name__ == "__main__":
    main()
