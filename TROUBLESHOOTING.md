# 🔧 Устранение проблем

## Частые проблемы и решения

### 🐳 Docker проблемы

#### Проблема: "Docker not running"
**Решение:**
1. Запустите Docker Desktop
2. Дождитесь полной инициализации
3. Проверьте: `docker --version`

#### Проблема: "Port already in use"
**Решение:**
```bash
# Остановите конфликтующие контейнеры
docker-compose down
# Или найдите процесс на порту
netstat -tulpn | grep :5601
kill -9 [PID]
```

#### Проблема: "Not enough memory"
**Решение:**
1. Увеличьте память для Docker (Settings → Resources → Memory)
2. Минимум 4GB, рекомендуется 8GB

#### Проблема: Кракозябры в start.bat (Windows)
**Решение:**
1. Файл `start.bat` уже настроен для UTF-8
2. Если проблемы продолжаются: `chcp 65001`

### 📊 ELK Stack проблемы

#### Проблема: Elasticsearch не стартует
**Решение:**
1. Проверьте логи: `docker logs elasticsearch`
2. Увеличьте vm.max_map_count:
   ```bash
   # Linux/Mac
   sudo sysctl -w vm.max_map_count=262144
   
   # Windows (в WSL)
   wsl -d docker-desktop
   sysctl -w vm.max_map_count=262144
   ```

#### Проблема: Kibana показывает "Elasticsearch unavailable"
**Решение:**
1. Дождитесь запуска Elasticsearch (может занять 2-3 минуты)
2. Проверьте: `curl http://localhost:9200/_cluster/health`

#### Проблема: Нет данных в Kibana
**Решение:**
1. Проверьте автонастройку: `docker logs setup-init`
2. Проверьте логи генераторов: `docker logs auth-service-logs`
3. Проверьте Logstash: `docker logs logstash`
4. Убедитесь что папка logs создана: `ls -la logs/`
5. Подождите 3-4 минуты для полной инициализации

#### Проблема: Нет Data View в Kibana
**Решение:**
1. Проверьте автонастройку: `docker logs setup-init`
2. Если setup-init завершился с ошибкой:
   ```bash
   docker-compose restart setup-init
   ```
3. Или создайте вручную: Kibana → Data Views → Create → `banking-logs-*`

### 📈 Grafana проблемы

#### Проблема: Нет метрик в Grafana
**Решение:**
1. Проверьте Prometheus: http://localhost:9090/targets
2. Убедитесь что metrics-exporter работает: `docker logs metrics-exporter`

#### Проблема: "Login failed"
**Логин:** admin  
**Пароль:** admin

### 🔄 Общие команды

#### Полная перезагрузка
```bash
docker-compose down -v
docker-compose up -d
```

#### Просмотр логов
```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker logs -f elasticsearch
docker logs -f kibana
docker logs -f auth-service-logs
```

#### Проверка статуса
```bash
docker-compose ps
```

#### Очистка данных
```bash
# ВНИМАНИЕ: Удалит все данные!
docker-compose down -v
docker volume prune
rm -rf logs/*
```

### 🌐 Проблемы с портами

По умолчанию используются порты:
- **5601** - Kibana
- **3000** - Grafana  
- **9090** - Prometheus
- **9200** - Elasticsearch
- **8081** - Metrics Exporter

Если порты заняты, измените их в `docker-compose.yml`:
```yaml
ports:
  - "15601:5601"  # Изменено с 5601 на 15601
```

### 💡 Советы по производительности

1. **Закройте ненужные приложения** - ELK стек требует ресурсов
2. **Увеличьте память Docker** до 6-8GB
3. **Используйте SSD** для лучшей производительности Elasticsearch
4. **Отключите антивирус** для папки проекта (может замедлять I/O)

### 📞 Получение помощи

1. Проверьте логи: `docker-compose logs`
2. Убедитесь что используете последние версии Docker/Docker Compose
3. Перезапустите Docker Desktop
4. Попробуйте полную перезагрузку проекта

### 🔍 Полезные команды для диагностики

```bash
# Проверка здоровья Elasticsearch
curl http://localhost:9200/_cluster/health?pretty

# Список индексов
curl http://localhost:9200/_cat/indices?v

# Проверка Kibana
curl http://localhost:5601/api/status

# Метрики Prometheus
curl http://localhost:8081/metrics

# Статистика Docker
docker stats
``` 