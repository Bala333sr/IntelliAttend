#!/usr/bin/env python3
import pymysql
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration  
DB_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'user': os.environ.get('MYSQL_USER', 'root'),
    'password': os.environ.get('MYSQL_PASSWORD', ''),
    'database': os.environ.get('MYSQL_DB', 'IntelliAttend_DataBase'),
    'charset': 'utf8mb4',
    'port': int(os.environ.get('MYSQL_PORT', 3306))
}

print("Database configuration:")
for key, value in DB_CONFIG.items():
    print(f"  {key}: {value}")

try:
    # Connect and test
    connection = pymysql.connect(**DB_CONFIG)
    print("✅ MySQL connection successful!")
    cursor = connection.cursor()
    cursor.execute("SELECT VERSION()")
    version = cursor.fetchone()
    if version:
        print(f"MySQL version: {version[0]}")
    else:
        print("MySQL version: Unknown")
    cursor.close()
    connection.close()
except Exception as e:
    print(f"❌ MySQL connection failed: {e}")