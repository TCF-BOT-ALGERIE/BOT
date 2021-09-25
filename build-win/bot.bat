@echo off
echo Starting Server
start cmd /k Call "events.exe"
timeout 5

echo Starting updater
start cmd /k Call "updater.exe"
timeout 5

echo Starting main-bot
start cmd /k Call "run.exe"
timeout 5
