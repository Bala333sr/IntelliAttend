#!/usr/bin/env python3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Print all environment variables related to MySQL
print("Environment variables:")
for key, value in os.environ.items():
    if 'MYSQL' in key.upper() or 'SQL' in key.upper():
        print(f"  {key}: {value}")

# Database configuration from config.py
MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or ''
MYSQL_DB = os.environ.get('MYSQL_DB') or 'IntelliAttend_DataBase'
MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))

print("\nConfig values:")
print(f"  MYSQL_HOST: {MYSQL_HOST}")
print(f"  MYSQL_USER: {MYSQL_USER}")
print(f"  MYSQL_PASSWORD: {MYSQL_PASSWORD}")
print(f"  MYSQL_DB: {MYSQL_DB}")
print(f"  MYSQL_PORT: {MYSQL_PORT}")

SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
print(f"\nGenerated URI: {SQLALCHEMY_DATABASE_URI}")