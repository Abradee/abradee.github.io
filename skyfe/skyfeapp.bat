@echo off
echo Opening 30 tabs in Microsoft Edge...

FOR /L %%A IN (1,1,30) DO (
   start "" msedge "https://google.com"
   timeout /nobreak /t 1 >nul
)

echo Waiting 10 seconds before closing Edge...
timeout /t 10

echo Closing Edge...
taskkill /f /im msedge.exe

echo Done.
pause
