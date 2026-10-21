@echo off
chcp 65001 >nul
title GOOGLE FLOW AUTO GENERATOR (CANH 24 DEN 143)

echo ==========================================================
echo       KHOI DONG TU DONG HOA GOOGLE FLOW PRO (CANH 24-143)
echo ==========================================================
echo.
echo 1. Dang khoi dong bo lang nghe tu dong luu file anh...
start "" python "C:\Users\VNTT\.gemini\antigravity-ide\scratch\organize_downloads.py"

echo 2. Dang khoi dong Chrome voi tien ich Auto-Bot tich hop...
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --profile-directory="Profile 2" --load-extension="C:\Users\VNTT\.gemini\antigravity-ide\scratch\flow-extension" "https://flow.google.com/u/1/project/8eda747b-1aff-4f13-a079-c9bcecc6c2c2"

echo.
echo ==========================================================
echo  DA KHOI DONG THANH CONG!
echo  Trang Google Flow dang mo tren trinh duyet Chrome cua ban.
echo  Hop thoai Auto-Bot se tu dong ve va tai tu canh 24 den 143!
echo ==========================================================
timeout /t 5 >nul 2>&1
