import streamlit as st
import mysql.connector
import pandas as pd

# Connect to MySQL database
def create_connection():
    return mysql.connector.connect(
        host='https://rekhatravels.com/myweb/',   # Replace with your host   
        user='bnapajbo_himadri',    # Replace with your username
        password='Bolbok3no?',# Replace with your password
        database='bnapajbo_sln' # Replace with your database name
    )

# Function to create the table if it doesn't exist
def create_table(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            sl_no_test VARCHAR(255) NOT NULL,
            date DATE NOT NULL,     
            location_test VARCHAR(255) NOT NULL
        )
    ''')
    conn.commit()

# Function to insert data into the table
def insert_data(conn, data):
    cursor = conn.cursor()
    for _, row in data.iterrows():
        try:
            # Convert and format the date column
            date = pd.to_datetime(row['Date'], errors='coerce').strftime('%Y-%m-%d')
            
            # Check if all fields are valid
            if pd.notna(row['Location (Test)']) and pd.notna(row['Sl No (Test)']) and pd.notna(date):
                cursor.execute('''
                    INSERT INTO test_data (location_test, sl_no_test, date)
                    VALUES (%s, %s, %s)
                ''', (row['Location (Test)'], row['Sl No (Test)'], date))
        except Exception as e:
            st.error(f"Error inserting row: {e}")
    conn.commit()

# Function to fetch data based on search criteria
def fetch_data(conn, location=None, sl_no=None, date=None):
    cursor = conn.cursor(dictionary=True)
    query = 'SELECT location_test, sl_no_test, date FROM test_data WHERE 1=1'
    params = []
    if location:
        query += ' AND location_test = %s'
        params.append(location)
    if sl_no:
        query += ' AND sl_no_test = %s'
        params.append(sl_no)
    if date:
        query += ' AND date = %s'
        params.append(date)
    cursor.execute(query, tuple(params))
    return cursor.fetchall()

# Streamlit App
def main():
    st.title('MySQL Data Search and Upload Application')

    # MySQL Connection
    conn = create_connection()
    create_table(conn)

    # File uploader for CSV
    st.sidebar.subheader('Upload CSV')
    uploaded_file = st.sidebar.file_uploader('Choose a CSV file', type='csv')
    if uploaded_file is not None:
        # Read CSV file into DataFrame
        csv_data = pd.read_csv(uploaded_file)
        st.write('Uploaded Data:', csv_data)

        # Insert data into MySQL
        if st.sidebar.button('Upload to Database'):
            # Check if all required columns are present
            if {'Location (Test)', 'Sl No (Test)', 'Date'}.issubset(csv_data.columns):
                insert_data(conn, csv_data)
                st.sidebar.success('Data uploaded successfully!')
            else:
                st.sidebar.error('CSV file must contain "Location (Test)", "Sl No (Test)", and "Date" columns.')  #(Date Is YYYY-MM-DD)

    # Search Section
    st.subheader('Search Data')
    location = st.text_input('Enter Location (Test)')
    sl_no = st.text_input('Enter Sl No (Test)')
    date = st.text_input('Enter Date (YYYY-MM-DD)')

    # Ensure all fields are mandatory before searching
    if st.button('Search'):
        if location and sl_no and date:
            results = fetch_data(conn, location=location, sl_no=sl_no, date=date)
            if results:
                st.write('Search Results:', pd.DataFrame(results))
            else:
                st.write('No results found.')
        else:
            st.error('All fields are mandatory for searching!')

    # Close the database connection
    conn.close()

if __name__ == "__main__":
    main()
