@echo off
chcp 65001 >nul

echo Banking ELK Test Environment
echo =============================

echo [1] Checking Docker...
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker not running! Start Docker Desktop first.
    pause
    exit /b 1
)
echo [OK] Docker ready

echo [2] Stopping old containers...
docker-compose down -v 2>nul

echo [3] Creating logs folder...
if not exist logs mkdir logs

echo [4] Starting services...
docker-compose up -d
if errorlevel 1 (
    echo [ERROR] Failed to start! Check ports or Docker memory.
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Services started!
echo.
echo [5] Auto-configuring Kibana...
echo This will create Data Views and dashboards automatically.
echo.
echo Open these URLs:
echo   Kibana:     http://localhost:5601
echo   Grafana:    http://localhost:3000 (admin/admin)
echo   Prometheus: http://localhost:9090
echo.
echo [INFO] Data and dashboards will appear in 3-4 minutes.
echo [INFO] Check docker logs setup-init to see setup progress.
echo.
echo To stop: docker-compose down
echo.
pause 