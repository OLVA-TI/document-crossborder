import os
import cx_Oracle
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    connection = cx_Oracle.connect(
        user=os.getenv("DB_USERNAME"),
        password=os.getenv("DB_PASSWORD"),
        dsn=f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_DATABASE')}"
    )
    return connection
