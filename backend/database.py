import os
import bcrypt
import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

load_dotenv()

def hash_password(password):
    password_bytes = password.encode("utf-8")
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")

def open_db():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")

    connection = psycopg.connect(database_url, row_factory=dict_row)
    cursor = connection.cursor()
    return connection, cursor

def close_db(connection):
    connection.close()


# CRUD operations
def get_users():
    connection, cursor = open_db()
    try:
        cursor.execute("SELECT * FROM users")
        return cursor.fetchall()
    finally:
        cursor.close()
        close_db(connection)


def get_user_by_username(username):
    connection, cursor = open_db()
    try:
        cursor.execute(
            "SELECT * FROM users WHERE LOWER(username) = %s",
            (username.lower(),),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        close_db(connection)


def get_user_by_id(user_id):
    connection, cursor = open_db()
    try:
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        close_db(connection)


def get_user_conversations(user_id):
    connection, cursor = open_db()
    try:
        cursor.execute(
            """
            SELECT conversations.title,
                   conversations.created_at,
                   conversations.id
            FROM users
            JOIN conversation_participants
              ON conversation_participants.user_id = users.id
            JOIN conversations
              ON conversations.id = conversation_participants.conversation_id
            WHERE users.id = %s
            ORDER BY conversations.created_at DESC
            """,
            (user_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        close_db(connection)


def get_conversation_chat_log(conversation_id):
    connection, cursor = open_db()
    try:
        cursor.execute(
            """
            SELECT *
            FROM messages
            WHERE conversation_id = %s
            ORDER BY created_at ASC, id ASC
            """,
            (conversation_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        close_db(connection)


def get_conversation_by_id(conversation_id):
    connection, cursor = open_db()
    try:
        cursor.execute(
            "SELECT * FROM conversations WHERE id = %s",
            (conversation_id,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        close_db(connection)


def send_conversation_message(current_user_id, conversation_id, message_content):
    connection, cursor = open_db()
    try:
        cursor.execute(
            """
            INSERT INTO messages (user_id, conversation_id, content)
            VALUES (%s, %s, %s)
            """,
            (current_user_id, conversation_id, message_content),
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        close_db(connection)


def create_conversation(participant_username):
    connection, cursor = open_db()
    try:
        cursor.execute(
            """
            INSERT INTO conversations (title)
            VALUES (%s)
            RETURNING id
            """,
            (participant_username,),
        )
        conversation_id = cursor.fetchone()["id"]
        connection.commit()
        return conversation_id
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        close_db(connection)


def add_conversation_participant(user_id, conversation_id):
    connection, cursor = open_db()
    try:
        cursor.execute(
            """
            INSERT INTO conversation_participants (user_id, conversation_id)
            VALUES (%s, %s)
            """,
            (user_id, conversation_id),
        )
        connection.commit()
        return f"Added user_id: {user_id} to conversation_id: {conversation_id}"
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        close_db(connection)


def get_other_conversation_participant_by_id(conversation_id, user_id):
    connection, cursor = open_db()
    try:
        cursor.execute(
            """
            SELECT users.*
            FROM conversation_participants
            JOIN users ON conversation_participants.user_id = users.id
            WHERE conversation_participants.conversation_id = %s
              AND conversation_participants.user_id != %s
            """,
            (conversation_id, user_id),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        close_db(connection)


def create_user(username, password, age):
    connection, cursor = open_db()
    try:
        hashed_password = hash_password(password)
        cursor.execute(
            """
            INSERT INTO users (username, password, age)
            VALUES (%s, %s, %s)
            """,
            (username, hashed_password, age),
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        close_db(connection)


def update_user(new_username, new_password, new_age, user_id):
    connection, cursor = open_db()
    try:
        hashed_password = hash_password(new_password)
        cursor.execute(
            """
            UPDATE users
            SET username = %s, password = %s, age = %s
            WHERE id = %s
            """,
            (new_username, hashed_password, new_age, user_id),
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        close_db(connection)


def delete_user(user_id):
    connection, cursor = open_db()
    try:
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        close_db(connection)


def verify_password(username, input_password):
    user = get_user_by_username(username)

    if user is None:
        return {
            "status": "error",
            "message": "login failed, username does not exist",
        }

    hashed_password = user["password"].encode("utf-8")
    input_password_bytes = input_password.encode("utf-8")

    if bcrypt.checkpw(input_password_bytes, hashed_password):
        return {"status": "success", "message": "login success"}
    return {"status": "error", "message": "login failed, invalid password"}
