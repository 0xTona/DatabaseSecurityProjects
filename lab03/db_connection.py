"""
db_connection.py — Kết nối SQL Server và gọi Stored Procedure.
"""

import pyodbc
from config import DB_CONFIG


def get_connection() -> pyodbc.Connection:
    """Trả về một kết nối pyodbc tới SQL Server."""
    # Nếu uid/pwd là rỗng thì dùng Windows Authentication
    if not DB_CONFIG.get('uid') or not DB_CONFIG.get('pwd'):
        conn_str = (
            f"DRIVER={{{DB_CONFIG['driver']}}};"
            f"SERVER={DB_CONFIG['server']};"
            f"DATABASE={DB_CONFIG['database']};"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=yes;"
        )
    else:
        conn_str = (
            f"DRIVER={{{DB_CONFIG['driver']}}};"
            f"SERVER={DB_CONFIG['server']};"
            f"DATABASE={DB_CONFIG['database']};"
            f"UID={DB_CONFIG['uid']};"
            f"PWD={DB_CONFIG['pwd']};"
            "TrustServerCertificate=yes;"
        )
    return pyodbc.connect(conn_str)


def call_sp(sp_name: str, params: dict) -> list:
    """
    Gọi một Stored Procedure với các tham số dạng dict.
    Trả về danh sách các row (list of Row objects).
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        placeholders = ",".join(["?" for _ in params])
        sql = f"EXEC {sp_name} {placeholders}" if params else f"EXEC {sp_name}"
        values = tuple(params.values())
        cursor.execute(sql, values) if params else cursor.execute(sql)

        result = []
        if cursor.description:
            result = cursor.fetchall()

        conn.commit()
        return result
    finally:
        conn.close()
