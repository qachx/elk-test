#!/bin/bash

echo "🏦 Starting Banking ELK Test Environment..."
echo "======================================"

# Проверяем, что Docker запущен
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker не запущен! Пожалуйста, запустите Docker Desktop."
    exit 1
fi

# Проверяем docker-compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose не найден! Пожалуйста, установите docker-compose."
    exit 1
fi

echo "✅ Docker и docker-compose доступны"

# Останавливаем существующие контейнеры если есть
echo "🛑 Останавливаем существующие контейнеры..."
docker-compose down

# Создаем необходимые папки
echo "📁 Создаем папки для логов..."
mkdir -p logs

# Запускаем все сервисы
echo "🚀 Запускаем все сервисы..."
docker-compose up -d

if [ $? -ne 0 ]; then
    echo "❌ Ошибка запуска! Проверьте порты или память Docker."
    exit 1
fi

echo ""
echo "✅ Сервисы запущены!"
echo ""
echo "🔧 Автонастройка Kibana..."
echo "Создаются Data Views и дашборды автоматически."
echo ""
echo "⏳ Ожидание полной инициализации (3-4 минуты)..."
echo ""

# Ждем запуска Elasticsearch
echo "🔍 Ожидание Elasticsearch..."
while ! curl -s http://localhost:9200/_cluster/health >/dev/null 2>&1; do
    echo "   Elasticsearch еще не готов, ждем..."
    sleep 5
done
echo "✅ Elasticsearch запущен"

# Ждем запуска Kibana
echo "📊 Ожидание Kibana..."
while ! curl -s http://localhost:5601/api/status >/dev/null 2>&1; do
    echo "   Kibana еще не готова, ждем..."
    sleep 5
done
echo "✅ Kibana запущена"

# Ждем запуска Grafana
echo "📈 Ожидание Grafana..."
while ! curl -s http://localhost:3000/api/health >/dev/null 2>&1; do
    echo "   Grafana еще не готова, ждем..."
    sleep 5
done
echo "✅ Grafana запущена"

echo ""
echo "🎉 Все сервисы запущены! Теперь можно открывать интерфейсы:"
echo ""
echo "📊 Kibana:      http://localhost:5601"
echo "📈 Grafana:     http://localhost:3000 (admin/admin)"
echo "🔍 Prometheus:  http://localhost:9090"
echo "⚡ Elasticsearch: http://localhost:9200"
echo ""
echo "💡 Генераторы логов уже работают в фоне!"
echo "💡 Данные и дашборды появятся через 3-4 минуты."
echo "💡 Проверьте прогресс: docker logs setup-init"
echo ""
echo "📋 Откройте README.md для выполнения практических заданий!"
echo ""
echo "🛑 Для остановки: docker-compose down" 