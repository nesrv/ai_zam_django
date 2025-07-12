#!/usr/bin/env python3
"""
Тест для проверки загрузки Excel файлов на эндпоинт /telegram/
"""

import requests
import os

def test_excel_upload():
    """Тестирует загрузку Excel файла"""
    
    # URL эндпоинта
    url = "http://127.0.0.1:8000/telegram/send-file-to-deepseek/"
    
    # Путь к тестовому файлу
    excel_file_path = "test_construction_resources.xlsx"
    
    if not os.path.exists(excel_file_path):
        print(f"❌ Тестовый файл {excel_file_path} не найден!")
        print("Запустите: python test_excel.py")
        return False
    
    try:
        # Подготавливаем данные для отправки
        with open(excel_file_path, 'rb') as f:
            files = {
                'file': (excel_file_path, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            }
            data = {
                'message': 'Проанализируй данные из этой строительной сметы'
            }
            
            print(f"📤 Отправляю Excel файл на {url}...")
            
            # Отправляем POST запрос
            response = requests.post(url, files=files, data=data)
            
            print(f"📊 Статус ответа: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    print("✅ Файл успешно отправлен и проанализирован!")
                    print(f"📝 Ответ DeepSeek (первые 200 символов):")
                    print(result.get('generated_content', '')[:200] + "...")
                    return True
                else:
                    print(f"❌ Ошибка обработки: {result.get('error')}")
                    return False
            else:
                print(f"❌ Ошибка HTTP: {response.status_code}")
                print(f"Ответ сервера: {response.text}")
                return False
                
    except requests.exceptions.ConnectionError:
        print("❌ Не удается подключиться к серверу!")
        print("Убедитесь, что Django сервер запущен на http://127.0.0.1:8000/")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Тестирование загрузки Excel файлов в DeepSeek")
    print("=" * 50)
    
    success = test_excel_upload()
    
    if success:
        print("\n🎉 Тест пройден успешно!")
        print("Теперь можете использовать интерфейс на http://127.0.0.1:8000/telegram/")
    else:
        print("\n💥 Тест не пройден!")
        print("Проверьте настройки и попробуйте снова.")