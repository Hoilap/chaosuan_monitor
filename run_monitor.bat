@echo off
:: 1. 进入脚本所在目录
cd /d %~dp0

:: 2. 在后台最小化窗口运行 monitor.py
:: uv run 会自动寻找并激活虚拟环境，如果没环境会自动创建
start uv run python monitor.py

echo Monitoring script started in the background.
pause