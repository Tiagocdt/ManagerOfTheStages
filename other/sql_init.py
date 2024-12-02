import sqlite3
import json

# Step 1: Connect to SQLite database (this will create the file if it doesn't exist)
conn = sqlite3.connect('medaka_development.db')
cursor = conn.cursor()

# Step 2: Create the table (only if it doesn't already exist)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS development_times (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        species TEXT NOT NULL,
        temperature REAL NOT NULL,
        stage INTEGER NOT NULL,
        development_time_hpf REAL NOT NULL
    );
''')

# Step 3: Insert data from JSON file into the database
def insert_data(species, temperature, stage, development_time_hpf):
    cursor.execute('''
        INSERT INTO development_times (species, temperature, stage, development_time_hpf)
        VALUES (?, ?, ?, ?)
    ''', (species, temperature, stage, development_time_hpf))
    conn.commit()

# Step 4: Load data from JSON file and insert it into the database
with open('Development_Times.json', 'r') as file:
    data = json.load(file)
    for temp_data in data['temperatures']:
        temperature = float(temp_data['temperature'])
        for stage_data in temp_data['stages']:
            stage = int(stage_data['stage'])
            for development_time in stage_data['times']:
                # Assuming species is static for now, you can modify this if species data is in JSON
                insert_data('Oryzias latipes', temperature, stage, development_time)

# Close the connection when done
conn.close()
