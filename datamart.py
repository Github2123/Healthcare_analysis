import pymysql

# Database connection details
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "healthcare",
}

# Data mart creation queries
DATA_MART_QUERIES = {
    "patient_data_mart": """
        CREATE TABLE IF NOT EXISTS patient_data_mart AS
        SELECT 
            p.patient_id,
            p.name,
            p.age,
            p.gender,
            p.location,
            p.blood_type,
            p.weight,
            p.height,
            p.smoker_status,
            p.alcohol_consumption,
            p.exercise_frequency,
            COUNT(hf.visit_id) AS total_visits,
            SUM(hf.total_bill) AS total_spent
        FROM patient_dim p
        LEFT JOIN hospital_visits_fact hf ON p.patient_id = hf.patient_id
        GROUP BY p.patient_id;
    """,

    "disease_data_mart": """
        CREATE TABLE IF NOT EXISTS disease_data_mart AS
        SELECT 
            d.disease_id,
            d.disease_name,
            d.category,
            d.severity_level,
            COUNT(hf.visit_id) AS total_cases,
            SUM(hf.total_bill) AS total_revenue
        FROM disease_dim d
        LEFT JOIN hospital_visits_fact hf ON d.disease_id = hf.disease_id
        GROUP BY d.disease_id;
    """,

    "doctor_data_mart": """
        CREATE TABLE IF NOT EXISTS doctor_data_mart AS
        SELECT 
            doc.doctor_id,
            doc.doctor_name,
            doc.specialization,
            doc.years_of_experience,
            COUNT(hf.visit_id) AS total_patients_seen,
            SUM(hf.total_bill) AS total_revenue_generated
        FROM doctor_dim doc
        LEFT JOIN hospital_visits_fact hf ON doc.doctor_id = hf.doctor_id
        GROUP BY doc.doctor_id;
    """,

    "hospital_data_mart": """
        CREATE TABLE IF NOT EXISTS hospital_data_mart AS
        SELECT 
            h.hospital_id,
            h.hospital_name,
            h.city,
            h.type,
            COUNT(hf.visit_id) AS total_visits,
            SUM(hf.total_bill) AS total_revenue
        FROM hospital_dim h
        LEFT JOIN hospital_visits_fact hf ON h.hospital_id = hf.hospital_id
        GROUP BY h.hospital_id;
    """,

    "billing_data_mart": """
        CREATE TABLE IF NOT EXISTS billing_data_mart AS
        SELECT 
            b.billing_id,
            b.insurance_type,
            b.claim_status,
            b.payment_method,
            COUNT(hf.visit_id) AS total_transactions,
            SUM(hf.total_bill) AS total_billed
        FROM billing_dim b
        LEFT JOIN hospital_visits_fact hf ON b.billing_id = hf.billing_id
        GROUP BY b.billing_id;
    """
}


def create_data_marts():
    """Connects to MySQL and executes queries to create data marts."""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        for mart_name, query in DATA_MART_QUERIES.items():
            print(f"📌 Creating {mart_name}...")
            cursor.execute(query)
            print(f"✅ {mart_name} created successfully!")

        conn.commit()
        print("\n🎉 All data marts have been successfully created!")

    except pymysql.MySQLError as e:
        print(f"❌ Database Error: {e}")

    finally:
        cursor.close()
        conn.close()


# Run script
if __name__ == "__main__":
    create_data_marts()
