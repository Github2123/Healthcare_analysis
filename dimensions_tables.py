import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

Host=os.getenv('host')
User=os.getenv('user')
Password=os.getenv('password')
Database=os.getenv('database')

DB_CONFIG = {
        "host": Host,       
        "user":User,            
        "password":Password,     
        "database":Database  
}



# Tables and their respective ID columns
TABLES = {
    "patient_dim": "patient_id",
    "disease_dim": "disease_id",
    "doctor_dim": "doctor_id",
    "hospital_dim": "hospital_id",
    "billing_dim": "billing_id",
    
}

# Connect to MySQL and execute queries
def modify_and_set_primary_keys():
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        for table, column in TABLES.items():
            print(f"Processing table: {table}...")

            # Step 1: Modify column type
            modify_query = f"ALTER TABLE {table} MODIFY {column} VARCHAR(255) NOT NULL;"
            cursor.execute(modify_query)
            print(f" Modified {column} in {table} to VARCHAR(255).")

            # Step 2: Add Primary Key
            try:
                primary_key_query = f"ALTER TABLE {table} ADD PRIMARY KEY ({column});"
                cursor.execute(primary_key_query)
                print(f" Added PRIMARY KEY on {column} in {table}.")
            except pymysql.err.OperationalError as e:
                print(f"Error adding PRIMARY KEY to {table}: {e}")

        conn.commit()
        print(" All tables processed successfully!")
    
    except pymysql.MySQLError as e:
        print(f" Database Error: {e}")
    
    finally:
        cursor.close()
        conn.close()

# Run the function
if __name__ == "__main__":
    modify_and_set_primary_keys()