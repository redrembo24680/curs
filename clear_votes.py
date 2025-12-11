"""Script to clear all votes from both databases."""
import sqlite3
import os


def clear_flask_votes():
    """Clear votes from Flask database."""
    flask_db = os.path.join('web_flask', 'data', 'database.sqlite')
    if not os.path.exists(flask_db):
        print(f"Flask database not found: {flask_db}")
        return

    conn = sqlite3.connect(flask_db)
    cursor = conn.cursor()

    try:
        # Clear user_votes table
        cursor.execute("DELETE FROM user_votes")
        conn.commit()
        deleted = cursor.rowcount
        print(f"✓ Видалено {deleted} голосів з Flask database (user_votes)")
    except Exception as e:
        print(f"✗ Помилка очищення Flask database: {e}")
    finally:
        conn.close()


def clear_cpp_votes():
    """Clear votes from C++ backend database."""
    cpp_db = os.path.join('server_cpp', 'data', 'voting.db')
    if not os.path.exists(cpp_db):
        print(f"C++ database not found: {cpp_db}")
        return

    conn = sqlite3.connect(cpp_db)
    cursor = conn.cursor()

    try:
        # Clear votes table
        cursor.execute("DELETE FROM votes")
        conn.commit()
        deleted_votes = cursor.rowcount
        print(f"✓ Видалено {deleted_votes} записів з C++ database (votes)")

        # Reset player votes to 0
        cursor.execute("UPDATE players SET votes = 0")
        conn.commit()
        updated_players = cursor.rowcount
        print(f"✓ Скинуто votes для {updated_players} гравців")

    except Exception as e:
        print(f"✗ Помилка очищення C++ database: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    print("=== Очищення голосів з баз даних ===\n")

    print("1. Flask database:")
    clear_flask_votes()

    print("\n2. C++ backend database:")
    clear_cpp_votes()

    print("\n=== Готово! Всі голоси видалено ===")
    print("\nТепер перезапусти контейнери:")
    print("docker-compose restart")
