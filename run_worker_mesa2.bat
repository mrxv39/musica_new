@echo off
title Worker Mesa 2

cd /d C:\Users\Usuario\Desktop\projectos\musica_new

echo ==========================================
echo   Lanzando Worker SOLO para Mesa 2
echo ==========================================
echo.

REM ROI Mesa 2 (AJUSTA SI ES NECESARIO)
set X1=1300
set Y1=210
set X2=2076
set Y2=807

python -u workers\worker.py ^
    --mesa 2 ^
    --x1 %X1% ^
    --y1 %Y1% ^
    --x2 %X2% ^
    --y2 %Y2% ^
    --interval-ms 1000 ^
    --log-every-ms 1000

pause
