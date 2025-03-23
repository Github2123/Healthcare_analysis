import pymysql
import pandas as pd

# --- Database Connection ---
def connect_db():
    return pymysql.connect(
        host="localhost",  # e.g., "localhost"
        user="root",  # e.g., "root"
        password="root",
        database="healthcare",
        cursorclass=pymysql.cursors.DictCursor  # Returns results as dictionaries
    )

# --- SQL Aggregation Queries ---
QUERIES = {
    "patient_statistics": """
        SELECT 
            COUNT(DISTINCT patient_id) AS total_patients,
            AVG(age) AS average_age,
            COUNT(visit_id) AS total_visits
        FROM hospital_visits_fact 
        JOIN patient_dim USING (patient_id);
    """,

    "financial_metrics": """
        SELECT 
            AVG(total_bill) AS average_bill_per_visit,
            SUM(total_bill) AS total_revenue
        FROM hospital_visits_fact;
    """,

    "hospital_revenue": """
        SELECT 
            h.hospital_name, 
            SUM(f.total_bill) AS revenue
        FROM hospital_visits_fact f
        JOIN hospital_dim h USING (hospital_id)
        GROUP BY h.hospital_name;
    """,

    "patients_per_doctor": """
        SELECT 
            d.doctor_name, 
            COUNT(DISTINCT f.patient_id) AS patient_count
        FROM hospital_visits_fact f
        JOIN doctor_dim d USING (doctor_id)
        GROUP BY d.doctor_name;
    """,

    "disease_category_counts": """
        SELECT 
            d.category, 
            COUNT(f.disease_id) AS disease_count
        FROM hospital_visits_fact f
        JOIN disease_dim d USING (disease_id)
        GROUP BY d.category;
    """
}

# --- Function to Execute SQL Queries ---
def run_query(query):
    conn = connect_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
        return result
    finally:
        conn.close()

# --- Main Execution ---
if __name__ == "__main__":
    patient_stats = run_query(QUERIES["patient_statistics"])
    financial_metrics = run_query(QUERIES["financial_metrics"])
    hospital_revenue = run_query(QUERIES["hospital_revenue"])
    patients_per_doctor = run_query(QUERIES["patients_per_doctor"])
    disease_counts = run_query(QUERIES["disease_category_counts"])

    # Display Results
    print("\n📊 Patient Statistics:", patient_stats)
    print("\n💰 Financial Metrics:", financial_metrics)
    print("\n🏥 Revenue Per Hospital:", hospital_revenue)
    print("\n👨‍⚕️ Patients Per Doctor:", patients_per_doctor)
    print("\n🦠 Disease Category Counts:", disease_counts)

    print("\n✅ Aggregations Completed from MySQL!")