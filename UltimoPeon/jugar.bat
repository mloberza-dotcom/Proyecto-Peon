@echo off
title El Ultimo Peon
python main.py
if %errorlevel% neq 0 (
    echo.
    echo Ocurrio un error al ejecutar el juego.
    pause
)
