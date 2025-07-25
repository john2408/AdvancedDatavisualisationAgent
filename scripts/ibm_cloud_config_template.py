# IBM Cloud PostgreSQL Configuration Template
# Copy this file to 'ibm_cloud_config.py' and update with your actual credentials

"""
IBM Cloud PostgreSQL Configuration Template

Instructions:
1. Copy this file to 'ibm_cloud_config.py'
2. Update the values below with your IBM Cloud PostgreSQL service credentials
3. Import this configuration in the create_postgresql_database.py script

To use this configuration, modify the import in create_postgresql_database.py:
    from ibm_cloud_config import IBM_CLOUD_CONFIG as DATABASE_CONFIG
"""

# IBM Cloud PostgreSQL Service Credentials
# Get these values from your IBM Cloud PostgreSQL service credentials
IBM_CLOUD_CONFIG = {
    # Connection Details
    'host': 'your-instance-id.databases.appdomain.cloud',    # Replace with your hostname
    'port': 30123,                                           # Replace with your port (usually 30XXX)
    'database': 'ibmclouddb',                               # Usually 'ibmclouddb' for IBM Cloud
    'user': 'ibm_cloud_user',                              # Replace with your username
    'password': 'your_actual_password_here',                # Replace with your password
    
    # SSL Configuration (Required for IBM Cloud)
    'sslmode': 'require',                                   # Required for IBM Cloud
    'connect_timeout': 30,                                  # Connection timeout in seconds
    
    # Optional SSL Certificates (uncomment if required)
    # 'sslcert': 'path/to/client-cert.pem',                # Client certificate
    # 'sslkey': 'path/to/client-key.pem',                  # Client private key  
    # 'sslrootcert': 'path/to/ca-cert.pem',               # Root CA certificate
}

# Example of a complete IBM Cloud configuration:
EXAMPLE_IBM_CLOUD_CONFIG = {
    'host': 'abc123def-456g-789h-ijkl-123456789abc.databases.appdomain.cloud',
    'port': 30123,
    'database': 'ibmclouddb',
    'user': 'ibm_cloud_abc123def456',
    'password': 'your_32_character_password_here',
    'sslmode': 'require',
    'connect_timeout': 30,
}

# Alternative configuration using environment variables (recommended for production)
import os

ENV_CONFIG = {
    'host': os.getenv('IBM_POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('IBM_POSTGRES_PORT', 5432)),
    'database': os.getenv('IBM_POSTGRES_DATABASE', 'ibmclouddb'),
    'user': os.getenv('IBM_POSTGRES_USER', 'postgres'),
    'password': os.getenv('IBM_POSTGRES_PASSWORD', 'password'),
    'sslmode': os.getenv('IBM_POSTGRES_SSLMODE', 'require'),
    'connect_timeout': int(os.getenv('IBM_POSTGRES_TIMEOUT', 30)),
}

# Usage instructions:
"""
To use this configuration:

1. For direct configuration:
   - Update IBM_CLOUD_CONFIG with your actual credentials
   - In create_postgresql_database.py, change:
     DATABASE_CONFIG = IBM_CLOUD_CONFIG

2. For environment variables (recommended):
   - Set environment variables:
     export IBM_POSTGRES_HOST="your-host.databases.appdomain.cloud"
     export IBM_POSTGRES_PORT="30123"
     export IBM_POSTGRES_DATABASE="ibmclouddb"
     export IBM_POSTGRES_USER="your_username"
     export IBM_POSTGRES_PASSWORD="your_password"
   - In create_postgresql_database.py, change:
     DATABASE_CONFIG = ENV_CONFIG

3. For testing locally:
   - Keep the default DATABASE_CONFIG for local PostgreSQL
"""
