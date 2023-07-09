@echo off

whoami /user | find /i "S-1-5-18" > nul 2>&1 || (
	call RunAsTI.cmd "%~f0" "%*"
	exit /b
)

SET mypath=%~dp0
cd %mypath%
powershell.exe -Command "& {python src/main.py %*}"
pause