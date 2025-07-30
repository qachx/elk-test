#!/usr/bin/env python3
"""
Banking Notification Service Log Generator
Генерирует логи системы уведомлений
"""

import random
import time
import logging
import os
from datetime import datetime
from faker import Faker
from pythonjsonlogger import jsonlogger

fake = Faker('ru_RU')

log_dir = "/app/logs"
os.makedirs(log_dir, exist_ok=True)

json_handler = logging.FileHandler(f"{log_dir}/notification-service.json")
json_formatter = jsonlogger.JsonFormatter(fmt='%(asctime)s %(levelname)s %(name)s %(message)s')
json_handler.setFormatter(json_formatter)

text_handler = logging.FileHandler(f"{log_dir}/notification-service.log")
text_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
text_handler.setFormatter(text_formatter)

json_logger = logging.getLogger('notification-service-json')
json_logger.addHandler(json_handler)
json_logger.setLevel(logging.INFO)

text_logger = logging.getLogger('notification-service')
text_logger.addHandler(text_handler)
text_logger.setLevel(logging.INFO)

NOTIFICATION_TYPES = {
    'sms_sent': {'level': 'INFO', 'weight': 50},
    'email_sent': {'level': 'INFO', 'weight': 30},
    'push_sent': {'level': 'INFO', 'weight': 15},
    'sms_failed': {'level': 'ERROR', 'weight': 3},
    'email_failed': {'level': 'ERROR', 'weight': 2}
}

def generate_notification_event():
    event_weights = [NOTIFICATION_TYPES[event]['weight'] for event in NOTIFICATION_TYPES]
    event_type = random.choices(list(NOTIFICATION_TYPES.keys()), weights=event_weights)[0]
    
    event_data = {
        'timestamp': datetime.now().isoformat(),
        'service': 'notification-service',
        'event_type': event_type,
        'notification_id': fake.uuid4(),
        'user_id': f'user_{random.randint(1, 500):04d}',
        'level': NOTIFICATION_TYPES[event_type]['level']
    }
    
    if 'sms' in event_type:
        event_data['phone'] = fake.phone_number()
        event_data['message'] = "Код подтверждения: " + str(random.randint(100000, 999999))
    elif 'email' in event_type:
        event_data['email'] = fake.email()
        event_data['subject'] = random.choice(['Операция по карте', 'Пополнение счета', 'Изменение тарифа'])
    
    if 'failed' in event_type:
        event_data['error_code'] = random.choice(['NETWORK_ERROR', 'INVALID_RECIPIENT', 'QUOTA_EXCEEDED'])
        event_data['message'] = f"Notification failed: {event_data['error_code']}"
    else:
        event_data['message'] = f"Notification sent successfully via {event_type.split('_')[0]}"
    
    return event_data

def log_event(event_data):
    level = event_data['level']
    message = event_data.get('message', f"Notification event: {event_data['event_type']}")
    
    # Убираем message из extra чтобы избежать конфликта
    log_data = event_data.copy()
    log_data.pop('message', None)
    
    if level == 'INFO':
        json_logger.info(message, extra=log_data)
        text_logger.info(message)
    elif level == 'ERROR':
        json_logger.error(message, extra=log_data)
        text_logger.error(message)

def main():
    print("📱 Starting Banking Notification Service Log Generator...")
    print(f"📁 Logs will be written to: {log_dir}")
    
    event_count = 0
    
    try:
        while True:
            events_per_cycle = random.randint(1, 4)
            
            for _ in range(events_per_cycle):
                event = generate_notification_event()
                log_event(event)
                event_count += 1
                
                if event_count % 100 == 0:
                    print(f"📱 Generated {event_count} notification events")
            
            time.sleep(random.uniform(2.0, 15.0))
            
    except KeyboardInterrupt:
        print(f"\n✅ Notification service generator stopped. Total events: {event_count}")
    except Exception as e:
        print(f"❌ Error in notification service generator: {e}")

if __name__ == "__main__":
    main() 