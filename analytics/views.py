from django.shortcuts import render
import pandas as pd
import numpy as np
from django.db import connection
import json
from datetime import datetime, timedelta

def analytics_home(request):
    return render(request, 'analytics/analytics_home.html')

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
    return render(request, 'analytics/ml_demo.html', {
        'title': 'Прогнозирование рисков перерасхода ресурсов',
        'description': 'Предиктивная аналитика на базе временных рядов',
        'technologies': ['scikit-learn', 'XGBoost', 'Random Forest'],
        'demo_code': 'from sklearn.ensemble import RandomForestRegressor\nimport pandas as pd\n\n# Загрузка данных\ndf = pd.read_sql("SELECT * FROM expenses", connection)\n\n# Обучение модели\nmodel = RandomForestRegressor()\nmodel.fit(X_train, y_train)\n\n# Прогноз рисков\nrisk_score = model.predict(new_data)'
    })

def schedule_analysis(request):
    return render(request, 'analytics/ml_demo.html', {
        'title': 'Анализ соблюдения графика и объемов работ',
        'description': 'Интеллектуальный анализ выполнения проектных планов',
        'technologies': ['pandas', 'statsmodels', 'matplotlib'],
        'demo_code': 'import pandas as pd\nimport statsmodels.api as sm\n\n# Анализ временных рядов\nts_data = pd.read_sql("SELECT date, progress FROM schedule", conn)\n\n# Статистический анализ\nmodel = sm.tsa.ARIMA(ts_data, order=(1,1,1))\nresult = model.fit()\n\n# Прогноз выполнения\nforecast = result.forecast(steps=30)'
    })

def task_recommendations(request):
    return render(request, 'analytics/ml_demo.html', {
        'title': 'Рекомендации по постановке задач бригадам',
        'description': 'ИИ-система оптимизации распределения задач',
        'technologies': ['TensorFlow', 'Keras', 'Neural Networks'],
        'demo_code': 'import tensorflow as tf\nfrom tensorflow import keras\n\n# Создание нейронной сети\nmodel = keras.Sequential([\n    keras.layers.Dense(64, activation="relu"),\n    keras.layers.Dense(32, activation="relu"),\n    keras.layers.Dense(1, activation="sigmoid")\n])\n\n# Обучение модели\nmodel.compile(optimizer="adam", loss="mse")\nmodel.fit(X_train, y_train, epochs=100)'
    })

def deadline_risks(request):
    return render(request, 'analytics/ml_demo.html', {
        'title': 'Прогнозирование рисков срыва сроков',
        'description': 'Модели глубокого обучения для предсказания задержек',
        'technologies': ['PyTorch', 'LSTM', 'Time Series'],
        'demo_code': 'import torch\nimport torch.nn as nn\n\nclass LSTMModel(nn.Module):\n    def __init__(self, input_size, hidden_size):\n        super().__init__()\n        self.lstm = nn.LSTM(input_size, hidden_size)\n        self.linear = nn.Linear(hidden_size, 1)\n    \n    def forward(self, x):\n        out, _ = self.lstm(x)\n        return self.linear(out[-1])\n\nmodel = LSTMModel(10, 50)'
    })

def efficiency_analysis(request):
    return render(request, 'analytics/ml_demo.html', {
        'title': 'Анализ общей эффективности по окончанию объекта',
        'description': 'Комплексная оценка KPI проекта с многофакторным анализом',
        'technologies': ['pandas', 'numpy', 'seaborn'],
        'demo_code': 'import pandas as pd\nimport numpy as np\nimport seaborn as sns\n\n# Загрузка данных эффективности\ndf = pd.read_sql("SELECT * FROM project_kpi", conn)\n\n# Корреляционный анализ\ncorr_matrix = df.corr()\n\n# Расчет индекса эффективности\nefficiency_score = np.mean([\n    df["cost_efficiency"],\n    df["time_efficiency"],\n    df["quality_score"]\n])'
    })

def legal_risks(request):
    return render(request, 'analytics/ml_demo.html', {
        'title': 'Анализ юридических рисков в Договорах',
        'description': 'NLP-анализ договорной документации',
        'technologies': ['NLTK', 'spaCy', 'Transformers'],
        'demo_code': 'import nltk\nimport spacy\nfrom transformers import pipeline\n\n# Загрузка модели NLP\nnlp = spacy.load("ru_core_news_sm")\nclassifier = pipeline("text-classification")\n\n# Анализ договора\ndoc = nlp(contract_text)\nrisks = []\n\nfor sent in doc.sents:\n    risk_score = classifier(sent.text)\n    if risk_score[0]["label"] == "HIGH_RISK":\n        risks.append(sent.text)'
    })