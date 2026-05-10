@echo off
REM Drag & drop d'un fichier .urdf sur ce .bat pour le visualiser

setlocal

if "%~1"=="" (
    echo Usage : glisse-depose un fichier .urdf sur ce .bat
    pause
    exit /b 1
)

set "SCRIPT_DIR=%~dp0"
set "VIEWER=%SCRIPT_DIR%view_urdf.py"

REM Detection conda : essaie le PATH d'abord, puis emplacements typiques
where conda >nul 2>&1
if %errorlevel% equ 0 (
    set "CONDA=conda"
) else (
    if exist "C:\ProgramData\miniconda3\Scripts\conda.exe" (
        set "CONDA=C:\ProgramData\miniconda3\Scripts\conda.exe"
    ) else if exist "%USERPROFILE%\miniconda3\Scripts\conda.exe" (
        set "CONDA=%USERPROFILE%\miniconda3\Scripts\conda.exe"
    ) else if exist "%USERPROFILE%\Anaconda3\Scripts\conda.exe" (
        set "CONDA=%USERPROFILE%\Anaconda3\Scripts\conda.exe"
    ) else (
        echo [ERR] conda introuvable. Voir INSTALL.md.
        pause
        exit /b 1
    )
)

"%CONDA%" run -n hmgenv --no-capture-output python "%VIEWER%" "%~1"

pause
endlocal
