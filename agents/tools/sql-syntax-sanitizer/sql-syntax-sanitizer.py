import re
import json

def sanitize_sql(raw_sql: str) -> str:
    """
    Takes a raw, best-effort SQL query from an LLM and enforces strict syntax rules.
    This version uses a hardcoded list of schema identifiers.
    """
    schema_identifiers = [
        "FactRegisteredVehicles", "DimTime", "DimOEM", "DimVehicle", "DimGeographyCountry", 
        "DimGeographyDistrict", "time_key", "year_report", "month_report", "year_month", 
        "quarter", "year_quarter", "oem_key", "oem_name", "oem_category", "country_origin", 
        "vehicle_key", "body_type", "fuel_type", "vehicle_desc", "geography_country_key", 
        "country_name", "country_code", "geography_district_key", "region_name", 
        "district_postcode", "district_town_name", "full_location_path", 
        "vehicle_count_id", "vehicle_count"
    ]

    sanitized_sql = raw_sql

    # Rule 1: Add double quotes to all known schema identifiers.
    for identifier in sorted(schema_identifiers, key=len, reverse=True):
        pattern = r'\b(' + re.escape(identifier) + r')\b(?!["])'
        sanitized_sql = re.sub(pattern, f'"{identifier}"', sanitized_sql, flags=re.IGNORECASE)

    # Rule 2: Replace single-quoted strings with dollar-quoted strings.
    # ✅ FIX: Removed the extra backslash before the '1'
    sanitized_sql = re.sub(r"'([^']*)'", r"$$\1$$", sanitized_sql)

    return sanitized_sql

def main(params):
    """
    This is the main entry point for the IBM Code Engine Function.
    It expects a JSON object with a key 'sql_query'.
    """
    try:
        raw_query = params.get("sql_query")
        
        if not raw_query or not isinstance(raw_query, str):
            error_body = {"error": "Missing or invalid 'sql_query' parameter in the request body."}
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(error_body)
            }
            
        sanitized_query = sanitize_sql(raw_query)
        response_body = {"sanitized_query": sanitized_query}
        
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(response_body) 
        }

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        error_body = {"error": "An internal error occurred during SQL sanitization."}
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(error_body)
        }

# =================================================================
#  🚀 Local Testing Block 
# =================================================================
if __name__ == '__main__':
    # 1. Define a sample "dirty" query to test with
    test_sql_query = "SELECT oem_name, country_origin FROM DimOEM WHERE oem_name IN ('AUDI', 'PORSCHE') AND oem_category = 'Luxury'"

    # 2. Simulate the 'params' dictionary that the cloud function expects
    test_params = {
        "sql_query": test_sql_query
    }

    # 3. Call the main function directly with the test parameters
    print("--- Running Local Test ---")
    print(f"Original Query:\n{test_sql_query}\n")
    
    function_result = main(test_params)

    # 4. Unpack and print the results for verification
    status_code = function_result.get("statusCode")
    body_str = function_result.get("body")
    
    print(f"Function returned status code: {status_code}\n")

    if status_code == 200 and body_str:
        # The body is a JSON string, so we parse it to see the contents
        body_dict = json.loads(body_str)
        sanitized_query = body_dict.get('sanitized_query')
        print("✅ Test Successful!")
        print(f"Sanitized Query:\n{sanitized_query}")
    else:
        print("❌ Test Failed!")
        print(f"Response Body:\n{body_str}")