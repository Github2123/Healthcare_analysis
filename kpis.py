import pymysql
import pandas as pd

# Database connection details
import mysql.connector

# Function to connect to the MySQL database
def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",        # Corrected 'DB_HOST'
        user="root",             # Corrected 'DB_USER'
        password="root",      # Corrected 'DB_PASSWORD'
        database="healthcare"        # Corrected 'DB_NAME'
    )
    return connection


# 1. Total Revenue (Billing) Analysis
def get_total_revenue():
    query = "SELECT SUM(total_bill) AS total_revenue FROM hospital_visits_fact"
    connection = get_db_connection()
    df = pd.read_sql(query, connection)
    connection.close()
    return df['total_revenue'][0]


# 2. Revenue by Disease (Join with disease_dim)
def get_revenue_by_disease():
    query = """
    SELECT d.disease_name, SUM(v.total_bill) AS total_revenue
    FROM hospital_visits_fact v
    JOIN disease_dim d ON v.disease_id = d.disease_id
    GROUP BY d.disease_name;
    """
    connection = get_db_connection()
    df = pd.read_sql(query, connection)
    connection.close()
    return df


# 3. Revenue by Doctor (Join with doctor_dim)
def get_revenue_by_doctor():
    query = """
    SELECT d.doctor_name, SUM(v.total_bill) AS total_revenue
    FROM hospital_visits_fact v
    JOIN doctor_dim d ON v.doctor_id = d.doctor_id
    GROUP BY d.doctor_name limit 10;
    """
    connection = get_db_connection()
    df = pd.read_sql(query, connection)
    connection.close()
    return df


# 4. Revenue by Hospital (Join with hospital_dim)
def get_revenue_by_hospital():
    query = """
    SELECT h.hospital_name, SUM(v.total_bill) AS total_revenue
    FROM hospital_visits_fact v
    JOIN hospital_dim h ON v.hospital_id = h.hospital_id
    GROUP BY h.hospital_name;
    """
    connection = get_db_connection()
    df = pd.read_sql(query, connection)
    connection.close()
    return df


# 5. Number of Visits (Volume) Analysis
def get_total_visits():
    query = "SELECT COUNT(DISTINCT visit_id) AS total_visits FROM hospital_visits_fact"
    connection = get_db_connection()
    df = pd.read_sql(query, connection)
    connection.close()
    return df['total_visits'][0]


# 6. Average Revenue per Visit
def get_avg_revenue_per_visit():
    query = "SELECT AVG(total_bill) AS avg_revenue_per_visit FROM hospital_visits_fact"
    connection = get_db_connection()
    df = pd.read_sql(query, connection)
    connection.close()
    return df['avg_revenue_per_visit'][0]


# 7. Revenue per Patient (Join with patient_dim)
def get_revenue_per_patient():
    query = """
    SELECT p.name, SUM(v.total_bill) AS revenue_per_patient
    FROM hospital_visits_fact v
    JOIN patient_dim p ON v.patient_id = p.patient_id
    GROUP BY p.name;
    """
    connection = get_db_connection()
    df = pd.read_sql(query, connection)
    connection.close()
    return df


# 8. Patient Visits by Gender (Join with patient_dim)
def get_visits_by_gender():
    query = """
    SELECT p.gender, COUNT(DISTINCT v.visit_id) AS total_visits
    FROM hospital_visits_fact v
    JOIN patient_dim p ON v.patient_id = p.patient_id
    GROUP BY p.gender;
    """
    connection = get_db_connection()
    df = pd.read_sql(query, connection)
    connection.close()
    return df


# 9. Patient Visits by Age Group (Join with patient_dim)
def get_visits_by_age_group():
    query = """
    SELECT
        CASE
            WHEN p.age BETWEEN 0 AND 18 THEN '0-18'
            WHEN p.age BETWEEN 19 AND 35 THEN '19-35'
            WHEN p.age BETWEEN 36 AND 60 THEN '36-60'
            ELSE '60+'
        END AS age_group,
        COUNT(DISTINCT v.visit_id) AS total_visits
    FROM hospital_visits_fact v
    JOIN patient_dim p ON v.patient_id = p.patient_id
    GROUP BY age_group;
    """
    connection = get_db_connection()
    df = pd.read_sql(query, connection)
    connection.close()
    return df


# 10. Claim Status Breakdown (Join with billing_dim)
def get_claim_status_breakdown():
    query = """
    SELECT b.claim_status, COUNT(b.billing_id) AS total_claims
    FROM billing_dim b
    GROUP BY b.claim_status;
    """
    connection = get_db_connection()
    df = pd.read_sql(query, connection)
    connection.close()
    return df


# 11. Revenue by Insurance Type (Join with billing_dim)
def get_revenue_by_insurance_type():
    query = """
    SELECT b.insurance_type, SUM(v.total_bill) AS total_revenue
    FROM hospital_visits_fact v
    JOIN billing_dim b ON v.billing_id = b.billing_id
    GROUP BY b.insurance_type;
    """
    connection = get_db_connection()
    df = pd.read_sql(query, connection)
    connection.close()
    return df


# 12. Hospital Visits Trend Over Time
def get_hospital_visits_trend():
    query = """
    SELECT DATE_FORMAT(v.visit_date, '%Y-%m') AS month, COUNT(DISTINCT v.visit_id) AS total_visits
    FROM hospital_visits_fact v
    GROUP BY month
    ORDER BY month;
    """
    connection = get_db_connection()
    df = pd.read_sql(query, connection)
    connection.close()
    return df


# Example of calling the functions
if __name__ == "__main__":
    print("Total Revenue: ", get_total_revenue())
    print("Revenue by Disease: \n", get_revenue_by_disease())
    print("Revenue by Doctor: \n", get_revenue_by_doctor())
    print("Revenue by Hospital: \n", get_revenue_by_hospital())
    print("Total Visits: ", get_total_visits())
    print("Average Revenue per Visit: ", get_avg_revenue_per_visit())
    print("Revenue per Patient: \n", get_revenue_per_patient())
    print("Visits by Gender: \n", get_visits_by_gender())
    print("Visits by Age Group: \n", get_visits_by_age_group())
    print("Claim Status Breakdown: \n", get_claim_status_breakdown())
    print("Revenue by Insurance Type: \n", get_revenue_by_insurance_type())
    print("Hospital Visits Trend: \n", get_hospital_visits_trend())