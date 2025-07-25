# PostgreSQL Database Setup Guide

## Overview

This guide explains how to use the `create_postgresql_database.py` script to load the Vehicle Market Share star schema data into a PostgreSQL database, including configuration for IBM Cloud PostgreSQL services.

## Prerequisites

### 1. Install Required Python Packages

```bash
pip install psycopg2-binary pandas pyarrow
```

### 2. Prepare Your Data

Ensure you have already created the star schema parquet files by running:

```bash
python scripts/create_star_schema.py
```

This will create the required parquet files in the `data/star_schema/` directory.

## Configuration

### Local PostgreSQL Setup

For a local PostgreSQL installation, update the `DATABASE_CONFIG` dictionary in the script:

```python
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'market_share',
    'user': 'your_username',
    'password': 'your_password',
    'sslmode': 'prefer',
    'connect_timeout': 30,
}
```

### IBM Cloud PostgreSQL Configuration

For IBM Cloud PostgreSQL, you'll need to update the configuration with your service credentials:

#### Step 1: Get Your IBM Cloud PostgreSQL Credentials

1. Go to your IBM Cloud dashboard
2. Navigate to your PostgreSQL service instance
3. Click on "Service Credentials" in the left sidebar
4. Copy the connection details from your service credentials

#### Step 2: Update the Database Configuration

Replace the `DATABASE_CONFIG` dictionary with your IBM Cloud credentials:

```python
DATABASE_CONFIG = {
    'host': 'your-instance.databases.appdomain.cloud',  # hostname from credentials
    'port': 30XXX,                                      # port from credentials (usually 30XXX)
    'database': 'ibmclouddb',                          # database name from credentials
    'user': 'ibm_cloud_user',                         # username from credentials
    'password': 'your_password',                       # password from credentials
    'sslmode': 'require',                              # Required for IBM Cloud
    'connect_timeout': 30,
}
```

#### Step 3: Optional SSL Certificate Configuration

If your IBM Cloud PostgreSQL requires SSL certificates, download them and add:

```python
DATABASE_CONFIG = {
    # ... other config ...
    'sslcert': 'path/to/your-cert.pem',      # Client certificate
    'sslkey': 'path/to/your-key.pem',       # Client private key
    'sslrootcert': 'path/to/ca-cert.pem',   # Root certificate
}
```

## Key Variables to Adjust for IBM Cloud

### Required Changes:

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `host` | IBM Cloud PostgreSQL hostname | `your-instance.databases.appdomain.cloud` |
| `port` | IBM Cloud PostgreSQL port | `30123` (varies by instance) |
| `database` | Database name | `ibmclouddb` (default for IBM Cloud) |
| `user` | Database username | `ibm_cloud_user` (from credentials) |
| `password` | Database password | Your actual password from credentials |
| `sslmode` | SSL mode | `require` (mandatory for IBM Cloud) |

### Optional SSL Configuration:

| Variable | Description | When to Use |
|----------|-------------|-------------|
| `sslcert` | Client certificate path | If client certificates are required |
| `sslkey` | Client private key path | If client certificates are required |
| `sslrootcert` | Root CA certificate path | For additional security validation |

## Usage

### 1. Basic Execution

```bash
python scripts/create_postgresql_database.py
```

### 2. Database Features

The script will create:

- **7 Tables**: 5 dimension tables + 2 fact tables
- **Foreign Key Constraints**: Ensuring referential integrity
- **Performance Indexes**: Optimized for analytical queries
- **Data Validation**: Comprehensive integrity checks

### 3. Expected Output

```
2025-07-25 12:45:48,728 - INFO - Connected to PostgreSQL database: your-host:30123
2025-07-25 12:45:48,730 - INFO - Creating database tables...
2025-07-25 12:45:48,730 - INFO - All tables created successfully.
2025-07-25 12:45:48,730 - INFO - Loading dimension tables...
2025-07-25 12:45:48,756 - INFO - Loaded 12 records into DimTime
...
======================================================================
VEHICLE MARKET SHARE POSTGRESQL DATABASE CREATION SUMMARY
======================================================================
```

## Key Differences from SQLite

### Advantages of PostgreSQL:

1. **Proper Data Types**: Uses `DECIMAL` for precise financial calculations
2. **Foreign Key Constraints**: Enforced at database level
3. **COPY Performance**: Faster bulk data loading using PostgreSQL's COPY command
4. **Enterprise Features**: Better for production environments
5. **Concurrent Access**: Multi-user support out of the box

### Schema Improvements:

- **Decimal Precision**: Market share values use `DECIMAL(10,8)` for accuracy
- **VARCHAR Limits**: Proper column size constraints
- **BIGINT**: For large vehicle count values
- **CASCADE Operations**: Proper foreign key cascade behavior

## Troubleshooting

### Common Issues:

1. **Connection Timeout**
   ```
   psycopg2.OperationalError: timeout expired
   ```
   - Increase `connect_timeout` value
   - Check firewall settings
   - Verify IBM Cloud service is running

2. **SSL Certificate Issues**
   ```
   psycopg2.OperationalError: SSL connection failed
   ```
   - Ensure `sslmode` is set to `require` for IBM Cloud
   - Download and configure SSL certificates if required

3. **Permission Errors**
   ```
   psycopg2.ProgrammingError: permission denied
   ```
   - Verify user has CREATE TABLE permissions
   - Check database name is correct
   - Ensure user can connect to the specified database

### Debug Mode

To enable more detailed logging, modify the logging level:

```python
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
```

## Performance Considerations

### For Large Datasets:

1. **Increase Batch Size**: The script uses COPY for optimal performance
2. **Monitor Memory**: Large parquet files may require sufficient RAM
3. **Connection Pooling**: For production use, consider connection pooling
4. **Index Creation**: Indexes are created after data loading for better performance

### IBM Cloud Specific:

1. **Network Latency**: IBM Cloud connections may have higher latency
2. **Resource Limits**: Check your service plan limits
3. **Backup Strategy**: Consider IBM Cloud backup options

## Production Deployment

### Environment Variables

For production, use environment variables instead of hardcoded credentials:

```python
import os

DATABASE_CONFIG = {
    'host': os.getenv('POSTGRES_HOST'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
    'database': os.getenv('POSTGRES_DATABASE'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'sslmode': os.getenv('POSTGRES_SSLMODE', 'require'),
}
```

### Security Best Practices

1. **Never commit credentials** to version control
2. **Use environment variables** or secure credential stores
3. **Enable SSL/TLS** for all connections
4. **Regular credential rotation** for IBM Cloud services
5. **Monitor database access** logs

## Next Steps

After successful database creation:

1. **Connect your BI tools** (Tableau, Power BI, etc.)
2. **Set up analytics dashboards**
3. **Create additional indexes** based on query patterns
4. **Implement data refresh procedures** for ongoing updates
5. **Set up monitoring and alerting** for the database
