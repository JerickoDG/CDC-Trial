import streamlit as st
import mysql.connector
from kafka import KafkaConsumer, KafkaAdminClient
import json
import threading
import time
import pandas as pd
import plotly.express as px
from datetime import datetime

# Configuration
MYSQL_CONFIG = {
    'host': 'mysql',
    'user': 'jobuser',
    'password': 'jobpass',
    'database': 'jobdb'
}

KAFKA_CONFIG = {
    'bootstrap_servers': 'kafka:9092',
    'auto_offset_reset': 'latest',
    'enable_auto_commit': True,
    'group_id': 'streamlit-consumer'
}

# Initialize session state
if 'job_orders' not in st.session_state:
    st.session_state.job_orders = []
if 'kafka_messages' not in st.session_state:
    st.session_state.kafka_messages = []

def get_db_connection():
    return mysql.connector.connect(**MYSQL_CONFIG)

def fetch_job_orders():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM job_orders ORDER BY created_at DESC")
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def update_job_order(job_order_number, current_qty, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Calculate percentage
    cursor.execute("SELECT desired_qty FROM job_orders WHERE job_order_number = %s", (job_order_number,))
    result = cursor.fetchone()
    desired_qty = result[0]
    percent_completion = (current_qty / desired_qty) * 100 if desired_qty > 0 else 0
    
    # Update the record
    cursor.execute("""
        UPDATE job_orders 
        SET current_qty = %s, percent_completion = %s, status = %s, updated_at = NOW()
        WHERE job_order_number = %s
    """, (current_qty, percent_completion, status, job_order_number))
    
    conn.commit()
    cursor.close()
    conn.close()

def create_job_order(job_order_number, desired_qty):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO job_orders (job_order_number, desired_qty, current_qty, percent_completion, status)
        VALUES (%s, %s, 0, 0.00, 'ONGOING')
    """, (job_order_number, desired_qty))
    
    conn.commit()
    cursor.close()
    conn.close()

def kafka_consumer():
    try:
        consumer = KafkaConsumer(
            'mysql-server.jobdb.job_orders',  # Updated topic name
            **KAFKA_CONFIG,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')) if m else None
        )
        
        st.session_state.kafka_messages.append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'operation': 'info',
            'data': {'message': 'Kafka consumer started successfully'}
        })
        
        for message in consumer:
            if message.value:
                st.session_state.kafka_messages.append({
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'operation': message.value.get('op', 'unknown'),
                    'data': message.value.get('after', message.value.get('before', {}))
                })
                # Keep only last 10 messages
                if len(st.session_state.kafka_messages) > 10:
                    st.session_state.kafka_messages.pop(0)
                
                # Refresh the job orders
                st.session_state.job_orders = fetch_job_orders()
                
                # Trigger a rerun to update the UI
                st.rerun()
    except Exception as e:
        st.session_state.kafka_messages.append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'operation': 'error',
            'data': {'message': f'Kafka consumer error: {str(e)}'}
        })

# Start Kafka consumer in background thread
def start_kafka_consumer():
    thread = threading.Thread(target=kafka_consumer, daemon=True)
    thread.start()

# Streamlit UI
st.set_page_config(page_title="Job Orders CDC Dashboard", layout="wide")
st.title("📊 Real-time Job Orders CDC Dashboard")

# Initialize data
if not st.session_state.job_orders:
    st.session_state.job_orders = fetch_job_orders()

# Start Kafka consumer
start_kafka_consumer()

# Sidebar for operations
st.sidebar.header("Operations")

# Create new job order
st.sidebar.subheader("Create New Job Order")
with st.sidebar.form("create_job"):
    new_job_number = st.text_input("Job Order Number")
    new_desired_qty = st.number_input("Desired Quantity", min_value=1, value=100)
    
    if st.form_submit_button("Create Job Order"):
        if new_job_number:
            try:
                create_job_order(new_job_number, new_desired_qty)
                st.sidebar.success(f"Job order {new_job_number} created!")
                st.session_state.job_orders = fetch_job_orders()
            except Exception as e:
                st.sidebar.error(f"Error creating job order: {str(e)}")

# Update job order
st.sidebar.subheader("Update Job Order")
if st.session_state.job_orders:
    job_numbers = [job['job_order_number'] for job in st.session_state.job_orders]
    selected_job = st.sidebar.selectbox("Select Job Order", job_numbers)

    if selected_job:
        current_job = next((job for job in st.session_state.job_orders if job['job_order_number'] == selected_job), None)
        if current_job:
            current_qty = st.sidebar.number_input("Current Quantity", 
                                                min_value=0, 
                                                max_value=current_job['desired_qty'],
                                                value=current_job['current_qty'])
            
            status = st.sidebar.selectbox("Status", ["ONGOING", "COMPLETED"], 
                                        index=0 if current_job['status'] == 'ONGOING' else 1)
            
            if st.sidebar.button("Update Job Order"):
                update_job_order(selected_job, current_qty, status)
                st.sidebar.success(f"Job order {selected_job} updated!")
                st.session_state.job_orders = fetch_job_orders()

# Main content area
st.subheader("Job Orders")

if st.session_state.job_orders:
    df = pd.DataFrame(st.session_state.job_orders)
    st.dataframe(df, use_container_width=True)
    
    # Progress chart
    st.subheader("Completion Progress")
    fig = px.bar(df, x='job_order_number', y='percent_completion',
                title='Job Order Completion Percentage',
                color='status',
                color_discrete_map={'ONGOING': 'blue', 'COMPLETED': 'green'})
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No job orders found")


# Manual refresh button
if st.button("Refresh Data"):
    st.session_state.job_orders = fetch_job_orders()
    st.rerun()

# Debug information
with st.expander("Debug Information"):
    st.write("Kafka Topics:")
    try:
        admin = KafkaAdminClient(bootstrap_servers='kafka:9092')
        topics = admin.list_topics()
        st.write(list(topics))
    except Exception as e:
        st.error(f"Error listing topics: {e}")