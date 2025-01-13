import tkinter as tk
from tkinter import filedialog, ttk
import pandas as pd
import os
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import messagebox

# Global variables for max and min temperature
global_max_temp = None
global_min_temp = None

# Database setup
db_file = 'logfile.db'

# Create the database and table if it doesn't exist
def setup_database():
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create log_file table with additional columns for start_time, end_time, and projection_duration
    cursor.execute('''CREATE TABLE IF NOT EXISTS log_file (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_name TEXT,
        max_temperature REAL,
        min_temperature REAL,
        start_time TEXT,
        end_time TEXT,
        projection_duration INTEGER,
        upload_date TEXT
    )''')
    # Create the global_temperatures table if it doesn't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS global_temperatures (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        global_max_temp REAL,
        global_min_temp REAL
    )''')

    # Create temperature_records table to store temperature values and corresponding datetime
    # cursor.execute('''CREATE TABLE IF NOT EXISTS temperature_records (
    #     id INTEGER PRIMARY KEY AUTOINCREMENT,
    #     filename TEXT,
    #     datetime TEXT,
    #     temperature REAL
    # )''')

    # Insert initial global temperature values if the table is empty
    cursor.execute('SELECT COUNT(*) FROM global_temperatures')
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO global_temperatures (global_max_temp, global_min_temp) VALUES (?, ?)', (None, None))
    conn.commit()
    conn.close()

# Load global temperatures from the database
def load_global_temperatures():
    global global_max_temp, global_min_temp
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('SELECT global_max_temp, global_min_temp FROM global_temperatures WHERE id = 1')
    result = cursor.fetchone()
    conn.close()
    if result:
        global_max_temp, global_min_temp = result

# Function to dynamically calculate global temperatures
# Function to dynamically calculate global temperatures
def update_global_temperatures():
    global global_max_temp, global_min_temp

    # Calculate the global max/min temperatures from the database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('SELECT MAX(max_temperature), MIN(min_temperature) FROM log_file')
    result = cursor.fetchone()
    conn.close()

    # Update global variables
    global_max_temp = result[0] if result and result[0] is not None else None
    global_min_temp = result[1] if result and result[1] is not None else None

    # Update global temperature label
    global_temp_label.config(
        text=f"Global Max Temperature: {global_max_temp or '0.0'}\nGlobal Min Temperature: {global_min_temp or '0.0'}"
    )



# Function to display file details
def display_file_details():
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('SELECT file_name, max_temperature, min_temperature, start_time, end_time, projection_duration, upload_date FROM log_file')
    rows = cursor.fetchall()
    conn.close()

    # Clear existing data in the treeview
    for item in tree.get_children():
        tree.delete(item)

    # Insert rows into the treeview
    for row in rows:
        tree.insert("", "end", values=row)


# Process the file and extract relevant information
def process_file(file_path):
    global global_max_temp, global_min_temp

    file_name = os.path.basename(file_path)
    # Database connection
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Check if the file is already in the database
    cursor.execute('SELECT COUNT(*) FROM log_file WHERE file_name = ?', (file_name,))
    if cursor.fetchone()[0] > 0:
        status_label.config(text=f"File '{file_name}' has already been uploaded.", fg="red")
        conn.close()
        return  # Exit function if file is already uploaded

    # If the file is not already uploaded, proceed with the insertion

    try:    
        # Load and process the file
        df = pd.read_csv(file_path, delimiter=',', low_memory=False)
        upload_date = datetime.now().strftime('%B %d, %Y %H:%M:%S')

        df = df[["System Time", "plcToPc-elevatorTemp"]]
        df = df.iloc[1:].reset_index(drop=True)

        # Ensure 'System Time' is numeric
        df['System Time'] = pd.to_numeric(df['System Time'], errors='coerce')

        # Convert 'System Time' (Unix timestamp) to datetime
        df['datetime'] = pd.to_datetime(df['System Time'], unit='s')

        # Extract date and time into separate columns
        df['date'] = df['datetime'].dt.strftime('%B %d, %Y')  # Example: February 23, 2023
        df['time'] = df['datetime'].dt.strftime('%H:%M:%S')  # Example: 14:16:50

        # Dynamically extract and combine the date and time from the columns
        start_date_time = f"{df['date'].iloc[0]} {df['time'].iloc[0]}"  # Combine date and time for the start
        end_date_time = f"{df['date'].iloc[-1]} {df['time'].iloc[-1]}"  # Combine date and time for the end

        # Convert to datetime objects
        start = datetime.strptime(start_date_time, "%B %d, %Y %H:%M:%S")
        end = datetime.strptime(end_date_time, "%B %d, %Y %H:%M:%S")

        # Calculate the total duration
        projection_duration = end - start

        # Extract hours, minutes, and seconds
        total_seconds = projection_duration.total_seconds()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)

        # Convert projection_duration to a total duration in seconds
        # projection_duration = f"{hours:02}:{minutes:02}:{seconds:02}"
        projection_duration = f"{hours}h {minutes}min {seconds}s"

        start_time = start.strftime('%B %d, %Y %H:%M:%S')
        end_time = end.strftime('%B %d, %Y %H:%M:%S')
        
        df['plcToPc-elevatorTemp'] = pd.to_numeric(df['plcToPc-elevatorTemp'], errors='coerce')
        df['plcToPc-elevatorTemp'] = df['plcToPc-elevatorTemp'].fillna(df['plcToPc-elevatorTemp'].mean())
        df['plcToPc-elevatorTemp'] = df['plcToPc-elevatorTemp'].round(2)

        # Calculate max/min temperatures for the file
        max_temp = df['plcToPc-elevatorTemp'].max()
        min_temp = df['plcToPc-elevatorTemp'].min()

        # # Get start and end times
        # start_time = df['datetime'].min()  # Assuming 'datetime' column exists
        # end_time = df['datetime'].max()

    
        # # Calculate projection duration (in minutes)
        # projection_duration = (pd.to_datetime(end_time) - pd.to_datetime(start_time)).total_seconds() / 60

        # # Save file metadata and temperatures into the database
        # upload_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        file_name = os.path.basename(file_path)

        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Insert file metadata into log_file
        cursor.execute('''INSERT INTO log_file (file_name, max_temperature, min_temperature, start_time, end_time, projection_duration, upload_date) 
                          VALUES (?, ?, ?, ?, ?, ?, ?)''',
                       (file_name, max_temp, min_temp, start_time, end_time, projection_duration, upload_date))

        # df['filename'] = file_name
        # data = df[['plcToPc-elevatorTemp','datetime']]
        # data['temperature']= data['plcToPc-elevatorTemp']
        # data = data.drop('plcToPc-elevatorTemp', axis = "columns")

        # # Insert the data into the table
        # data.to_sql('temperature_records', conn, if_exists='append', index=False)
        # print("successfully, uploaded")
        conn.commit()
        conn.close()

        # Update global max/min based on file values
        if global_max_temp is None or max_temp > global_max_temp:
            global_max_temp = max_temp
        if global_min_temp is None or min_temp < global_min_temp:
            global_min_temp = min_temp

        # Refresh the display and update global temperatures
        display_data()
        update_global_temperatures()
        show_graph(df, file_name)
        status_label.config(text="File processed successfully!", fg="green")
        # Return the DataFrame if you need to access it later
        return df
        
    except Exception as e:
        status_label.config(text=f"Error: {str(e)}", fg="red")
        return None  # Return None if there's an error




