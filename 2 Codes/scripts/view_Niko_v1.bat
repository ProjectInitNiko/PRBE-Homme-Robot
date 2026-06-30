@echo off
REM Lance le viewer iDynTree sur examples\Niko_v1.urdf
REM Marche depuis n'importe ou tant que ce .bat reste dans scripts\

setlocal

set "SCRIPT_DIR=%~dp0"
set "REPO_ROOT=%SCRIPT_DIR%.."
set "VIEWER=%SCRIPT_DIR%view_urdf.py"
set "URDF=%REPO_ROOT%\examples\Niko_v1.urdf"

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

"%CONDA%" run -n hmgenv --no-capture-output python "%VIEWER%" "%URDF%"

pause
endlocal
