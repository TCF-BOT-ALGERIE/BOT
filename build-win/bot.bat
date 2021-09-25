@echo off
echo Starting Server
call "events.exe"
timeout 5

echo Starting updater
call "updater.exe"
timeout 5

echo Starting main-bot
call "run.exe"
timeout 5
