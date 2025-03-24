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


# --- Data Mart Queries ---
def get_patient_data_mart():
    return run_query("SELECT * FROM patient_data_mart")

def get_disease_data_mart():
    return run_query("SELECT * FROM disease_data_mart")

def get_doctor_data_mart():
    return run_query("SELECT * FROM doctor_data_mart")

def get_hospital_data_mart():
    return run_query("SELECT * FROM hospital_data_mart")

def get_billing_data_mart():
    return run_query("SELECT * FROM billing_data_mart")


# --- Streamlit Dashboard ---
st.set_page_config(page_title="Healthcare Dashboard", layout="wide")
st.title("Healthcare Data Dashboard")

# Navigation Menu
menu = st.sidebar.radio("NAVIGATION", ["Schema", "KPIs", "Aggregations", "Data Marts"])

# --- Schema Section ---
if menu == "Schema":
    st.header("Database Schema")
    st.image("schema.png", caption="Healthcare Database Schema", use_container_width=True)


# --- KPI Section ---
elif menu == "KPIs":
    st.header("📊 Key Performance Indicators")
    
    kpi_options = [
        "Total Revenue", "Total Visits", "Total Patients Treated", "Most Common Specialization Consulted"
    ]
    kpi_choice = st.selectbox("🔍 Select a KPI", kpi_options)
    
    if kpi_choice == "Total Revenue":
        total_revenue = get_total_revenue()
        st.subheader("💰 Total Revenue")
        st.metric(label="Total Revenue", value=f"${total_revenue:,.2f}")

        # 📊 **Bar Chart for Total Revenue**
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.barh(["Total Revenue"], [total_revenue], color="orange")
        ax.set_xlabel("Revenue ($)")
        ax.set_title("💰 Total Revenue Generated")

        # Display value inside the bar
        for i, v in enumerate([total_revenue]):
            ax.text(v, i, f"${v:,.2f}", va='center', fontsize=12, fontweight="bold")

        st.pyplot(fig)

    elif kpi_choice == "Total Visits":
        total_visits = get_total_visits()
        st.subheader("🏥 Total Visits")
        st.metric(label="Total Visits", value=f"{total_visits:,}")

        # 📊 **Pie Chart for Total Visits**
        labels = ["Total Visits"]
        sizes = [total_visits]
        colors = ["#FF6F61"]

        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct="%1.1f%%", colors=colors, startangle=90)
        ax.set_title("🏥 Total Visits Breakdown")

        st.pyplot(fig)

    elif kpi_choice == "Total Patients Treated":
        total_patients = get_total_patients()
        st.subheader("🩺 Total Patients Treated")
        st.metric(label="Total Patients", value=f"{total_patients:,}")

        # 📊 **Gauge Chart for Total Patients**
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.barh(["Patients Treated"], [total_patients], color="seagreen")
        ax.set_xlabel("Patients")
        ax.set_title("🩺 Total Patients Treated")

        # Display value inside the bar
        for i, v in enumerate([total_patients]):
            ax.text(v, i, f"{v:,}", va='center', fontsize=12, fontweight="bold")

        st.pyplot(fig)

    elif kpi_choice == "Most Common Specialization Consulted":
        common_specialization = get_most_common_specialization()
        st.subheader("🧑‍⚕️ Most Common Specialization Consulted")
        st.metric(label="Top Specialization", value=f"{common_specialization}")

        # 📊 **Donut Chart for Specialization**
        labels = [common_specialization, "Other Specializations"]
        sizes = [70, 30]  # Assume 70% consultations for top specialization
        colors = ["#0073e6", "#d3d3d3"]

        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct="%1.1f%%", colors=colors, startangle=90, wedgeprops={'edgecolor': 'white'})
        ax.set_title("🧑‍⚕️ Specialization Popularity")

        st.pyplot(fig)
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
        query = """
        SELECT d.category, COUNT(f.disease_id) AS disease_count
        FROM hospital_visits_fact f
        JOIN disease_dim d USING (disease_id)
        GROUP BY d.category;
        """
        df = run_query(query)
        fig, ax = plt.subplots()
        ax.pie(df["disease_count"], labels=df["category"], autopct='%1.1f%%', startangle=90)
        ax.set_title("Disease Category Distribution")
        st.pyplot(fig)

    elif agg_choice == "Hospital Revenue":
        query = """
        SELECT h.hospital_name, SUM(f.total_bill) AS revenue
        FROM hospital_visits_fact f
        JOIN hospital_dim h USING (hospital_id)
        GROUP BY h.hospital_name;
        """
        df = run_query(query)
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