# Function to display the data on the GUI
def display_data():
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Execute SQL query to fetch data
    cursor.execute('SELECT file_name, max_temperature, min_temperature, start_time, end_time, projection_duration, upload_date FROM log_file')
    rows = cursor.fetchall()

    # Close the database connection
    conn.close()

    # Clear existing Treeview data
    for item in tree.get_children():
        tree.delete(item)

    # Insert new data into the Treeview widget
    for row in rows:
        tree.insert("", "end", values=row)

def show_graph(df, filename):
    plt.figure(figsize=(10.8, 6))
    plt.plot(df['datetime'], df['plcToPc-elevatorTemp'], marker='o', linestyle='', color='b')

    plt.xlabel("Datetime")
    plt.ylabel("Temperature (°C)")
    plt.title(f"Temperature Over Time for {filename}")
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.show()

def on_item_double_click(event):
    item = tree.selection()[0]
    column = tree.identify_column(event.x)
    column_index = int(column[1:]) - 1
    
    if column_index in [1, 2]:  # Max or Min Temperature columns
        current_value = tree.item(item, 'values')[column_index]
        edit_temperature(item, column_index, current_value)

def edit_temperature(item, column_index, current_value):
    def update_temp():
        new_value = entry.get()
        if new_value.replace('.', '', 1).isdigit():
            new_value = float(new_value)
            values = list(tree.item(item, 'values'))
            values[column_index] = new_value
            tree.item(item, values=values)
            
            # Update database
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            file_name = values[0]
            max_temp = values[1]
            min_temp = values[2]
            cursor.execute('UPDATE log_file SET max_temperature = ?, min_temperature = ? WHERE file_name = ?', 
                           (max_temp, min_temp, file_name))
            conn.commit()
            conn.close()
            
            # Update global temperatures
            update_global_temperatures()
            
            top.destroy()
        else:
            messagebox.showerror("Invalid Input", "Please enter a valid number.")

    top = tk.Toplevel(root)
    top.title("Edit Temperature")
    top.geometry("200x100")
    label = tk.Label(top, text=f"Enter new {'max' if column_index == 1 else 'min'} temperature:")
    label.pack()
    entry = tk.Entry(top,width=20)
    entry.insert(0, current_value)
    entry.pack()
    button = tk.Button(top, text="Update", command=update_temp)
    button.pack()



