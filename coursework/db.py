import sqlite3
import hashlib
import random
from collections import namedtuple
from jinja2 import Template

# Функция возвращает готовый хеш
def md5sum(value):
    return hashlib.md5(value.encode()).hexdigest()


conn = sqlite3.connect('database.db')

cursor = conn.cursor()

# Пользователи
cursor.execute('''
               CREATE TABLE IF NOT EXISTS Users (
               id INTEGER PRIMARY KEY,
               name VARCHAR(30),
               age INTEGER(3),
               sex INTEGER MOT NULL DEFAULT 1,
               balance REAL,
               login VARCHAR(15),
               password VARCHAR(20)
                )''')

conn.commit()

cursor.execute('''
               CREATE TABLE IF NOT EXISTS Products (
               id INTEGER PRIMARY KEY,
               product_name VARCHAR(50),
               description TEXT,
               price REAL,
               user_id INTEGER,
               photo BLOB,
               category VARCHAR(50),
               FOREIGN KEY (user_id) REFERENCES Users(id)
               )''')

conn.commit()
conn.close()

# Регистрация
def registration():
    name = input("Name: ")
    age = int(input("Age: "))
    sex= int(input("Sex: "))
    login = input("Login: ")
    password= input("Password: ")
    
    try:
        db = sqlite3.connect("database.db")
        cursor = db.cursor()

        db.create_function("md5", 1, md5sum)

        cursor.execute("SELECT Login FROM users WHERE Login = ?", [login])
        if cursor.fetchone() is None:
            values = [name, age, sex, login, password]

            cursor.execute("INSERT INTO users (name, age, sex, login, password) VALUES(?, ?, ?, ?, md5(?))", values)
            db.commit()
        else:
            print("Логин уже существует")
            registration()
    except sqlite3.Error as e:
        print("Error", e)
    finally:
        cursor.close()
        db.close()

# Вход в аккаунт
def log_in():
    login = input("Login: ")
    password= input("Password: ")

    try:
        db = sqlite3.connect("database.db")
        cursor = db.cursor()

        db.create_function("md5", 1, md5sum)

        cursor.execute("SELECT login FROM Users WHERE login = ?", [login])
        if cursor.fetchone() is None:
            print("Логин не существует")
        else:
            cursor.execute("SELECT login FROM Users WHERE login = ? AND password = md5(?)", [login, password])
            if cursor.fetchone() is None:
                print("Пароль неверный")
            else:
                print ("ВЫ вошли!")
    except sqlite3.Error as e:
        print("Error", e)
    finally:
        cursor.close()
        db.close()

# Добавление товара
def add_product(user_id):
    product_name = input("Product's Name: ")
    description = input("Description: ")
    price = float(input("Price: "))
    photo_path = input("Photo Path: ")
    category = input("Category: ")

    try:
        db = sqlite3.connect("database.db")
        cursor = db.cursor()

        with open(photo_path, 'rb') as file:
            photo_data = file.read()

        values = [product_name, description, price, user_id, photo_data, category]
        cursor.execute("INSERT INTO Products (product_name, description, price, user_id, photo, category) VALUES (?, ?, ?, ?, ?, ?)", values)
        db.commit()
        print("Товар успешно добавлен!")
    except sqlite3.Error as e:
        print("Error", e)
    finally:
        cursor.close()
        db.close()

# Удаление товара
def delete_product(user_id, product_id):
    try:
        db = sqlite3.connect("database.db")
        cursor = db.cursor()

        cursor.execute("DELETE FROM Products WHERE id = ? AND user_id = ?", (product_id, user_id))
        if cursor.rowcount > 0:
            db.commit()
            print("Товар успешно удален!")
        else:
            print("Товар с указанным ID не найден или вы не имеете права удалить его.")
    except sqlite3.Error as e:
        print("Error", e)
    finally:
        cursor.close()
        db.close()

# registration()
# log_in()
# add_product(0)


# def get_random_product():
#     try:
#         db = sqlite3.connect("database.db")
#         cursor = db.cursor()

#         cursor.execute("SELECT * FROM Products ORDER BY RANDOM() LIMIT 1")
#         product = cursor.fetchone()
#         return product  # Возвращает кортеж с данными о товаре (id, product_name, description, price, user_id, photo, category)
#     except sqlite3.Error as e:
#         print("Error", e)
#     finally:
#         cursor.close()
#         db.close()


# Создаем namedtuple для товара
Product = namedtuple('Product', ['product_name', 'description', 'price', 'category'])

# Функция для получения случайного товара из базы данных
def get_random_product():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT product_name, description, price, category FROM Products")
    products = cursor.fetchall()

    if not products:
        return None

    # Выбираем случайный товар из списка
    random_product = random.choice(products)

    # Создаем объект Product с помощью namedtuple и возвращаем его
    return Product(*random_product)

# Получаем случайный товар из базы данных
random_item = get_random_product()

# Открываем файл с шаблоном HTML
with open('index_template.html', 'r') as file:
    template_content = file.read()

# Создаем объект шаблона Jinja2
template = Template(template_content)

# Заполняем шаблон данными о товаре
rendered_template = template.render(
    product_name=random_item[0],
    description=random_item[1],
    price=random_item[2],
    photo=random_item[3],
    category=random_item[4]
    )