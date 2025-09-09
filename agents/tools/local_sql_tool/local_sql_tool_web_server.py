from flask import Flask, request, jsonify
import json
from local_sql_tool import main as execute_sql_tool

app = Flask(__name__)

@app.route('/', methods=['POST'])
def handle_request():
    """
    This endpoint receives the request from watsonx.orchestrate,
    passes it to your main function logic, and returns the result.
    """
    print("Received a request...")
    try:
        # Get the JSON payload from the incoming request
        params = request.get_json()
        if not params:
            return jsonify({"error": "Request body must be JSON"}), 400

        # Call your core function logic
        result = execute_sql_tool(params)
        
        # The result from your function is already a complete HTTP response
        # We just need to extract the parts for Flask
        response_body = json.loads(result.get("body", "{}"))
        status_code = result.get("statusCode", 500)
        headers = result.get("headers", {})

        return jsonify(response_body), status_code, headers

    except Exception as e:
        print(f"An error occurred in the server: {e}")
        return jsonify({"error": "An internal server error occurred"}), 500

if __name__ == '__main__':
    # Runs the Flask app on localhost, port 8080
    app.run(host='0.0.0.0', port=8080)
