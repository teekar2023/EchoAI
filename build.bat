@echo off
pyinstaller --hidden-import=pyttsx3.drivers.sapi5 -i echo.ico EchoAI.pyw
PAUSE