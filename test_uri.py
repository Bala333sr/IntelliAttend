#!/usr/bin/env python3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration  
MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or ''
MYSQL_DB = os.environ.get('MYSQL_DB') or 'IntelliAttend_DataBase'
MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))

SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"

print("Generated SQLALCHEMY_DATABASE_URI:")
print(SQLALCHEMY_DATABASE_URI)