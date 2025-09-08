import os
import base64
import json
import pandas as pd
import psycopg2
from psycopg2 import OperationalError

cert_b64 = "LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUREekNDQWZlZ0F3SUJBZ0lKQU5FSDU4eTIva3pITUEwR0NTcUdTSWIzRFFFQkN3VUFNQjR4SERBYUJnTlYKQkFNTUUwbENUU0JEYkc5MVpDQkVZWFJoWW1GelpYTXdIaGNOTVRnd05qSTFNVFF5T1RBd1doY05Namd3TmpJeQpNVFF5T1RBd1dqQWVNUnd3R2dZRFZRUUREQk5KUWswZ1EyeHZkV1FnUkdGMFlXSmhjMlZ6TUlJQklqQU5CZ2txCmhraUc5dzBCQVFFRkFBT0NBUThBTUlJQkNnS0NBUUVBOGxwYVFHemNGZEdxZU1sbXFqZmZNUHBJUWhxcGQ4cUoKUHIzYklrclhKYlRjSko5dUlja1NVY0NqdzRaL3JTZzhublQxM1NDY09sKzF0bys3a2RNaVU4cU9XS2ljZVlaNQp5K3laWWZDa0dhaVpWZmF6UUJtNDV6QnRGV3YrQUIvOGhmQ1RkTkY3Vlk0c3BhQTNvQkUyYVM3T0FOTlNSWlNLCnB3eTI0SVVnVWNJTEpXK21jdlc4MFZ4K0dYUmZEOVl0dDZQUkpnQmhZdVVCcGd6dm5nbUNNR0JuK2wyS05pU2YKd2VvdllEQ0Q2Vm5nbDIrNlc5UUZBRnRXWFdnRjNpRFFENW5sL240bXJpcE1TWDZVRy9uNjY1N3U3VERkZ2t2QQoxZUtJMkZMellLcG9LQmU1cmNuck03bkhnTmMvbkNkRXM1SmVjSGIxZEh2MVFmUG02cHpJeHdJREFRQUJvMUF3ClRqQWRCZ05WSFE0RUZnUVVLMytYWm8xd3lLcytERW9ZWGJIcnV3U3BYamd3SHdZRFZSMGpCQmd3Rm9BVUszK1gKWm8xd3lLcytERW9ZWGJIcnV3U3BYamd3REFZRFZSMFRCQVV3QXdFQi96QU5CZ2txaGtpRzl3MEJBUXNGQUFPQwpBUUVBSmY1ZHZselVwcWFpeDI2cUpFdXFGRzBJUDU3UVFJNVRDUko2WHQvc3VwUkhvNjNlRHZLdzh6Ujd0bFdRCmxWNVAwTjJ4d3VTbDlacUFKdDcvay8zWmVCK25Zd1BveU8zS3ZLdkFUdW5SdmxQQm40RldWWGVhUHNHKzdmaFMKcXNlam1reW9uWXc3N0hSekdPekpINFpnOFVONm1mcGJhV1NzeWFFeHZxa25DcDlTb1RRUDNENjdBeldxYjF6WQpkb3FxZ0dJWjJueENrcDUvRlh4Ri9UTWI1NXZ0ZVRRd2ZnQnk2MGpWVmtiRjdlVk9XQ3YwS2FOSFBGNWhycWJOCmkrM1hqSjcvcGVGM3hNdlRNb3kzNURjVDNFMlplU1Zqb3VaczE1Tzkwa0kzazJkYVMyT0hKQUJXMHZTajRuTHoKK1BRenAvQjljUW1PTzhkQ2UwNDlRM29hVUE9PQotLS0tLUVORCBDRVJUSUZJQ0FURS0tLS0tCgo="

# --- Database Utility Function ---
def run_postgres_query(query: str) -> pd.DataFrame:
    """
    Executes a SQL query against a PostgreSQL database using credentials
    from environment variables and returns a pandas DataFrame.
    """
    cert_path = None
    try:
        # Decode the base64 certificate and write it to a temporary file
        if not cert_b64:
            raise ValueError("DB_CERT_B64 environment variable is not set.")
            
        cert_path = '/tmp/ca.crt'
        with open(cert_path, 'wb') as f:
            f.write(base64.b64decode(cert_b64))

        # Establish the database connection
        conn = psycopg2.connect(
            host="77ffc5dd-8640-4646-a7a6-beb1dea99edb.bn2a2uid0up8mv7mv2ig.databases.appdomain.cloud",
            port="31173",
            dbname="ibmclouddb",
            user="ibm_cloud_0a0913bc_2444_4373_a330_c4fda9f8afdc",
            password="P9SPEyCFa2wKhnNuztRq2DcsNj73JTUS",
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
        # Clean up the temporary certificate file
        if cert_path and os.path.exists(cert_path):
            os.remove(cert_path)

# --- Main Cloud Function Logic ---
def main(params):
    """
    IBM Cloud Code Engine entry point.
    This function acts as a tool for a watsonx.orchestrate agent.
    It receives a SQL query, executes it, and returns a summary of the data.
    """
    sql_query = params.get('sql_query')

    if not sql_query:
        return {"error": "Missing 'sql_query' in input parameters."}

    # 1. Execute the SQL Query against the database
    print(f"Executing query: {sql_query}")
    result_df = run_postgres_query(sql_query)

    # 2. Check for errors or empty results
    if "Error" in result_df.columns or result_df.empty:
        error_message = result_df['Error'].iloc[0] if "Error" in result_df.columns else "Query returned no data."
        print(f"Query execution failed: {error_message}")
        return {"error": error_message, "status": "QUERY_FAILED"}

    # 3. If successful, prepare and return the data summary
    print(f"Query successful. Found {result_df.shape[0]} rows. Preparing summary.")
    
    # This is the exact output structure your Data Analyst Agent needs
    data_summary = {
        "columns": list(result_df.columns),
        "shape": result_df.shape,
        "dtypes": {col: str(dtype) for col, dtype in result_df.dtypes.items()},
        "sample_data": result_df.head(5).to_dict(orient="records")
    }

    return {
        "success": True,
        "data_summary": data_summary
    }

