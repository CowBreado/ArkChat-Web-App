import sqlite3
import bcrypt
import os

#Connect to the database path 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, f'{"practice"}.db')

def hash_password(password):
    #Convert the password into bytes so bcrypt can be used
    password = password.encode('utf-8')
    #Hash the converted bytes using bcrypt 
    hashed_password = bcrypt.hashpw(password, bcrypt.gensalt()).decode()
    return hashed_password 

def open_db():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    return connection, cursor

def close_db(connection):
    print("Closing database connection")
    return connection.close()

#Crud operations 
def get_users():
    connection, cursor = open_db()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    close_db(connection)
    return users
def get_user_by_username(username):
    connection, cursor = open_db()
    cursor.execute("SELECT * FROM users WHERE lower(username) = ?", (username.lower(), ))
    queried_user = cursor.fetchone()
    close_db(connection)
    return queried_user

def get_user_by_id(user_id):
    connection, cursor = open_db()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id, ))
    queried_user = cursor.fetchone()
    close_db(connection)
    return queried_user

def get_user_conversations(user_id):
    connection, cursor = open_db()
    #Query all conversation title that belongs to the current session id or user id
    cursor.execute("""
    SELECT conversations.title, conversations.created_at, conversations.id FROM USERS 
        JOIN conversation_participants ON conversation_participants.user_id=users.id
        JOIN conversations ON conversations.id = conversation_participants.conversation_id
        WHERE users.id =?
    """, (user_id,))
    current_conversations = cursor.fetchall()
    close_db(connection)
    return current_conversations


def get_conversation_chat_log(conversation_id):
    connection, cursor = open_db()
    cursor.execute("""
    SELECT * from messages WHERE conversation_id = ?""",(conversation_id,))
    messages = cursor.fetchall()
    close_db(connection)
    return messages

def get_conversation_by_id(conversation_id):
    connection, cursor = open_db()
    cursor.execute("""
    SELECT * FROM conversations WHERE id = ?
    """,(conversation_id,))
    conversation = cursor.fetchone()
    close_db(connection)
    return conversation

def send_conversation_message(current_user_id, conversation_id,message_content):
    connection, cursor = open_db()
    cursor.execute("""
    INSERT INTO messages (user_id, conversation_id, content)
    VALUES (?,?,?)
    """,(current_user_id, conversation_id, message_content,))
    connection.commit()
    close_db(connection)
    return

def create_conversation(participant_username):
    connection, cursor = open_db()
    cursor.execute("""
    INSERT INTO conversations (title)
    VALUES(?)
    """, (participant_username,))
    conversation_id = cursor.lastrowid
    connection.commit()
    close_db(connection)
    return conversation_id 

def add_conversation_participant(user_id, conversation_id):
    connection, cursor = open_db()
    cursor.execute("""
    INSERT INTO conversation_participants (user_id, conversation_id)
    VALUES(?,?)
    """,(user_id,conversation_id))
    connection.commit()
    close_db(connection)
    return f'Added user_id: {user_id} to conversation_id: {conversation_id}'


#Get the other participant, not the current session id
def get_other_conversation_participant_by_id(conversation_id, user_id):
    connection,cursor = open_db()
    #Combine conversation_participants and users table 
    cursor.execute("""
    SELECT * FROM conversation_participants
    JOIN users ON conversation_participants.user_id = users.id
    WHERE conversation_participants.conversation_id = ?
    AND conversation_participants.user_id != ?
    """,(conversation_id,user_id))
    other_participant = cursor.fetchone()
    return other_participant

def create_user(username, password, age):
    connection, cursor = open_db()
    password = hash_password(password)
    cursor.execute("INSERT INTO users (username, password, age) VALUES(?,?,?)", (username, password, age))
    connection.commit()
    close_db(connection)

def update_user(new_username, new_password, new_age, user_id):
    connection, cursor = open_db()
    new_password = hash_password(new_password)
    cursor.execute("UPDATE users SET username = ?, password = ?, age = ? WHERE id = ?", 
    (new_username, new_password,new_age,user_id)
    )
    connection.commit()
    close_db(connection)

def delete_user(user_id):
    connection, cursor = open_db()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id, ))
    connection.commit()
    close_db(connection)

def verify_password(username, input_password):
    user = get_user_by_username(username)  
    if user is None:
        return {
            "status":"error",
            "message":"login failed, username does not exist"
        }
    hashed_password = user["password"].encode('utf-8')
    input_password = input_password.encode('utf-8')
    if bcrypt.checkpw(input_password, hashed_password):
        return {
            "status":"success",
            "message":"login success"
        }
    return {
        "status":"error",
        "message":"login failed, invalid password"
    }

