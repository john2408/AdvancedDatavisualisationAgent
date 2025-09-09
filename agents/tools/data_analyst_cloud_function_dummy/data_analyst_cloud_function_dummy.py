import json

def main(params):
    """
    Dummy IBM Cloud Code Engine function.
    This final version uses a more explicit return structure to ensure the
    response body is correctly processed by the platform.
    """
    
    print("Dummy function invoked.")

    try:
        # This is the pre-fabricated data summary.
        hardcoded_data_summary = {
            "columns": [
                "year_month",
                "total_registrations"
            ],
            "shape": [
                12,
                2
            ],
            "dtypes": {
                "year_month": "object",
                "total_registrations": "int64"
            },
            "sample_data": [
                {"year_month": "2023-01", "total_registrations": 1450},
                {"year_month": "2023-02", "total_registrations": 1620},
                {"year_month": "2023-03", "total_registrations": 2150},
                {"year_month": "2023-04", "total_registrations": 1890},
                {"year_month": "2023-05", "total_registrations": 2300},
                {"year_month": "2023-06", "total_registrations": 1950},
                {"year_month": "2023-07", "total_registrations": 2100},
                {"year_month": "2023-08", "total_registrations": 2200},
                {"year_month": "2023-09", "total_registrations": 2400},
                {"year_month": "2023-10", "total_registrations": 2500},
                {"year_month": "2023-11", "total_registrations": 2600},
                {"year_month": "2023-12", "total_registrations": 2700}
            ]
        }

        response_payload = {
            "success": True,
            "data_summary": hardcoded_data_summary
        }
        
        print(f"Function finished. Preparing to return explicit HTTP response.")

        # --- THE FIX ---
        # Instead of just returning the dictionary, we wrap it in a structure
        # that explicitly defines the HTTP response details. We also convert
        # the body to a JSON string ourselves.
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps(response_payload)
        }

    except Exception as e:
        # This will catch any error that happens inside the function
        error_message = f"An unexpected error occurred inside the dummy function: {e}"
        print(error_message)
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({"error": error_message})
        }

