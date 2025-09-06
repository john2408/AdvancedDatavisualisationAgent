import os
import logging
import requests
import json
import base64
from omegaconf import OmegaConf
from typing import Optional, Dict, List, Any

# Setup logging
logger = logging.getLogger(__name__)

# Load configuration
config = OmegaConf.load("config.yaml")
IBM_ORCHESTRATE_URL = config.ibm_orchestrate_url
IBM_ORCHESTRATE_KEY = os.environ.get("IBM_ORCHESTRATE_KEY")

# Replace with your actual values
API_KEY = IBM_ORCHESTRATE_KEY
AUTH_URL = "https://iam.cloud.ibm.com/identity/token"

# Extract the real tenant ID from the config URL
if '/instances/' in IBM_ORCHESTRATE_URL:
    tenant_id = IBM_ORCHESTRATE_URL.split('/instances/')[-1].strip('/')
    print(f"🔍 Extracted tenant ID: {tenant_id}")
else:
    tenant_id = "70549626-895e-4bf8-a49d-8415fd802d55"  # fallback
    print(f"⚠️  Using fallback tenant ID: {tenant_id}")

BASE_URL = f"https://api.us-south.watson-orchestrate.cloud.ibm.com/instances/{tenant_id}"

print(f"🌐 Base URL: {BASE_URL}")
print(f"🔑 API Key available: {'Yes' if API_KEY else 'No'}")
print(f"🔑 API Key length: {len(API_KEY) if API_KEY else 0}")
print("="*50)

# Step 1: Get IAM access token
print("🔐 Step 1: Getting IAM access token...")
try:
    auth_response = requests.post(
        AUTH_URL,
        data={"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": API_KEY},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    auth_response.raise_for_status()
    iam_token = auth_response.json()["access_token"]
    print(f"✅ IAM token obtained (length: {len(iam_token)})")
    print(f"🔍 Token starts with: {iam_token[:20]}...")
except Exception as e:
    print(f"❌ Error getting IAM token: {e}")
    print(f"   Response status: {auth_response.status_code if 'auth_response' in locals() else 'No response'}")
    if 'auth_response' in locals():
        print(f"   Response text: {auth_response.text}")
    exit(1)

# Step 2: Call the Watson Orchestrate API to list agents
print("🤖 Step 2: Calling Watson Orchestrate API...")
endpoint_url = f"{BASE_URL}/v1/orchestrate/agents"
print(f"🌐 Full endpoint: {endpoint_url}")

headers = {"Authorization": f"Bearer {iam_token}", "Accept": "application/json"}
print(f"📋 Headers: Authorization=Bearer {iam_token[:20]}..., Accept=application/json")

# First, let's test a simple endpoint to see if the instance is responsive
print("🔍 Testing instance health...")
try:
    health_response = requests.get(f"{BASE_URL}/", headers=headers, timeout=10)
    print(f"   Instance root status: {health_response.status_code}")
except:
    print("   Instance root test failed")

try:
    response = requests.get(endpoint_url, headers=headers, timeout=30)
    print(f"📊 Response status: {response.status_code}")
    print(f"📋 Response headers: {dict(response.headers)}")
except Exception as e:
    print(f"❌ Error making request: {e}")
    exit(1)

# Step 3: Print results
print("📊 Step 3: Processing results...")
if response.status_code == 200:
    print("✅ Success! Processing agent data...")
    try:
        agents_data = response.json()
        print(f"🔍 Response keys: {list(agents_data.keys()) if isinstance(agents_data, dict) else 'Not a dict'}")
        
        agents = agents_data.get("agents", [])
        print(f"🤖 Found {len(agents)} agents:")
        
        if agents:
            for i, agent in enumerate(agents, 1):
                print(f"{i}. ID: {agent.get('id', 'N/A')}, Name: {agent.get('name', 'N/A')}")
                if agent.get('description'):
                    print(f"   Description: {agent['description']}")
        else:
            print("   No agents found in the response")
            
    except json.JSONDecodeError:
        print(f"❌ Response is not valid JSON")
        print(f"   Content-Type: {response.headers.get('content-type', 'Unknown')}")
        print(f"   Response text (first 200 chars): {response.text[:200]}...")
        
elif response.status_code == 401:
    print("❌ Authentication failed (401)")
    print(f"   Response: {response.text}")
    print("   💡 This might mean:")
    print("      - IAM token is invalid or expired")
    print("      - Wrong authentication method")
    print("      - Need a different type of token")
elif response.status_code == 403:
    print("❌ Permission denied (403)")
    print(f"   Response: {response.text}")
    print("   💡 You might not have access to list agents")
elif response.status_code == 404:
    print("❌ Endpoint not found (404)")
    print(f"   Response: {response.text}")
    print("   💡 The URL might be incorrect")
elif response.status_code == 500:
    print("❌ Server error (500)")
    print(f"   Response: {response.text}")
    print("   💡 This might be a temporary server issue")
else:
    print(f"❌ Unexpected status code: {response.status_code}")
    print(f"   Response: {response.text}")
    print(f"   Content-Type: {response.headers.get('content-type', 'Unknown')}")