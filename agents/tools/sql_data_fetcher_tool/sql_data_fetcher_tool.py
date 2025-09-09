import os
import base64
import json
import pandas as pd
import psycopg2
from psycopg2 import OperationalError

# --- Database Utility Function ---
def run_postgres_query(query: str) -> pd.DataFrame:
    cert_path = None
    try:
        cert_b64 = os.environ.get('DB_CERT_B64')
        if not cert_b64:
            raise ValueError("DB_CERT_B64 environment variable is not set.")
        cert_path = '/tmp/ca.crt'
        with open(cert_path, 'wb') as f:
            f.write(base64.b64decode(cert_b64))
        conn = psycopg2.connect(
            host=os.environ.get('DB_HOST'),
            port=os.environ.get('DB_PORT'),
            dbname=os.environ.get('DB_NAME'),
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASSWORD'),
            sslmode='verify-full',
            sslrootcert=cert_path
        )
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except (OperationalError, ValueError) as e:
        return pd.DataFrame({"Error": [f"Database connection or query failed: {e}"]})
    except Exception as e:
        return pd.DataFrame({"Error": [f"An unexpected error occurred: {e}"]})
    finally:
        if cert_path and os.path.exists(cert_path):
            os.remove(cert_path)

# --- Main Cloud Function Logic ---
def main(params):
    sql_query = params.get('sql_query')
    if not sql_query:
        return {
            "statusCode": 400, "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Missing 'sql_query' in input parameters."})
        }
    print(f"Executing query: {sql_query}")
    result_df = run_postgres_query(sql_query)
    if result_df is None or "Error" in result_df.columns or result_df.empty:
        error_message = "Query returned None or was empty."
        if result_df is not None and "Error" in result_df.columns:
            error_message = result_df['Error'].iloc[0]
        elif result_df is not None and result_df.empty:
            error_message = "Query returned no data."
        print(f"Query execution failed: {error_message}")
        return {
            "statusCode": 500, "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": error_message, "status": "QUERY_FAILED"})
        }
    print(f"Query successful. Found {result_df.shape[0]} rows. Preparing summary.")
    data_summary = {
        "columns": list(result_df.columns),
        "shape": list(result_df.shape),
        "dtypes": {col: str(dtype) for col, dtype in result_df.dtypes.items()},
        "sample__data": result_df.head(5).to_dict(orient="records")
    }
    response_payload = {"success": True, "data_summary": data_summary}
    return {
        "statusCode": 200, "headers": {"Content-Type": "application/json"},
        "body": json.dumps(response_payload)
    }

