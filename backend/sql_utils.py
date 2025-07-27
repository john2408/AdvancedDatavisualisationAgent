import sqlite3
import pandas as pd

def run_query(query, db_path: str) -> pd.DataFrame:
    """Execute SQL query and return pandas DataFrame"""
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        # Return an empty DataFrame with error information
        return pd.DataFrame({"Error": [f"Query failed: {e}"]})

def get_db_schema(db_path: str) -> str:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    schema = ""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table_name, in tables:
        cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}';")
        create_stmt = cursor.fetchone()[0]
        schema += create_stmt + ";\n\n"
    conn.close()
    return schema

def get_structured_schema(db_path: str) -> str:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    lines = ["Available tables and columns:"]
    for table_name, in tables:
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]
        lines.append(f"- {table_name}: {', '.join(columns)}")
    conn.close()
    return '\n'.join(lines)

