import os
import base64
import json
import pandas as pd
import psycopg2
from psycopg2 import OperationalError

# --- Database Utility Function (with Debugging) ---
def run_postgres_query(query: str) -> pd.DataFrame:
    """
    Executes a SQL query against a PostgreSQL database using credentials
    from environment variables and returns a pandas DataFrame.
    """
    cert_path = None
    try:
        # --- NEW: Print environment variables to verify they are loaded ---
        print("[DEBUG] Reading environment variables...")
        db_host = os.environ.get('DB_HOST')
        db_cert_b64 = os.environ.get('DB_CERT_B64')
        print(f"[DEBUG] DB_HOST found: {'Yes' if db_host else 'No'}")
        print(f"[DEBUG] DB_CERT_B64 found: {'Yes' if db_cert_b64 else 'No'}")
        # --- End of New Code ---

        if not db_cert_b64:
            raise ValueError("DB_CERT_B64 environment variable is not set.")
            
        cert_path = '/tmp/ca.crt'
        with open(cert_path, 'wb') as f:
            f.write(base64.b64decode(db_cert_b64))

        conn = psycopg2.connect(
            host=db_host,
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

# --- Main Cloud Function Logic (with Debugging) ---
def main(params):
    """
    Main function logic with added debugging prints.
    """
    sql_query = params.get('sql_query')

    if not sql_query:
        return {
            "statusCode": 400, "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Missing 'sql_query' in input parameters."})
        }

    print(f"Executing query: {sql_query}")
    result_df = run_postgres_query(sql_query)

    # --- NEW: Print the type and value of the result ---
    print(f"[DEBUG] Value returned from run_postgres_query: {result_df}")
    print(f"[DEBUG] Type of result_df: {type(result_df)}")
    # --- End of New Code ---

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
        "sample_data": result_df.head(5).to_dict(orient="records")
    }
    
    response_payload = {"success": True, "data_summary": data_summary}
    
    return {
        "statusCode": 200, "headers": {"Content-Type": "application/json"},
        "body": json.dumps(response_payload)
    }

