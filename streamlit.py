import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pymysql
import pandas as pd

# --- Database Connection ---
def connect_db():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="root",
        database="healthcare",
        cursorclass=pymysql.cursors.DictCursor
    )

# Function to execute SQL query
def run_query(query):
    conn = connect_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query)
            result = pd.DataFrame(cursor.fetchall())
        return result
    finally:
        conn.close()


# --- KPI Functions ---
def get_total_revenue():
    query = "SELECT SUM(total_bill) AS total_revenue FROM hospital_visits_fact"
    return run_query(query).iloc[0, 0]

def get_total_visits():
    query = "SELECT COUNT(DISTINCT visit_id) AS total_visits FROM hospital_visits_fact"
    return run_query(query).iloc[0, 0]

def get_total_patients():
    query = "SELECT COUNT(DISTINCT patient_id) AS total_patients FROM hospital_visits_fact"
    return run_query(query).iloc[0, 0]

def get_most_common_specialization():
    query = """
    SELECT d.specialization, COUNT(f.doctor_id) AS count
    FROM hospital_visits_fact f
    JOIN doctor_dim d USING (doctor_id)
    GROUP BY d.specialization
    ORDER BY count DESC
    LIMIT 1;
    """
    return run_query(query).iloc[0, 0]

def get_disease_category_counts():
    query = """
    SELECT d.category, COUNT(f.disease_id) AS disease_count
    FROM hospital_visits_fact f
    JOIN disease_dim d USING (disease_id)
    GROUP BY d.category;
    """
    return run_query(query)

def get_hospital_revenue():
    query = """
    SELECT h.hospital_name, SUM(f.total_bill) AS revenue
    FROM hospital_visits_fact f
    JOIN hospital_dim h USING (hospital_id)
    GROUP BY h.hospital_name;
    """
    return run_query(query)

# --- Streamlit Dashboard ---
st.set_page_config(page_title="Healthcare Dashboard", layout="wide")
st.title("Healthcare Data Dashboard")

# Navigation Menu
menu = st.sidebar.radio("Navigation", ["Schema","KPIs", "Aggregations"])

# --- Schema Section ---
if menu == "Schema":
    st.header("Database Schema")
    st.image("schema.png", caption="Healthcare Database Schema", use_container_width=True)


# --- KPI Section ---
elif menu == "KPIs":
    st.header("Key Performance Indicators")
    kpi_options = [
        "Total Revenue", "Total Visits", "Total Patients Treated", "Most Common Specialization Consulted"
    ]
    kpi_choice = st.selectbox("Select a KPI", kpi_options)
    
    if kpi_choice == "Total Revenue":
        total_revenue = get_total_revenue()
        st.subheader("Total Revenue")
        st.metric(label="Total Revenue", value=f"${total_revenue:,.2f}")
        
        
    
    elif kpi_choice == "Total Visits":
        total_visits = get_total_visits()
        st.subheader("Total Visits")
        st.metric(label="Total Visits", value=f"{total_visits:,}")
    
    elif kpi_choice == "Total Patients Treated":
        total_patients = get_total_patients()
        st.subheader("Total Patients Treated")
        st.metric(label="Total Patients", value=f"{total_patients:,}")
        
        
    elif kpi_choice == "Most Common Specialization Consulted":
        common_specialization = get_most_common_specialization()
        st.subheader("Most Common Specialization Consulted")
        st.metric(label="Top Specialization", value=f"{common_specialization}")
        
        
# --- Aggregations Section ---
elif menu == "Aggregations":
    st.header("Aggregations and Insights")
    agg_options = [
        "Disease Category Counts", 
        "Hospital Revenue", 
        "Average Bill by Insurance Type", 
        "Patient Visits by Age Group"
    ]
    agg_choice = st.selectbox("Select an Aggregation", agg_options)

    if agg_choice == "Disease Category Counts":
        df = get_disease_category_counts()
        fig, ax = plt.subplots()
        ax.pie(df["disease_count"], labels=df["category"], autopct='%1.1f%%', startangle=90)
        ax.set_title("Disease Category Distribution")
        st.pyplot(fig)

    elif agg_choice == "Hospital Revenue":
        df = get_hospital_revenue()
        fig, ax = plt.subplots()
        ax.pie(df["revenue"], labels=df["hospital_name"], autopct='%1.1f%%', startangle=90)
        ax.set_title("Revenue by Hospital")
        st.pyplot(fig)

    elif agg_choice == "Average Bill by Insurance Type":
        query = """
        SELECT b.insurance_type, AVG(f.total_bill) AS avg_bill
        FROM hospital_visits_fact f
        JOIN billing_dim b USING (billing_id)
        GROUP BY b.insurance_type;
        """
        df = run_query(query)
        fig, ax = plt.subplots()
        sns.barplot(x="insurance_type", y="avg_bill", data=df, ax=ax)
        ax.set_title("Average Bill by Insurance Type")
        ax.set_xlabel("Insurance Type")
        ax.set_ylabel("Average Bill ($)")
        st.pyplot(fig)

    elif agg_choice == "Patient Visits by Age Group":
        query = """
        SELECT 
            CASE 
                WHEN p.age BETWEEN 0 AND 18 THEN '0-18'
                WHEN p.age BETWEEN 19 AND 35 THEN '19-35'
                WHEN p.age BETWEEN 36 AND 50 THEN '36-50'
                WHEN p.age BETWEEN 51 AND 65 THEN '51-65'
                ELSE '65+' 
            END AS age_group,
            COUNT(f.patient_id) AS visit_count
        FROM hospital_visits_fact f
        JOIN patient_dim p USING (patient_id)
        GROUP BY age_group
        ORDER BY age_group;
        """
        df = run_query(query)
        fig, ax = plt.subplots()
        sns.barplot(x="age_group", y="visit_count", data=df, ax=ax)
        ax.set_title("Patient Visits by Age Group")
        ax.set_xlabel("Age Group")
        ax.set_ylabel("Number of Visits")
        st.pyplot(fig)

