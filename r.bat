@echo off
cd vanalyzer
call npm run build
cd ..
python vanalyzer.py