# 📊 Sales Dashboard

> Аналитический дашборд для визуализации продаж с JWT авторизацией

## 🚀 Технологии

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=JSON%20web%20tokens)

### Тестовые пользователи
Логин	Пароль	Роль
admin	admin123	Администратор
user	user123	Пользователь

## 📊 Функционал
✅ JWT авторизация с логином/паролем
✅ Регистрация новых пользователей
✅ Интерактивный дашборд с графиками
✅ Фильтрация по категориям и товарам
✅ Экспорт данных в CSV
✅ Автодокументация API

## 📝 API Endpoints
  Метод	Путь	Описание
  POST	/login	Получение JWT токена
  POST	/register	Регистрация
  GET	/sales	Список продаж
  GET	/sales/stats	Статистика
  GET	/sales/by_category	Выручка по категориям
  GET	/sales/top_products	Топ товаров

## 🔒 Безопасность
  JWT токены с ограниченным временем жизни (30 мин)
  Хеширование паролей (SHA256)
  Защита всех эндпоинтов, кроме /login и /register
  
## ⚡ Быстрый старт
### Установка
```bash
git clone https://github.com/asojima/dashboard-sales.git
cd dashboard-sales
pip install -r requirements.txt

```
# 1. Инициализация БД
python init_db.py

# 2. Запуск бэкенда
uvicorn main:app --reload --port 8000

# 3. Запуск дашборда (в новом терминале)
streamlit run dashboard.py
