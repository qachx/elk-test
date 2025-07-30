#!/usr/bin/env python3
"""
Banking Metrics Exporter for Prometheus
Экспортирует метрики банковских сервисов для Prometheus
"""

import time
import random
from prometheus_client import start_http_server, Gauge, Counter, Histogram
from faker import Faker

fake = Faker()

# Определяем метрики
REQUEST_COUNT = Counter('banking_requests_total', 'Total requests', ['service', 'method', 'status'])
REQUEST_DURATION = Histogram('banking_request_duration_seconds', 'Request duration', ['service'])
ACTIVE_USERS = Gauge('banking_active_users', 'Currently active users')
TRANSACTION_AMOUNT = Gauge('banking_transaction_amount_total', 'Total transaction amount')
ERROR_RATE = Gauge('banking_error_rate', 'Error rate percentage', ['service'])
QUEUE_SIZE = Gauge('banking_queue_size', 'Queue size', ['queue_name'])

# Банковские сервисы
SERVICES = ['auth-service', 'payment-service', 'fraud-service', 'notification-service']

def update_metrics():
    """Обновляет метрики случайными реалистичными значениями"""
    
    # Активные пользователи (меняется в течение дня)
    current_hour = time.localtime().tm_hour
    if 9 <= current_hour <= 18:  # Рабочие часы
        base_users = random.randint(800, 1200)
    elif 19 <= current_hour <= 22:  # Вечерние часы
        base_users = random.randint(400, 700)
    else:  # Ночные часы
        base_users = random.randint(50, 200)
    
    ACTIVE_USERS.set(base_users + random.randint(-50, 50))
    
    # Обновляем метрики для каждого сервиса
    for service in SERVICES:
        # HTTP запросы
        for method in ['GET', 'POST', 'PUT', 'DELETE']:
            for status in ['200', '400', '401', '500']:
                # Больше успешных запросов
                weight = 0.8 if status == '200' else 0.05
                if random.random() < weight:
                    REQUEST_COUNT.labels(service=service, method=method, status=status).inc(
                        random.randint(1, 10)
                    )
        
        # Время ответа
        REQUEST_DURATION.labels(service=service).observe(random.uniform(0.01, 2.0))
        
        # Процент ошибок
        if service == 'fraud-service':
            error_rate = random.uniform(1, 8)  # Fraud сервис может иметь больше ошибок
        elif service == 'payment-service':
            error_rate = random.uniform(0.5, 5)  # Платежи критичны
        else:
            error_rate = random.uniform(0.1, 3)
        
        ERROR_RATE.labels(service=service).set(error_rate)
    
    # Размеры очередей
    queues = ['payment_queue', 'notification_queue', 'fraud_analysis_queue']
    for queue in queues:
        if queue == 'payment_queue':
            size = random.randint(10, 500)  # Платежная очередь может быть большой
        else:
            size = random.randint(0, 100)
        
        QUEUE_SIZE.labels(queue_name=queue).set(size)
    
    # Общий объем транзакций (в рублях)
    current_total = TRANSACTION_AMOUNT._value._value if hasattr(TRANSACTION_AMOUNT, '_value') else 0
    new_transaction = random.uniform(1000, 500000)  # Новая транзакция
    TRANSACTION_AMOUNT.set(current_total + new_transaction)

def main():
    """Основной цикл экспорта метрик"""
    port = 8080
    print(f"📊 Starting Banking Metrics Exporter on port {port}")
    print(f"🔗 Metrics available at: http://localhost:{port}/metrics")
    
    # Запускаем HTTP сервер для Prometheus
    start_http_server(port)
    
    metrics_count = 0
    
    try:
        while True:
            update_metrics()
            metrics_count += 1
            
            if metrics_count % 60 == 0:  # Каждую минуту
                print(f"📈 Updated metrics {metrics_count} times")
            
            # Обновляем метрики каждые 5 секунд
            time.sleep(5)
            
    except KeyboardInterrupt:
        print(f"\n✅ Metrics exporter stopped. Total updates: {metrics_count}")
    except Exception as e:
        print(f"❌ Error in metrics exporter: {e}")

if __name__ == "__main__":
    main() 