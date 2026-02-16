@echo off
cd /d %~dp0

echo =====================================
echo   Iniciando musica_new workers
echo =====================================

echo Lanzando Mesa 1...
start "Mesa 1" cmd /k python workers\worker.py --mesa 1 --x1 520 --y1 210 --x2 1296 --y2 807 --interval-ms 1000 --log-every-ms 500

echo Lanzando Mesa 2...
start "Mesa 2" cmd /k python workers\worker.py --mesa 2 --x1 520 --y1 807 --x2 1296 --y2 1404 --interval-ms 1000 --log-every-ms 500

echo Lanzando Mesa 3...
start "Mesa 3" cmd /k python workers\worker.py --mesa 3 --x1 1296 --y1 210 --x2 2072 --y2 807 --interval-ms 1000 --log-every-ms 500

echo Lanzando Mesa 4...
start "Mesa 4" cmd /k python workers\worker.py --mesa 4 --x1 1296 --y1 807 --x2 2072 --y2 1404 --interval-ms 1000 --log-every-ms 500

echo.
echo Todos los workers lanzados.
echo.
pause
