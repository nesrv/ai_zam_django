в app ai сделай чат-бота на основе данных файла docs\for_ai_chat_bot\menu_bot.py
на http://127.0.0.1:8000/ai/ выведи информацию о подкючении


теперь нужно реализовать хостинг чат-бота на основе этой информации docs\for_ai_chat_bot\chat_bot_cpanel.md


curl "https://api.telegram.org/bot7606767600:AAFGN18TMl0pUQIsQzaKiozmMKe0KBeSjyE/getWebhookInfo"

 https://api.telegram.org/bot7606767600:AAFGN18TMl0pUQIsQzaKiozmMKe0KBeSjyE/setWebhook?url=https://programism.ru/telegram-webhook/

 {
  "ok": true,
  "result": true,
  "description": "Webhook was set"
}

  curl -X POST https://programism.ru/telegram/webhook/ -d '{123}'