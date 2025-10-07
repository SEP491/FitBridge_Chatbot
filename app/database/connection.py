# app/database/connection.py - Database connection and configuration

import psycopg
from config import DATABASE_CONFIG

# Cấu hình cơ sở dữ liệu PostgreSQL (adjust for psycopg3 naming)
db_config = {
    'host': DATABASE_CONFIG['host'],
    'dbname': DATABASE_CONFIG['database'],  # psycopg3 sử dụng 'dbname' thay vì 'database'
    'user': DATABASE_CONFIG['user'],
    'password': DATABASE_CONFIG['password'],
    'port': DATABASE_CONFIG['port'],
    'sslmode': 'prefer'
}

# Kết nối cơ sở dữ liệu PostgreSQL
try:
    print("Đang kết nối đến cơ sở dữ liệu PostgreSQL...")
    print(f"Host: {db_config['host']}")
    print(f"Database: {db_config['dbname']}")
    print(f"Port: {db_config['port']}")
    
    conn = psycopg.connect(**db_config)
    cursor = conn.cursor(row_factory=psycopg.rows.dict_row)
    print("Kết nối cơ sở dữ liệu PostgreSQL thành công!")
    
except psycopg.Error as e:
    print(f"Kết nối cơ sở dữ liệu thất bại: {e}")
    print("Vui lòng kiểm tra cấu hình cơ sở dữ liệu PostgreSQL")
    conn = None
    cursor = None

def get_database_connection():
    """Trả về kết nối cơ sở dữ liệu"""
    return conn, cursor

def query_database(query):
    """Hàm truy vấn cơ sở dữ liệu"""
    if conn is None or cursor is None:
        print("Kết nối cơ sở dữ liệu không khả dụng")
        return "Lỗi kết nối cơ sở dữ liệu"
    
    try:
        print(f"Đang thực thi truy vấn: {query}")
        cursor.execute(query)
        results = cursor.fetchall()
        print(f"Kết quả truy vấn: {len(results)} hàng")
        return results
    except psycopg.Error as e:
        print(f"Lỗi cơ sở dữ liệu: {str(e)}")
        return f"Lỗi cơ sở dữ liệu: {str(e)}"