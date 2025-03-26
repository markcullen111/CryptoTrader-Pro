#!/usr/bin/env python3
import os
import sys
import sqlite3
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import yaml
from pathlib import Path

def load_config():
    """Load configuration from config.yaml."""
    config_path = Path("config/config.yaml")
    if not config_path.exists():
        print("Error: config.yaml not found. Please run setup script first.")
        sys.exit(1)
    
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def setup_sqlite():
    """Setup SQLite database."""
    print("Setting up SQLite database...")
    db_path = Path("data/cryptotrader.db")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            side TEXT NOT NULL,
            amount REAL NOT NULL,
            price REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS market_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            open REAL NOT NULL,
            high REAL NOT NULL,
            low REAL NOT NULL,
            close REAL NOT NULL,
            volume REAL NOT NULL,
            UNIQUE(symbol, timestamp)
        );
        
        CREATE TABLE IF NOT EXISTS strategies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            parameters TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS experiments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            parameters TEXT NOT NULL,
            results TEXT,
            status TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    conn.commit()
    conn.close()
    print("SQLite database setup complete!")

def setup_postgresql(config):
    """Setup PostgreSQL database."""
    print("Setting up PostgreSQL database...")
    db_config = config['database']
    
    try:
        # Connect to default postgres database
        conn = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password'],
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Create database if it doesn't exist
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_config['name']}'")
        if not cursor.fetchone():
            cursor.execute(f"CREATE DATABASE {db_config['name']}")
        
        # Close connection to postgres database
        cursor.close()
        conn.close()
        
        # Connect to the new database
        conn = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['name']
        )
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id SERIAL PRIMARY KEY,
                symbol VARCHAR(20) NOT NULL,
                side VARCHAR(4) NOT NULL,
                amount DECIMAL(20,8) NOT NULL,
                price DECIMAL(20,8) NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS market_data (
                id SERIAL PRIMARY KEY,
                symbol VARCHAR(20) NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                open DECIMAL(20,8) NOT NULL,
                high DECIMAL(20,8) NOT NULL,
                low DECIMAL(20,8) NOT NULL,
                close DECIMAL(20,8) NOT NULL,
                volume DECIMAL(30,8) NOT NULL,
                UNIQUE(symbol, timestamp)
            );
            
            CREATE TABLE IF NOT EXISTS strategies (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                parameters JSONB NOT NULL,
                status VARCHAR(20) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS experiments (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                parameters JSONB NOT NULL,
                results JSONB,
                status VARCHAR(20) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        conn.commit()
        print("PostgreSQL database setup complete!")
        
    except Exception as e:
        print(f"Error setting up PostgreSQL database: {str(e)}")
        sys.exit(1)
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def setup_api():
    """Setup API configuration."""
    print("Setting up API configuration...")
    
    # Check if .env file exists
    env_path = Path(".env")
    if not env_path.exists():
        print("Error: .env file not found. Please run setup script first.")
        sys.exit(1)
    
    # Read current .env file
    with open(env_path, 'r') as f:
        env_lines = f.readlines()
    
    # Check if API keys are set
    api_key_set = any(line.startswith("EXCHANGE_API_KEY=") and not line.startswith("EXCHANGE_API_KEY=your_") for line in env_lines)
    api_secret_set = any(line.startswith("EXCHANGE_API_SECRET=") and not line.startswith("EXCHANGE_API_SECRET=your_") for line in env_lines)
    
    if not api_key_set or not api_secret_set:
        print("\nPlease set your Binance API keys in the .env file:")
        print("EXCHANGE_API_KEY=your_api_key_here")
        print("EXCHANGE_API_SECRET=your_api_secret_here")
        print("\nYou can get your API keys from:")
        print("1. Log into your Binance account")
        print("2. Go to API Management in your account settings")
        print("3. Create a new API key with the following permissions:")
        print("   - Enable Reading")
        print("   - Enable Spot & Margin Trading")
        print("   - Disable Withdrawals")
        sys.exit(1)
    
    print("API configuration verified!")

def main():
    """Main setup function."""
    print("Starting database and API setup...")
    
    # Load configuration
    config = load_config()
    
    # Setup database based on configuration
    if config['database']['type'] == 'sqlite':
        setup_sqlite()
    elif config['database']['type'] == 'postgresql':
        setup_postgresql(config)
    else:
        print(f"Unsupported database type: {config['database']['type']}")
        sys.exit(1)
    
    # Setup API configuration
    setup_api()
    
    print("\nSetup completed successfully!")
    print("You can now start the application using:")
    if sys.platform == 'win32':
        print("run.bat")
    else:
        print("./run.sh")

if __name__ == "__main__":
    main() 