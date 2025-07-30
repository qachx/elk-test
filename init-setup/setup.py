#!/usr/bin/env python3
"""
Автоматическая настройка Kibana и дашбордов
Создает Data Views, дашборды и визуализации
"""

import requests
import json
import time
import sys

KIBANA_URL = "http://kibana:5601"
ELASTICSEARCH_URL = "http://elasticsearch:9200"

def wait_for_services():
    """Ждет запуска Elasticsearch и Kibana"""
    print("🔄 Waiting for Elasticsearch...")
    while True:
        try:
            response = requests.get(f"{ELASTICSEARCH_URL}/_cluster/health", timeout=5)
            if response.status_code == 200:
                print("✅ Elasticsearch ready")
                break
        except:
            pass
        time.sleep(5)
    
    print("🔄 Waiting for Kibana...")
    while True:
        try:
            response = requests.get(f"{KIBANA_URL}/api/status", timeout=5)
            if response.status_code == 200:
                print("✅ Kibana ready")
                break
        except:
            pass
        time.sleep(5)

def create_data_view():
    """Создает Data View для банковских логов"""
    print("📊 Creating Kibana Data View...")
    
    headers = {
        'Content-Type': 'application/json',
        'kbn-xsrf': 'true'
    }
    
    data_view = {
        "data_view": {
            "title": "banking-logs-*",
            "name": "Banking Logs",
            "timeFieldName": "@timestamp"
        }
    }
    
    try:
        response = requests.post(
            f"{KIBANA_URL}/api/data_views/data_view",
            headers=headers,
            json=data_view,
            timeout=30
        )
        
        if response.status_code in [200, 409]:  # 409 = уже существует
            print("✅ Data View created successfully")
            return True
        else:
            print(f"❌ Failed to create Data View: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Error creating Data View: {e}")
        return False

def create_index_template():
    """Создает index template для правильного маппинга"""
    print("🔧 Creating Elasticsearch index template...")
    
    template = {
        "index_patterns": ["banking-logs-*"],
        "template": {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            },
            "mappings": {
                "properties": {
                    "@timestamp": {"type": "date"},
                    "timestamp": {"type": "date"},
                    "service": {"type": "keyword"},
                    "level": {"type": "keyword"},
                    "message": {"type": "text"},
                    "user_id": {"type": "keyword"},
                    "amount": {"type": "double"},
                    "currency": {"type": "keyword"},
                    "client_ip": {"type": "ip"},
                    "risk_score": {"type": "integer"},
                    "event_type": {"type": "keyword"},
                    "status": {"type": "keyword"},
                    "error_code": {"type": "keyword"}
                }
            }
        }
    }
    
    try:
        response = requests.put(
            f"{ELASTICSEARCH_URL}/_index_template/banking-logs",
            json=template,
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            print("✅ Index template created")
            return True
        else:
            print(f"❌ Failed to create template: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error creating template: {e}")
        return False

def create_sample_dashboard():
    """Создает образец дашборда в Kibana"""
    print("📈 Creating sample dashboard...")
    
    headers = {
        'Content-Type': 'application/json',
        'kbn-xsrf': 'true'
    }
    
    # Создаем дашборд через простой API
    dashboard = {
        "attributes": {
            "title": "Banking Security Overview",
            "description": "Overview of banking system logs and security events",
            "panelsJSON": "[]",
            "optionsJSON": "{\"useMargins\":true,\"syncColors\":false,\"hidePanelTitles\":false}",
            "version": 1,
            "timeRestore": False,
            "kibanaSavedObjectMeta": {
                "searchSourceJSON": "{\"query\":{\"query\":\"\",\"language\":\"kuery\"},\"filter\":[]}"
            }
        }
    }
    
    try:
        response = requests.post(
            f"{KIBANA_URL}/api/saved_objects/dashboard",
            headers=headers,
            json=dashboard,
            timeout=30
        )
        
        if response.status_code in [200, 409]:
            print("✅ Sample dashboard created")
            return True
        else:
            print(f"❌ Failed to create dashboard: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error creating dashboard: {e}")
        return False

def main():
    """Основная функция настройки"""
    print("🏦 Banking ELK Auto-Setup Starting...")
    print("=" * 50)
    
    # Ждем запуска сервисов
    wait_for_services()
    
    # Даем время на полную инициализацию
    print("⏳ Waiting for full initialization...")
    time.sleep(30)
    
    # Создаем index template
    if not create_index_template():
        print("⚠️ Template creation failed, continuing...")
    
    # Создаем Data View
    if not create_data_view():
        print("⚠️ Data View creation failed, continuing...")
    
    # Создаем образец дашборда  
    if not create_sample_dashboard():
        print("⚠️ Dashboard creation failed, continuing...")
    
    print("=" * 50)
    print("🎉 Setup completed!")
    print("")
    print("📊 Access your services:")
    print("   Kibana:     http://localhost:5601")
    print("   Grafana:    http://localhost:3000 (admin/admin)")
    print("   Prometheus: http://localhost:9090")
    print("")
    print("💡 Data should appear in Kibana within 2-3 minutes")
    print("💡 Check Discover section for banking-logs-* data view")

if __name__ == "__main__":
    main() 