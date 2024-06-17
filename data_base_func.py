import sqlite3

# Создание базы данных и таблиц
def create_db(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Создаем таблицу Sections
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Sections (
        section_id INTEGER PRIMARY KEY,
        section_text TEXT NOT NULL
    )
    ''')
    
    # Создаем таблицу Points
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Points (
        point_id INTEGER PRIMARY KEY,
        section_id INTEGER,
        point_text TEXT NOT NULL,
        FOREIGN KEY (section_id) REFERENCES Sections (section_id)
    )
    ''')
    
    conn.commit()
    conn.close()

# Функция для добавлеения столбца в таблицу
def add_text_column_to_table(table_name, column_name, db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute(f'''ALTER TABLE {table_name} ADD COLUMN {column_name} INTEGER''')

    conn.commit()
    conn.close()

# Функция для добавления раздела в базу данных
def add_section(section_id, section_text, db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO Sections (section_id, section_text)
    VALUES (?, ?)
    ''', (section_id, section_text))
    
    conn.commit()
    conn.close()

# Функция для добавления пункта в базу данных
def add_point(point_id, point_text, db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO Points (point_id, section_id, point_text)
    VALUES (?, ?, ?)
    ''', (point_id, 1, point_text))
    
    conn.commit()
    conn.close()

# Функция для получения пунктна по его номеру из базы данных
def get_point_by_id(point_id, db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM Points WHERE point_id = ?', (point_id,))
    point = cursor.fetchone()
    conn.close()
    return point[2]

# Функция для получения всех разделов из базы данных
def get_all_sections(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM Sections')
    sections = cursor.fetchall()
    
    conn.close()
    return sections

# Функция для получения раздела из базы данных
def get_one_section(section_id, db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM Sections WHERE section_id = ?', (section_id,))
    section = cursor.fetchone()
    
    conn.close()
    return section 

# Функция для получения всех пунктов раздела из базы данных
def get_points_by_section(section_id, db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM Sections WHERE section_id = ?', (section_id,))
    section = cursor.fetchone()
    
    conn.close()
    return f"Раздел {section[0]}. {section[1]}. Пункты: {section[2]}"
    
# Функция для получения предыдущего пункта
def get_previous_point(point_id, db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    cursor.execute('SELECT point_id FROM Points WHERE point_id < ? ORDER BY point_id DESC LIMIT 1', (point_id,))
    prev_point = cursor.fetchone()
    
    conn.close()
    return prev_point[0] if prev_point else None

# Функция для получения следующего пункта
def get_next_point(point_id, db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    cursor.execute('SELECT point_id FROM Points WHERE point_id > ? ORDER BY point_id ASC LIMIT 1', (point_id,))
    next_point = cursor.fetchone()
    
    conn.close()
    return next_point[0] if next_point else None

# Функция для присвоения пунктам номера раздела в базе данных
def assign_point_to_section(section_id, point_id, db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Проверяет есть ли такой пункт в базе данных
    if check_point_exists(point_id, db_name):
        cursor.execute('''
        UPDATE Points
        SET section_id = ?
        WHERE point_id = ?
        ''', (section_id, point_id))
        conn.commit()
        print(f"Пункт с номером {point_id} был присвоен к разделу {section_id}.")
    else:
        print(f"Пункт с номером {point_id} не найден в базе данных.")
    
    conn.close()

# Функция для проверки существования пункта по его номеру в базе данных
def check_point_exists(point_id, db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    cursor.execute('SELECT 1 FROM Points WHERE point_id = ?', (point_id,))
    exists = cursor.fetchone() is not None
    
    conn.close()
    return exists

# Функция для экранирования специальных символов в тексте для MarkdownV2
def escape_markdown_v2(text):
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text

# Функция для добавления пункта в базу данных, с проверкой, нет ли его уже в базе
def add_point_if_not_exists(point_id, point_text, db_name):
    if not check_point_exists(point_id, db_name):
        add_point(point_id, point_text, db_name)


def double_newlines(text):
    """
    Функция принимает строку и заменяет все одиночные переносы строк на двойные.

    :param text: Исходная строка
    :return: Строка с двойными переносами строк
    """
    return text.replace('\n', '\n\n')
