import pandas as pd
from sqlalchemy import create_engine, text

# MySQL Database Connection Details
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "Healthcare",
}

# Create SQLAlchemy engine using DB_CONFIG
engine = create_engine(f"mysql+mysqlconnector://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}")

# Load CSV file for the fact table
hospital_visits_fact = pd.read_csv("cleaned_hospital_visits_fact.csv")


# Function to create the fact table if it doesn't exist
def create_fact_table():
    create_table_query = """
    CREATE TABLE hospital_visits_fact (
        visit_id VARCHAR(50) PRIMARY KEY,
        patient_id VARCHAR(255),
        disease_id VARCHAR(255),
        billing_id VARCHAR(255),
        visit_date DATE,
        hospital_id VARCHAR(255),
        doctor_id VARCHAR(255),
        total_bill DECIMAL(10, 2),
        FOREIGN KEY (patient_id) REFERENCES patient_dim(patient_id),
        FOREIGN KEY (disease_id) REFERENCES disease_dim(disease_id),
        FOREIGN KEY (billing_id) REFERENCES billing_dim(billing_id),
        FOREIGN KEY (hospital_id) REFERENCES hospital_dim(hospital_id),
        FOREIGN KEY (doctor_id) REFERENCES doctor_dim(doctor_id)
    );
    """
    with engine.connect() as connection:
        connection.execute(text(create_table_query))
        print("✅ Fact table `hospital_visits_fact` created (if not already existing).")


# Function to push DataFrame to MySQL with foreign key validation
def push_to_mysql(df, table_name):
    try:
        # Validate foreign keys before inserting data
        with engine.connect() as connection:
            # Use 'text' function to execute raw SQL queries properly
            valid_patient_ids = {row[0] for row in connection.execute(text("SELECT patient_id FROM patient_dim")).fetchall()}
            valid_disease_ids = {row[0] for row in connection.execute(text("SELECT disease_id FROM disease_dim")).fetchall()}
            valid_billing_ids = {row[0] for row in connection.execute(text("SELECT billing_id FROM billing_dim")).fetchall()}
            valid_hospital_ids = {row[0] for row in connection.execute(text("SELECT hospital_id FROM hospital_dim")).fetchall()}
            valid_doctor_ids = {row[0] for row in connection.execute(text("SELECT doctor_id FROM doctor_dim")).fetchall()}

            # Filter invalid rows
            valid_data = df[
                df['patient_id'].isin(valid_patient_ids) &
                df['disease_id'].isin(valid_disease_ids) &
                df['billing_id'].isin(valid_billing_ids) &
                df['hospital_id'].isin(valid_hospital_ids) &
                df['doctor_id'].isin(valid_doctor_ids)
            ]
            
            if valid_data.empty:
                raise ValueError("No valid rows to insert after foreign key validation.")

            # Insert valid data into MySQL table
            valid_data.to_sql(table_name, engine, if_exists="append", index=False)
            print(f"✅ Data pushed to {table_name}")
    except Exception as e:
        print(f"❌ Error inserting data into table: {e}")


# Main function to execute
if __name__ == "__main__":
    # Create the fact table if it doesn't exist
    create_fact_table()
    
    # Push data into the fact table
    push_to_mysql(hospital_visits_fact, "hospital_visits_fact")
    
    print("🎉 Fact table successfully loaded into MySQL!")