# Function to open the file chooser and process the selected files
def choose_files():
    file_paths = filedialog.askopenfilenames(title="Select Files", filetypes=[("text Files", "*.txt")])
    if file_paths:
        for file_path in file_paths:
            process_file(file_path)

# Setup the main Tkinter window
root = tk.Tk()
root.title('Log Files Analysis')

root.geometry(f"{root.winfo_screenwidth()}x600")


# Create a file chooser button
choose_button = tk.Button(root, text="Choose Files", command=choose_files)
choose_button.pack(pady=10)

# Create a status label to display messages
status_label = tk.Label(root, text="", fg="green")
status_label.pack(pady=5)

# Create a label to display global temperatures
global_temp_label = tk.Label(root, text="Global Max and Min Temperature will be displayed here", fg="blue")
global_temp_label.pack(pady=5)

# Create a style for Treeview to make headings bold
style = ttk.Style()
style.configure("Treeview.Heading", font=("Helvetica", 9, "bold"))

# Set up the Treeview for displaying data (including new columns)
tree = ttk.Treeview(root, columns=("File Name", "Max Temperature", "Min Temperature", "Start Time", "End Time", "Projection Duration", "Upload Date"), show="headings")

# Set heading text and apply the style (bold heading)
tree.heading("File Name", text="File Name")
tree.heading("Max Temperature", text="Max Temperature")
tree.heading("Min Temperature", text="Min Temperature")
tree.heading("Start Time", text="Start Time")
tree.heading("End Time", text="End Time")
tree.heading("Projection Duration", text="Projection Duration")
tree.heading("Upload Date", text="Upload Date")

# Center-align column content and set width for each column
for col in tree["columns"]:
    tree.column(col, anchor="center")  # Adjust the width as per your requirement

# Center-align column content and set width for each column
tree.column("File Name", width=250)
tree.column("Max Temperature", width=110)
tree.column("Min Temperature", width=110)

tree.pack(padx=10, pady=10)

# Bind the double-click event to update the temperature values
tree.bind("<Double-1>", on_item_double_click)


# Add the button to show the graph

# Initialize database
setup_database()
update_global_temperatures()
display_file_details()

# Start the Tkinter event loop
root.mainloop()
