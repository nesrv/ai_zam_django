from django.shortcuts import render
import pandas as pd
import numpy as np
from django.db import connection
import json
from datetime import datetime, timedelta
import random

def analytics_home(request):
    return render(request, 'analytics/analytics_home.html')

def financial_monitoring(request):
    # Создаем фейковые данные для визуализации
    projects = [
        {"id": 1, "name": "Реконструкция дома", "budget": 5000000, "status": "В процессе"},
        {"id": 2, "name": "Снос спортивного комплекса", "budget": 3500000, "status": "В процессе"},
        {"id": 3, "name": "Строительство офисного центра", "budget": 12000000, "status": "Планирование"},
        {"id": 4, "name": "Реновация парковой зоны", "budget": 8000000, "status": "Завершен"},
    ]
    
    # Генерируем данные о финансовых потоках
    months = ['Янв', 'Фев', 'Март', 'Апр', 'Май', 'Июнь', 'Июль', 'Авг', 'Сент', 'Окт', 'Нояб', 'Дек']
    financial_data = {}
    
    for project in projects:
        financial_data[project["id"]] = {
            "expenses": [random.randint(100000, 500000) for _ in range(12)],
            "income": [random.randint(150000, 600000) for _ in range(12)],
            "predictions": [random.randint(100000, 600000) for _ in range(6)],
            "risk_factors": {
                "budget_overrun": random.randint(10, 90),
                "schedule_delay": random.randint(10, 90),
                "quality_issues": random.randint(10, 90),
                "resource_shortage": random.randint(10, 90),
            },
            "resource_allocation": {
                "materials": random.randint(30, 50),
                "labor": random.randint(20, 40),
                "equipment": random.randint(10, 30),
                "management": random.randint(5, 15),
                "other": random.randint(5, 15)
            },
            "efficiency_metrics": {
                "roi": round(random.uniform(0.8, 1.5), 2),
                "cost_variance": round(random.uniform(-0.2, 0.3), 2),
                "schedule_variance": round(random.uniform(-0.15, 0.25), 2),
                "resource_utilization": round(random.uniform(0.6, 0.95), 2),
            },
            "anomalies": [
                {"date": "2025-03-15", "type": "Перерасход", "amount": random.randint(50000, 200000), "category": "Материалы"} if random.random() > 0.5 else None,
                {"date": "2025-05-22", "type": "Задержка платежа", "amount": random.randint(100000, 300000), "category": "Оплата"} if random.random() > 0.5 else None,
                {"date": "2025-07-10", "type": "Непредвиденные расходы", "amount": random.randint(30000, 150000), "category": "Оборудование"} if random.random() > 0.5 else None,
            ],
            "ml_insights": [
                "Высокая вероятность перерасхода бюджета в следующем квартале" if random.random() > 0.7 else None,
                "Рекомендуется оптимизировать закупку материалов" if random.random() > 0.7 else None,
                "Прогнозируется задержка в графике на 2 недели" if random.random() > 0.7 else None,
                "Обнаружены аномалии в расходовании средств на оборудование" if random.random() > 0.7 else None,
            ]
        }
    
    # Удаляем None из списков
    for project_id in financial_data:
        financial_data[project_id]["anomalies"] = [a for a in financial_data[project_id]["anomalies"] if a is not None]
        financial_data[project_id]["ml_insights"] = [i for i in financial_data[project_id]["ml_insights"] if i is not None]
    
    context = {
        "projects": projects,
        "months": months,
        "financial_data": financial_data,
        "page_title": "Автоматизированная система мониторинга финансовых потоков"
    }
    
    return render(request, 'analytics/financial_monitoring.html', context)

def daily_expenses_analytics(request):
    # Получаем данные из таблицы svodnaya_raskhod_dokhod_po_dnyam
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT data, raskhod, dokhod, objekt_id 
            FROM svodnaya_raskhod_dokhod_po_dnyam 
            ORDER BY data DESC LIMIT 100
        """)
        data = cursor.fetchall()
    
    # Создаем DataFrame
    df = pd.DataFrame(data, columns=['date', 'expense', 'income', 'object_id'])
    
    # Базовая аналитика
    analytics = {
        'total_expenses': float(df['expense'].sum()) if not df.empty else 0,
        'total_income': float(df['income'].sum()) if not df.empty else 0,
        'avg_daily_expense': float(df['expense'].mean()) if not df.empty else 0,
        'avg_daily_income': float(df['income'].mean()) if not df.empty else 0,
        'records_count': len(df),
        'date_range': {
            'start': df['date'].min().strftime('%Y-%m-%d') if not df.empty else None,
            'end': df['date'].max().strftime('%Y-%m-%d') if not df.empty else None
        }
    }
    
    # Данные для графиков
    chart_data = []
    if not df.empty:
        df_grouped = df.groupby('date').agg({
            'expense': 'sum',
            'income': 'sum'
        }).reset_index()
        
        for _, row in df_grouped.iterrows():
            chart_data.append({
                'date': row['date'].strftime('%Y-%m-%d'),
                'expense': float(row['expense']),
                'income': float(row['income'])
            })
    
    context = {
        'analytics': analytics,
        'chart_data': json.dumps(chart_data),
    }
    
    return render(request, 'analytics/daily_expenses.html', context)

def risk_prediction(request):
    # Создаем фейковые данные для визуализации
    projects = [
        {"id": "project1", "name": "Реконструкция объекта", "budget": 5000000, "status": "В процессе"},
        {"id": "project2", "name": "Снос спортивного комплекса", "budget": 8000000, "status": "В процессе"},
    ]
    
    # Генерируем данные о финансовых потоках и рисках
    months = ['Янв', 'Фев', 'Март', 'Апр', 'Май', 'Июнь', 'Июль', 'Авг', 'Сент']
    
    context = {
        "projects": projects,
        "months": months
    }
    
    return render(request, 'analytics/risk_prediction_new.html', context)

def schedule_analysis(request):
    return render(request, 'analytics/schedule_analysis.html')

def task_recommendations(request):
    return render(request, 'analytics/task_recommendations.html')

def deadline_risks(request):
    return render(request, 'analytics/deadline_risks.html')

def efficiency_analysis(request):
    return render(request, 'analytics/efficiency_analysis.html')

def legal_risks(request):
    # Создаем простой контекст для шаблона
    context = {
        "contract": {
            "id": "contract1",
            "name": "Договор подряда №2025-07-001",
            "risk_index": 68
        },
        "metrics": {
            "risk_index": 68,
            "risks_count": 9,
            "high_risks": 2,
            "accuracy": 94
        }
    }
    
    return render(request, 'analytics/legal_risks.html', context)