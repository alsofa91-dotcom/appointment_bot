from database.db import init_db
from database.models import add_master, add_service

# 1️⃣ Создаём таблицы
init_db()

# 2️⃣ Добавляем мастеров
masters = ["Иван", "Мария", "Алексей"]
for m in masters:
    add_master(m)
print(f"✅ Добавлены мастера: {', '.join(masters)}")

# 3️⃣ Добавляем услуги
services = [
    ("Стрижка", 30),
    ("Окрашивание", 60),
    ("Маникюр", 45)
]
for name, duration in services:
    add_service(name, duration)
print(f"✅ Добавлены услуги: {', '.join([s[0] for s in services])}")
