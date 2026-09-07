from database import engine, SessionLocal, Sale, Base  # ← добавил Base
import random
from datetime import datetime, timedelta

# Создаем таблицы
Base.metadata.create_all(engine)

db = SessionLocal()

# Проверяем, есть ли уже данные
if db.query(Sale).count() == 0:
    products = [
        ('iPhone 15', 'Electronics'),
        ('MacBook Pro', 'Electronics'), 
        ('Python Book', 'Education'),
        ('Pen Set', 'Stationery'),
        ('iPad Air', 'Electronics'),
        ('Notebook', 'Stationery'),
        ('Course', 'Education'),
        ('Keyboard', 'Electronics')
    ]
    
    for _ in range(100):
        product, cat = random.choice(products)
        db.add(Sale(
            product=product,
            category=cat,
            price=round(random.uniform(10, 1500), 2),
            quantity=random.randint(1, 15),
            date=datetime.now() - timedelta(days=random.randint(0, 60))
        ))
    db.commit()
    print("✅ База заполнена тестовыми данными!")
else:
    print("ℹ️ Данные уже есть в базе")

db.close()