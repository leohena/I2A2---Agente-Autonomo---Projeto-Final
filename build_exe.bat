@echo off
echo ============================================================
echo  CONT-AI - Gerador de Executavel
echo ============================================================
echo.
echo Instalando PyInstaller...
pip install pyinstaller
echo.
echo ============================================================
echo Gerando executavel... (isso pode demorar alguns minutos)
echo ============================================================
echo.
pyinstaller CONT-AI.spec --clean
echo.
echo ============================================================
echo Processo concluido!
echo ============================================================
echo.
echo O executavel esta em: dist\CONT-AI.exe
echo.
pause
