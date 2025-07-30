#!/usr/bin/env python3
"""
Banking Payment Service Log Generator
Генерирует реалистичные логи платежей и переводов для банковской системы
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
json_handler = logging.FileHandler(f"{log_dir}/payment-service.json")
json_formatter = jsonlogger.JsonFormatter(
    fmt='%(asctime)s %(levelname)s %(name)s %(message)s'
)
json_handler.setFormatter(json_formatter)

# Plain text logger для обычных логов
text_handler = logging.FileHandler(f"{log_dir}/payment-service.log")
text_formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
text_handler.setFormatter(text_formatter)

# Создаём логгеры
json_logger = logging.getLogger('payment-service-json')
json_logger.addHandler(json_handler)
json_logger.setLevel(logging.INFO)

text_logger = logging.getLogger('payment-service')
text_logger.addHandler(text_handler)
text_logger.setLevel(logging.INFO)

# Банковские счета (IBAN для России)
def generate_iban():
    """Генерирует корректный российский IBAN"""
    bank_code = random.choice(['044525974', '044525225', '044525593'])  # ВТБ, Сбербанк, Альфа
    account = ''.join([str(random.randint(0, 9)) for _ in range(20)])
    return f"RU{random.randint(10, 99)}{bank_code}{account}"

BANK_ACCOUNTS = [
    {
        'account_id': f'acc_{i:06d}',
        'iban': generate_iban(),
        'balance': random.uniform(1000, 1000000),
        'owner_name': fake.name(),
        'account_type': random.choice(['current', 'savings', 'business'])
    }
    for i in range(1, 1001)  # 1000 счетов
]

# Типы платежей и их характеристики
PAYMENT_TYPES = {
    'transfer': {
        'level': 'INFO', 
        'weight': 40,
        'min_amount': 100,
        'max_amount': 100000,
        'error_rate': 0.08
    },
    'card_payment': {
        'level': 'INFO', 
        'weight': 30,
        'min_amount': 50,
        'max_amount': 50000,
        'error_rate': 0.05
    },
    'utility_payment': {
        'level': 'INFO', 
        'weight': 15,
        'min_amount': 500,
        'max_amount': 20000,
        'error_rate': 0.03
    },
    'salary_payment': {
        'level': 'INFO', 
        'weight': 10,
        'min_amount': 20000,
        'max_amount': 300000,
        'error_rate': 0.01
    },
    'large_transfer': {
        'level': 'WARN', 
        'weight': 4,
        'min_amount': 500000,
        'max_amount': 10000000,
        'error_rate': 0.15
    },
    'international_transfer': {
        'level': 'INFO', 
        'weight': 1,
        'min_amount': 1000,
        'max_amount': 500000,
        'error_rate': 0.20
    }
}

# Ошибки платежей
PAYMENT_ERRORS = [
    'insufficient_funds',
    'account_blocked', 
    'invalid_recipient',
    'limit_exceeded',
    'network_timeout',
    'fraud_detected',
    'invalid_amount',
    'service_unavailable',
    'duplicate_transaction'
]

# Получатели платежей
RECIPIENTS = [
    'ООО "Газпром энергосбыт"',
    'МосЭнергоСбыт',
    'Мегафон',
    'МТС',
    'Билайн',
    'ПАО "МТБЦ"',
    'X5 Retail Group',
    'Магнит',
    'Лента',
    'Озон',
    'Wildberries',
    'Яндекс.Такси'
]

def get_current_hour_activity_multiplier():
    """Возвращает множитель активности в зависимости от времени суток"""
    current_hour = datetime.now().hour
    
    if 9 <= current_hour <= 18:  # Рабочие часы
        return 2.5
    elif 19 <= current_hour <= 22:  # Вечерние часы
        return 1.8
    elif 23 <= current_hour <= 6:   # Ночные часы (подозрительное время)
        return 0.2
    else:  # Утренние часы
        return 1.0

def generate_payment_event():
    """Генерирует одно событие платежа"""
    
    # Выбираем тип платежа на основе весов
    payment_weights = [PAYMENT_TYPES[ptype]['weight'] for ptype in PAYMENT_TYPES]
    payment_type = random.choices(list(PAYMENT_TYPES.keys()), weights=payment_weights)[0]
    payment_info = PAYMENT_TYPES[payment_type]
    
    # Выбираем случайные счета
    sender_account = random.choice(BANK_ACCOUNTS)
    recipient_account = random.choice(BANK_ACCOUNTS)
    
    # Убеждаемся что отправитель и получатель разные
    while recipient_account['account_id'] == sender_account['account_id']:
        recipient_account = random.choice(BANK_ACCOUNTS)
    
    # Генерируем сумму платежа
    amount = round(random.uniform(payment_info['min_amount'], payment_info['max_amount']), 2)
    
    # Определяем валюту
    currency = 'RUB'
    if payment_type == 'international_transfer':
        currency = random.choice(['USD', 'EUR', 'CNY', 'KZT'])
    
    # Проверяем на ошибку
    is_error = random.random() < payment_info['error_rate']
    
    # Базовые данные события
    timestamp = datetime.now()
    transaction_id = fake.uuid4()
    
    event_data = {
        'timestamp': timestamp.isoformat(),
        'service': 'payment-service',
        'transaction_id': transaction_id,
        'payment_type': payment_type,
        'sender_account': sender_account['account_id'],
        'sender_iban': sender_account['iban'],
        'sender_name': sender_account['owner_name'],
        'recipient_account': recipient_account['account_id'],
        'recipient_iban': recipient_account['iban'],
        'recipient_name': recipient_account['owner_name'],
        'amount': amount,
        'currency': currency,
        'processing_time_ms': random.randint(50, 2000)
    }
    
    # Обработка успешного платежа
    if not is_error:
        event_data.update({
            'status': 'success',
            'level': payment_info['level'],
            'message': f"Payment processed successfully: {amount} {currency}",
            'fee': round(amount * random.uniform(0.001, 0.01), 2),
            'authorization_code': fake.bothify('AUTH-######'),
            'merchant_category': random.choice(['5411', '5812', '4900', '6011']) if payment_type == 'card_payment' else None
        })
        
        # Специальная обработка для подозрительных сумм
        if amount > 1000000:
            event_data.update({
                'level': 'WARN',
                'suspicious_amount': True,
                'compliance_check': True,
                'message': f"Large payment processed: {amount} {currency} - compliance check required"
            })
            
    # Обработка ошибки платежа
    else:
        error_code = random.choice(PAYMENT_ERRORS)
        event_data.update({
            'status': 'failed',
            'level': 'ERROR',
            'error_code': error_code,
            'message': f"Payment failed: {error_code}",
            'retry_count': random.randint(0, 3),
            'can_retry': error_code not in ['fraud_detected', 'account_blocked']
        })
    
    # Дополнительные поля для разных типов платежей
    if payment_type == 'utility_payment':
        event_data['recipient_name'] = random.choice(RECIPIENTS)
        event_data['service_type'] = random.choice(['electricity', 'gas', 'water', 'internet', 'mobile'])
        
    elif payment_type == 'international_transfer':
        event_data['swift_code'] = fake.bothify('????????###')
        event_data['correspondent_bank'] = fake.company()
        event_data['exchange_rate'] = round(random.uniform(50, 100), 4) if currency != 'RUB' else 1.0
        
    elif payment_type == 'card_payment':
        event_data['card_number'] = fake.credit_card_number()[-4:]  # Последние 4 цифры
        event_data['terminal_id'] = fake.bothify('TERM-#####')
        event_data['merchant_name'] = fake.company()
    
    # Ночные платежи отмечаем как подозрительные
    if 0 <= timestamp.hour <= 6:
        event_data['night_transaction'] = True
        if event_data['status'] == 'success':
            event_data['level'] = 'WARN'
            event_data['message'] += " [Night transaction - requires review]"
    
    return event_data

def log_event(event_data):
    """Записывает событие в логи"""
    level = event_data['level']
    message = event_data.get('message', f"Payment event: {event_data['payment_type']}")
    
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
    print("💰 Starting Banking Payment Service Log Generator...")
    print(f"📁 Logs will be written to: {log_dir}")
    
    event_count = 0
    
    try:
        while True:
            # Учитываем активность по времени суток
            activity_multiplier = get_current_hour_activity_multiplier()
            
            # Генерируем события
            events_per_cycle = max(1, int(random.randint(2, 8) * activity_multiplier))
            
            for _ in range(events_per_cycle):
                event = generate_payment_event()
                log_event(event)
                event_count += 1
                
                if event_count % 100 == 0:
                    print(f"📊 Generated {event_count} payment events")
            
            # Пауза между циклами (от 0.5 до 5 секунд)
            sleep_time = random.uniform(0.5, 5.0) / activity_multiplier
            time.sleep(sleep_time)
            
    except KeyboardInterrupt:
        print(f"\n✅ Payment service generator stopped. Total events: {event_count}")
    except Exception as e:
        print(f"❌ Error in payment service generator: {e}")

if __name__ == "__main__":
    main() 