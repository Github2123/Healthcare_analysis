import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine, text

# Database Connection
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "healthcare",
}

engine = create_engine(f"mysql+mysqlconnector://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}")

# Function to fetch data
def run_query(query):
    with engine.connect() as connection:
        result = connection.execute(text(query))
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
    return df

# Functions to fetch data marts
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

# Streamlit App
st.set_page_config(page_title="Healthcare Data Marts", layout="wide")

st.sidebar.title("Navigation")
menu = st.sidebar.radio("Select a Data Mart", 
                        ["Patient Data Mart", "Disease Data Mart", "Doctor Data Mart", "Hospital Data Mart", "Billing Data Mart"])

# 📂 Data Marts Section
st.title("Healthcare Data Marts")

if menu == "Patient Data Mart":
    df = get_patient_data_mart()
    st.subheader("Patient Data Mart")
    st.dataframe(df)

    # Visualization: Age Distribution
    st.subheader("Patient Age Distribution")
    fig, ax = plt.subplots()
    sns.histplot(df["age"], bins=20, kde=True, ax=ax)
    ax.set_xlabel("Age")
    ax.set_ylabel("Frequency")
    st.pyplot(fig)

elif menu == "Disease Data Mart":
    df = get_disease_data_mart()
    st.subheader("Disease Data Mart")
    st.dataframe(df)

    # Visualization: Disease Cases
    st.subheader("Most Common Diseases")
    disease_counts = df.set_index("disease_name")["total_cases"].sort_values(ascending=False)
    fig, ax = plt.subplots()
    disease_counts.head(10).plot(kind="bar", color="lightblue", ax=ax)
    ax.set_ylabel("Total Cases")
    st.pyplot(fig)

elif menu == "Doctor Data Mart":
    df = get_doctor_data_mart()
    st.subheader("Doctor Data Mart")
    st.dataframe(df)

    # Visualization: Specialization Distribution
    st.subheader("Top Specializations by Patients Seen")
    specialization_counts = df.groupby("specialization")["total_patients_seen"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots()
    specialization_counts.head(10).plot(kind="bar", color="orange", ax=ax)
    ax.set_ylabel("Patients Seen")
    st.pyplot(fig)

elif menu == "Hospital Data Mart":
    df = get_hospital_data_mart()
    st.subheader("Hospital Data Mart")
    st.dataframe(df)

    # Visualization: Hospital Type Distribution
    st.subheader("Hospital Type Distribution")
    hospital_counts = df["type"].value_counts()
    fig, ax = plt.subplots()
    hospital_counts.plot(kind="pie", autopct='%1.1f%%', colors=sns.color_palette("pastel"), ax=ax)
    st.pyplot(fig)

elif menu == "Billing Data Mart":
    df = get_billing_data_mart()
    st.subheader("Billing Data Mart")
    st.dataframe(df)

    # Visualization: Payment Method Distribution
    st.subheader("Payment Methods Used")
    payment_counts = df["payment_method"].value_counts()
    fig, ax = plt.subplots()
    payment_counts.plot(kind="bar", color="purple", ax=ax)
    ax.set_ylabel("Number of Transactions")
    st.pyplot(fig)

st.sidebar.markdown("---")
st.sidebar.text("📊 Healthcare Data Marts Dashboard")
