import os
import logging
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Получаем API ключ
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

logger = logging.getLogger(__name__)

def format_menu_text(text):
    """Заменяем символы на эмодзи"""
    # Заменяем различные символы на эмодзи
    text = text.replace('# ', '🍽️ ')
    text = text.replace('## ', '📅 ')
    text = text.replace('### ', '🍴 ')
    text = text.replace('- ', '• ')
    text = text.replace('* ', '• ')
    text = text.replace('МЕНЮ НА НЕДЕЛЮ', '🍽️ МЕНЮ НА НЕДЕЛЮ')
    text = text.replace('СПИСОК ПОКУПОК', '🛍️ СПИСОК ПОКУПОК')

    # Добавляем эмодзи к дням недели
    days = {
        'Понедельник': '📅 Понедельник',
        'Вторник': '📅 Вторник',
        'Среда': '📅 Среда',
        'Четверг': '📅 Четверг',
        'Пятница': '📅 Пятница',
        'Суббота': '📅 Суббота',
        'Воскресенье': '📅 Воскресенье'
    }

    for day, emoji_day in days.items():
        text = text.replace(f'{day}:', f'{emoji_day}:')

    # Добавляем эмодзи к приёмам пищи
    text = text.replace('Завтрак:', '🍳 Завтрак:')
    text = text.replace('Обед:', '🍲 Обед:')
    text = text.replace('Ужин:', '🍽️ Ужин:')

    return text

def generate_weekly_menu(preferences):
    """Генерация меню на неделю"""
    try:
        logger.info("Подключаюсь к DeepSeek...")
        client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

        prompt = f"""Ты опытный повар с 20-летним стажем. Составь меню на неделю (7 дней) для семьи из 4 человек, учитывая следующие предпочтения: {preferences}.

Меню должно быть разнообразным, полезным и вкусным и легко готовиться. Для каждого дня укажи:
1. Завтрак
2. Обед  
3. Ужин

После меню составь полный список покупок на всю неделю с указанием количества продуктов.

ВАЖНО: НЕ ИСПОЛЬЗУЙ символы # и * в ответе. Используй только тире (-) для списков.

Формат ответа:
МЕНЮ НА НЕДЕЛЮ:
Понедельник:
- Завтрак: [блюдо]
- Обед: [блюдо]
- Ужин: [блюдо]

[и так далее для всех дней]

СПИСОК ПОКУПОК:
- [продукт] - [количество]
- [продукт] - [количество]
[и так далее]"""

        return _generate_menu(client, prompt)

    except Exception as e:
        error_msg = f"Ошибка при работе с DeepSeek: {str(e)}"
        logger.error(error_msg)
        return error_msg

def generate_daily_menu(preferences):
    """Генерация меню на один день"""
    try:
        logger.info("Подключаюсь к DeepSeek...")
        client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

        prompt = f"""Ты опытный повар с 20-летним стажем. Составь меню на один день для семьи из 4 человек, учитывая следующие предпочтения: {preferences}.

Меню должно быть полезным, вкусным и легко готовиться. Укажи:
1. Завтрак
2. Обед  
3. Ужин

После меню составь список покупок на этот день с указанием количества продуктов.

ВАЖНО: НЕ ИСПОЛЬЗУЙ символы # и * в ответе. Используй только тире (-) для списков.

Формат ответа:
МЕНЮ НА ДЕНЬ:
- Завтрак: [блюдо]
- Обед: [блюдо]
- Ужин: [блюдо]

СПИСОК ПОКУПОК:
- [продукт] - [количество]
- [продукт] - [количество]
[и так далее]"""

        return _generate_menu(client, prompt)

    except Exception as e:
        error_msg = f"Ошибка при работе с DeepSeek: {str(e)}"
        logger.error(error_msg)
        return error_msg

def _generate_menu(client, prompt):
    """Общая функция генерации меню"""
    logger.info("Отправляю запрос к DeepSeek...")

    # Пробуем разные модели
    models_to_try = ["deepseek-chat", "deepseek-coder"]

    for model in models_to_try:
        try:
            logger.info(f"Пробую модель: {model}")
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Ты опытный повар с 20-летним стажем."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            break
        except Exception as model_error:
            logger.warning(f"Модель {model} недоступна: {model_error}")
            if model == models_to_try[-1]:  # Последняя модель
                raise model_error
            continue

    menu_content = response.choices[0].message.content
    logger.info(f"Меню сгенерировано, длина: {len(menu_content)} символов")
    return menu_content

def get_ai_response(message, session_messages=None):
    """Получение ответа от AI для общего чата"""
    try:
        if not DEEPSEEK_API_KEY:
            return "❌ Ошибка: API ключ DeepSeek не настроен. Обратитесь к администратору."
        
        logger.info("Подключаюсь к DeepSeek для общего чата...")
        client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

        # Формируем контекст из истории сообщений
        messages = [
            {"role": "system", "content": "Ты полезный AI ассистент. Отвечай кратко и по делу."}
        ]
        
        if session_messages:
            last_msgs = list(session_messages)[-5:]
            for msg in last_msgs:
                messages.append({
                    "role": msg.message_type,
                    "content": msg.content
                })
        
        messages.append({"role": "user", "content": message})

        # Пробуем разные модели
        models_to_try = ["deepseek-chat", "deepseek-coder"]

        for model in models_to_try:
            try:
                logger.info(f"Пробую модель: {model}")
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1000
                )
                break
            except Exception as model_error:
                logger.warning(f"Модель {model} недоступна: {model_error}")
                if model == models_to_try[-1]:  # Последняя модель
                    raise model_error
                continue

        ai_response = response.choices[0].message.content
        logger.info(f"AI ответ сгенерирован, длина: {len(ai_response)} символов")
        return ai_response

    except Exception as e:
        error_msg = f"❌ Ошибка при работе с AI: {str(e)}"
        logger.error(error_msg)
        return error_msg 