# --- Data Marts Section ---
elif menu == "Data Marts":
    st.header("Data Mart Insights")
    mart_options = ["Patient Data Mart", "Disease Data Mart", "Doctor Data Mart", "Hospital Data Mart", "Billing Data Mart"]
    mart_choice = st.selectbox("Select a Data Mart", mart_options)

    if mart_choice == "Patient Data Mart":
        df = get_patient_data_mart()
        st.subheader("Patient Data Mart")
        st.dataframe(df)

        st.subheader("Patient Age Distribution")
        fig, ax = plt.subplots()
        sns.histplot(df["age"], bins=20, kde=True, ax=ax)
        ax.set_xlabel("Age")
        ax.set_ylabel("Frequency")
        st.pyplot(fig)

    elif mart_choice == "Disease Data Mart":
        df = get_disease_data_mart()
        st.subheader("Disease Data Mart")
        st.dataframe(df)

        st.subheader("Most Common Diseases")
        disease_counts = df.set_index("disease_name")["total_cases"].sort_values(ascending=False)
        fig, ax = plt.subplots()
        disease_counts.head(10).plot(kind="bar", color="lightblue", ax=ax)
        ax.set_ylabel("Total Cases")
        st.pyplot(fig)

    elif mart_choice == "Doctor Data Mart":
        df = get_doctor_data_mart()
        st.subheader("Doctor Data Mart")
        st.dataframe(df)

        st.subheader("Top Specializations by Patients Seen")
        specialization_counts = df.groupby("specialization")["total_patients_seen"].sum().sort_values(ascending=False)
        fig, ax = plt.subplots()
        specialization_counts.head(10).plot(kind="bar", color="orange", ax=ax)
        ax.set_ylabel("Patients Seen")
        st.pyplot(fig)

    elif mart_choice == "Hospital Data Mart":
        df = get_hospital_data_mart()
        st.subheader("Hospital Data Mart")
        st.dataframe(df)

    # Debugging: Show column names
        st.write("Hospital Data Mart Columns:", df.columns)

    # 📊 Plot: Hospital Revenue Distribution
        st.subheader("Hospital Revenue Distribution")
        fig, ax = plt.subplots()
        sns.barplot(x="hospital_name", y="total_revenue", data=df, ax=ax)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
        ax.set_ylabel("Total Revenue ($)")
        st.pyplot(fig)

    # 📊 Plot: Hospital Patient Count
        st.subheader("Number of Patients Treated Per Hospital")
        fig, ax = plt.subplots()

    # ✅ Fixed column name from total_patients_treated → total_patients
        sns.barplot(x="hospital_name", y="total_patients", data=df, ax=ax, color="lightblue")  
    
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
        ax.set_ylabel("Total Patients Treated")
        st.pyplot(fig)


    elif mart_choice == "Billing Data Mart":
        df = get_billing_data_mart()
        st.subheader("Billing Data Mart")
        st.dataframe(df)

    # Debugging: Show column names
        st.write("Billing Data Mart Columns:", df.columns)

    # 📊 Plot: Total Revenue by Payment Method
        st.subheader("Total Revenue by Payment Method")
        fig, ax = plt.subplots()
        sns.barplot(x="payment_method", y="total_billed", data=df, ax=ax, palette="coolwarm")  # ✅ Fixed column name
        ax.set_ylabel("Total Billed ($)")
        st.pyplot(fig)

    # 📊 Plot: Claim Status Distribution
        st.subheader("Insurance Claim Status Distribution")
    
    # Handle NaN values before plotting
        df = df.dropna(subset=["claim_status"])
    
        fig, ax = plt.subplots()
        df["claim_status"].value_counts().plot(kind="pie", autopct="%1.1f%%", startangle=90, ax=ax)
        ax.set_ylabel("")
        st.pyplot(fig)



    
