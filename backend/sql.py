
import sqlite3
import json


def create_sql_tables():
    # check db for username
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    # create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL
        )
    ''')
    # create conversations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sender_id) REFERENCES users(id),
            FOREIGN KEY (receiver_id) REFERENCES users(id)
        )
    ''')

    # create sequences tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sequences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            step_number INTEGER NOT NULL,
            content TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # add AI as user in table if not exists
    cursor.execute("SELECT id FROM users WHERE username = ?", ('AI',))
    if cursor.fetchone() is None:
        cursor.execute('''
            INSERT INTO users (username) VALUES (?)
        ''', ('AI',))

    conn.commit()
    conn.close()

def get_all_messages_sql(username):
    # check db for username
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    print("checking user messages")
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    messages = []
    if user:
        user_id = user[0]
        cursor.execute("SELECT sender_id, receiver_id, content, timestamp FROM conversations WHERE sender_id = ? OR receiver_id = ?", (user_id, user_id))
        messages = cursor.fetchall()
    else:
        cursor.execute("INSERT INTO users (username) VALUES (?)", (username,))
        conn.commit()

    conn.close()
    print(messages)            
    return messages

def get_user_id(username):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    user_id = user[0] if user else None
    
    conn.close()
    return user_id

def add_to_conversation(sender_id, receiver_id, content):
    # Save the generated question to the database
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO conversations (sender_id, receiver_id, content) VALUES (?, ?, ?)", (sender_id, receiver_id, content))
    
    conn.commit()
    conn.close()

def get_sequence(username):
    try:
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()

        # Get the user_id for the given username
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if not user:
            return None

        user_id = user[0]

        # Get the sequence for the user
        cursor.execute("SELECT step_number, content FROM sequences WHERE user_id = ? ORDER BY step_number", (user_id,))
        sequence = cursor.fetchall()

        # Format the sequence as a list of dictionaries
        sequence_data = [{"step_number": step[0], "content": step[1]} for step in sequence]

        return sequence_data
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return None
    finally:
        if conn:
            conn.close()
def set_sequence(user_id, sequence):
    try:
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()

        # Parse the JSON sequence
        sequence_data = json.loads(sequence)

        # Delete existing sequence data for the user
        cursor.execute("DELETE FROM sequences WHERE user_id = ?", (user_id,))

        # Insert each step into the sequences table
        for step in sequence_data["data"]:
            step_number = step["step_number"]
            content = step["step_info"]
            cursor.execute("INSERT INTO sequences (user_id, step_number, content) VALUES (?, ?, ?)", (user_id, step_number, content))

        conn.commit()
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if conn:
            conn.close()
