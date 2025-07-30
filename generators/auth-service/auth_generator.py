#!/usr/bin/env python3
"""
Banking Auth Service Log Generator
Генерирует реалистичные логи аутентификации для банковской системы
"""

import json
import random
import time
import logging
import os
from datetime import datetime, timedelta
from faker import Faker
from pythonjsonlogger import jsonlogger

# Настройка Faker для русских данных
fake = Faker('ru_RU')

# Конфигурация логирования
log_dir = "/app/logs"
os.makedirs(log_dir, exist_ok=True)

# JSON logger для структурированных логов
json_handler = logging.FileHandler(f"{log_dir}/auth-service.json")
json_formatter = jsonlogger.JsonFormatter(
    fmt='%(asctime)s %(levelname)s %(name)s %(message)s'
)
json_handler.setFormatter(json_formatter)

# Plain text logger для обычных логов
text_handler = logging.FileHandler(f"{log_dir}/auth-service.log")
text_formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
text_handler.setFormatter(text_formatter)

# Создаём логгеры
json_logger = logging.getLogger('auth-service-json')
json_logger.addHandler(json_handler)
json_logger.setLevel(logging.INFO)

text_logger = logging.getLogger('auth-service')
text_logger.addHandler(text_handler)
text_logger.setLevel(logging.INFO)

# Пользователи банка (симуляция)
BANK_USERS = [
    {'user_id': f'user_{i:04d}', 'username': fake.user_name(), 'email': fake.email(), 
     'phone': fake.phone_number(), 'full_name': fake.name()}
    for i in range(1, 501)  # 500 пользователей
]

# IP адреса (симуляция разных регионов)
IP_POOLS = {
    'moscow': ['77.88.55.', '95.108.213.', '178.154.131.'],
    'spb': ['81.177.6.', '188.120.245.', '176.59.108.'],
    'regions': ['89.108.65.', '188.113.194.', '94.25.173.'],
    'suspicious': ['185.220.101.', '198.98.51.', '77.247.181.']
}

# События аутентификации
AUTH_EVENTS = {
    'login_success': {'level': 'INFO', 'weight': 70},
    'login_failed': {'level': 'WARN', 'weight': 15},
    'account_locked': {'level': 'ERROR', 'weight': 3},
    'password_reset': {'level': 'INFO', 'weight': 5},
    'two_factor_required': {'level': 'INFO', 'weight': 4},
    'suspicious_login': {'level': 'WARN', 'weight': 2},
    'logout': {'level': 'INFO', 'weight': 1}
}

def get_random_ip(region='random'):
    """Генерирует случайный IP адрес"""
    if region == 'random':
        region = random.choice(list(IP_POOLS.keys()))
    
    prefix = random.choice(IP_POOLS[region])
    return f"{prefix}{random.randint(1, 254)}"

def get_current_hour_activity_multiplier():
    """Возвращает множитель активности в зависимости от времени суток"""
    current_hour = datetime.now().hour
    
    if 9 <= current_hour <= 18:  # Рабочие часы
        return 3.0
    elif 19 <= current_hour <= 22:  # Вечерние часы
        return 1.5
    elif 23 <= current_hour <= 6:   # Ночные часы
        return 0.3
    else:  # Утренние часы
        return 1.0

def generate_auth_event():
    """Генерирует одно событие аутентификации"""
    user = random.choice(BANK_USERS)
    
    # Выбираем тип события на основе весов
    event_weights = [AUTH_EVENTS[event]['weight'] for event in AUTH_EVENTS]
    event_type = random.choices(list(AUTH_EVENTS.keys()), weights=event_weights)[0]
    event_info = AUTH_EVENTS[event_type]
    
    # Базовые данные события
    timestamp = datetime.now()
    session_id = fake.uuid4()
    
    # IP адрес (подозрительные логины чаще с подозрительных IP)
    if event_type == 'suspicious_login':
        client_ip = get_random_ip('suspicious')
    else:
        client_ip = get_random_ip()
    
    # Устройство и браузер
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)',
        'BankingApp/1.2.3 (iOS)',
        'BankingApp/2.1.0 (Android)'
    ]
    user_agent = random.choice(user_agents)
    
    # Специфичные данные для разных типов событий
    event_data = {
        'timestamp': timestamp.isoformat(),
        'service': 'auth-service',
        'event_type': event_type,
        'user_id': user['user_id'],
        'username': user['username'],
        'session_id': session_id,
        'client_ip': client_ip,
        'user_agent': user_agent,
        'level': event_info['level']
    }
    
    # Дополнительные поля в зависимости от типа события
    if event_type == 'login_success':
        event_data.update({
            'message': f"User {user['username']} successfully logged in",
            'location': fake.city(),
            'device_fingerprint': fake.sha256()[:16],
            'two_factor_used': random.choice([True, False])
        })
        
    elif event_type == 'login_failed':
        failure_reasons = ['invalid_password', 'user_not_found', 'account_disabled']
        reason = random.choice(failure_reasons)
        event_data.update({
            'message': f"Login failed for user {user['username']}: {reason}",
            'failure_reason': reason,
            'attempt_count': random.randint(1, 5)
        })
        
    elif event_type == 'account_locked':
        event_data.update({
            'message': f"Account {user['username']} locked due to multiple failed attempts",
            'failed_attempts': random.randint(5, 10),
            'lock_duration': '30m',
            'auto_unlock': True
        })
        
    elif event_type == 'suspicious_login':
        event_data.update({
            'message': f"Suspicious login attempt for user {user['username']}",
            'risk_score': random.randint(70, 95),
            'suspicious_factors': random.sample([
                'unusual_location', 'unusual_time', 'new_device', 
                'multiple_failed_attempts', 'tor_usage'
            ], k=random.randint(1, 3))
        })
        
    elif event_type == 'two_factor_required':
        event_data.update({
            'message': f"Two-factor authentication required for user {user['username']}",
            'sms_sent': random.choice([True, False]),
            'app_notification': True
        })
    
    return event_data

def log_event(event_data):
    """Записывает событие в логи"""
    level = event_data['level']
    message = event_data.get('message', f"Auth event: {event_data['event_type']}")
    
    # Убираем message из extra чтобы избежать конфликта
    log_data = event_data.copy()
    log_data.pop('message', None)
    
    # JSON лог
    if level == 'INFO':
        json_logger.info(message, extra=log_data)
        text_logger.info(message)
    elif level == 'WARN':
        json_logger.warning(message, extra=log_data)
        text_logger.warning(message)
    elif level == 'ERROR':
        json_logger.error(message, extra=log_data)
        text_logger.error(message)

def main():
    """Основной цикл генерации логов"""
    print("🔐 Starting Banking Auth Service Log Generator...")
    print(f"📁 Logs will be written to: {log_dir}")
    
    event_count = 0
    
    try:
        while True:
            # Учитываем активность по времени суток
            activity_multiplier = get_current_hour_activity_multiplier()
            
            # Генерируем события
            events_per_cycle = max(1, int(random.randint(1, 5) * activity_multiplier))
            
            for _ in range(events_per_cycle):
                event = generate_auth_event()
                log_event(event)
                event_count += 1
                
                if event_count % 100 == 0:
                    print(f"📊 Generated {event_count} auth events")
            
            # Пауза между циклами (от 1 до 10 секунд)
            sleep_time = random.uniform(1.0, 10.0) / activity_multiplier
            time.sleep(sleep_time)
            
    except KeyboardInterrupt:
        print(f"\n✅ Auth service generator stopped. Total events: {event_count}")
    except Exception as e:
        print(f"❌ Error in auth service generator: {e}")

if __name__ == "__main__":
    main() 