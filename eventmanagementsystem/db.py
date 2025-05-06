import mysql.connector

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Latha@17",
        database="eventmanagementsystem"
    )

def fetch_tables(db):
    cursor = db.cursor()
    cursor.execute("SHOW TABLES")
    return [table[0] for table in cursor.fetchall()]