#!/usr/bin/env python3
"""
Banking Fraud Detection Service Log Generator
Генерирует логи системы обнаружения мошенничества
"""

import json
import random
import time
import logging
import os
from datetime import datetime
from faker import Faker
from pythonjsonlogger import jsonlogger

fake = Faker('ru_RU')

# Конфигурация логирования
log_dir = "/app/logs"
os.makedirs(log_dir, exist_ok=True)

json_handler = logging.FileHandler(f"{log_dir}/fraud-service.json")
json_formatter = jsonlogger.JsonFormatter(fmt='%(asctime)s %(levelname)s %(name)s %(message)s')
json_handler.setFormatter(json_formatter)

text_handler = logging.FileHandler(f"{log_dir}/fraud-service.log")
text_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
text_handler.setFormatter(text_formatter)

json_logger = logging.getLogger('fraud-service-json')
json_logger.addHandler(json_handler)
json_logger.setLevel(logging.INFO)

text_logger = logging.getLogger('fraud-service')
text_logger.addHandler(text_handler)
text_logger.setLevel(logging.INFO)

# Типы мошеннических активностей
FRAUD_EVENTS = {
    'suspicious_transaction': {'level': 'WARN', 'weight': 40},
    'card_fraud_detected': {'level': 'ERROR', 'weight': 20},
    'account_takeover': {'level': 'CRITICAL', 'weight': 10},
    'money_laundering': {'level': 'CRITICAL', 'weight': 5},
    'identity_theft': {'level': 'ERROR', 'weight': 15},
    'false_positive': {'level': 'INFO', 'weight': 10}
}

def generate_fraud_event():
    """Генерирует событие fraud detection"""
    event_weights = [FRAUD_EVENTS[event]['weight'] for event in FRAUD_EVENTS]
    event_type = random.choices(list(FRAUD_EVENTS.keys()), weights=event_weights)[0]
    
    timestamp = datetime.now()
    
    event_data = {
        'timestamp': timestamp.isoformat(),
        'service': 'fraud-service',
        'event_type': event_type,
        'alert_id': fake.uuid4(),
        'risk_score': random.randint(1, 100),
        'user_id': f'user_{random.randint(1, 500):04d}',
        'transaction_id': fake.uuid4(),
        'level': FRAUD_EVENTS[event_type]['level']
    }
    
    if event_type == 'suspicious_transaction':
        event_data.update({
            'message': 'Suspicious transaction pattern detected',
            'amount': random.uniform(50000, 1000000),
            'factors': random.sample(['unusual_amount', 'unusual_time', 'multiple_transactions', 'new_recipient'], k=random.randint(1, 3))
        })
    elif event_type == 'card_fraud_detected':
        event_data.update({
            'message': 'Card fraud detected',
            'card_number': fake.credit_card_number()[-4:],
            'merchant': fake.company(),
            'location': fake.city()
        })
    
    return event_data

def log_event(event_data):
    level = event_data['level']
    message = event_data.get('message', f"Fraud event: {event_data['event_type']}")
    
    # Убираем message из extra чтобы избежать конфликта
    log_data = event_data.copy()
    log_data.pop('message', None)
    
    if level == 'INFO':
        json_logger.info(message, extra=log_data)
        text_logger.info(message)
    elif level == 'WARN':
        json_logger.warning(message, extra=log_data)
        text_logger.warning(message)
    elif level == 'ERROR':
        json_logger.error(message, extra=log_data)
        text_logger.error(message)
    elif level == 'CRITICAL':
        json_logger.critical(message, extra=log_data)
        text_logger.critical(message)

def main():
    print("🚨 Starting Banking Fraud Detection Service Log Generator...")
    print(f"📁 Logs will be written to: {log_dir}")
    
    event_count = 0
    
    try:
        while True:
            # Fraud события происходят реже
            events_per_cycle = random.randint(0, 2)
            
            for _ in range(events_per_cycle):
                event = generate_fraud_event()
                log_event(event)
                event_count += 1
                
                if event_count % 50 == 0:
                    print(f"🚨 Generated {event_count} fraud events")
            
            time.sleep(random.uniform(10.0, 60.0))  # 10-60 секунд между событиями
            
    except KeyboardInterrupt:
        print(f"\n✅ Fraud service generator stopped. Total events: {event_count}")
    except Exception as e:
        print(f"❌ Error in fraud service generator: {e}")

if __name__ == "__main__":
    main() 