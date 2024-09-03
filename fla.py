from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import pandas as pd

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Required for flash messages

# Connect to SQLite database (creates a new database if it doesn't exist)
def create_connection():
    try:
        conn = sqlite3.connect('test_data.db')
        return conn
    except sqlite3.Error as err:
        print(f"Error: {err}")
        return None

# Function to create the table if it doesn't exist
def create_table(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sl_no_test TEXT NOT NULL,
            date TEXT NOT NULL,     
            location_test TEXT NOT NULL
        )
    ''')
    conn.commit()

# Function to insert data into the table
def insert_data(conn, data):
    cursor = conn.cursor()
    for _, row in data.iterrows():
        try:
            date = pd.to_datetime(row['Date'], errors='coerce').strftime('%Y-%m-%d')
            if pd.notna(row['Location (Test)']) and pd.notna(row['Sl No (Test)']) and pd.notna(date):
                cursor.execute('''
                    INSERT INTO test_data (location_test, sl_no_test, date)
                    VALUES (?, ?, ?)
                ''', (row['Location (Test)'], row['Sl No (Test)'], date))
        except Exception as e:
            print(f"Error inserting row: {e}")
    conn.commit()

# Function to fetch data based on search criteria
def fetch_data(conn, location=None, sl_no=None, date=None):
    cursor = conn.cursor()
    query = 'SELECT location_test, sl_no_test, date FROM test_data WHERE 1=1'
    params = []
    if location:
        query += ' AND location_test = ?'
        params.append(location)
    if sl_no:
        query += ' AND sl_no_test = ?'
        params.append(sl_no)
    if date:
        query += ' AND date = ?'
        params.append(date)
    cursor.execute(query, tuple(params))
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

# Main route
@app.route('/', methods=['GET', 'POST'])
def index():
    conn = create_connection()
    if conn is None:
        flash("Failed to connect to the database.", "error")
        return redirect(url_for('index'))
    create_table(conn)

    if request.method == 'POST':
        # File upload
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                try:
                    data = pd.read_csv(file)
                    if {'Location (Test)', 'Sl No (Test)', 'Date'}.issubset(data.columns):
                        insert_data(conn, data)
                        flash('Data uploaded successfully!', 'success')
                    else:
                        flash('CSV file must contain "Location (Test)", "Sl No (Test)", and "Date" columns.', 'error')
                except Exception as e:
                    flash(f'Error reading file: {e}', 'error')

        # Search
        location = request.form.get('location')
        sl_no = request.form.get('sl_no')
        date = request.form.get('date')
        results = fetch_data(conn, location=location or None, sl_no=sl_no or None, date=date or None)

        conn.close()
        return render_template('index.html', results=results)

    conn.close()
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
