@echo off
title First Bot - Procesador de Solicitudes
echo ========================================
echo   First Bot - Procesador de Solicitudes
echo ========================================
echo.
echo Presiona Ctrl+C para detener el bot.
echo.

:loop
echo [%date% %time%] Ejecutando bot...
venv\Scripts\python -m src.first_bot.main
echo.
echo [%date% %time%] Esperando 60 segundos para la proxima ejecucion...
echo (Presiona cualquier tecla para pausar/reanudar)
timeout /t 60 /nobreak >nul
goto loop
