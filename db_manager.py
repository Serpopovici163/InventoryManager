import sqlite3
import re
import pandas as pd

# DATABASE COLUMNS

# INDEX, MANUFACTURER PART NUMBER (string), DESCRIPTION (string), QUANTITY (integer), TYPE, ATTR1, ATTR2, ATTR3, ATTR4, ATTR5

# ATTR1-3 are part-specific attributes. For passives:
# ATTR1 -> size
# ATTR2 -> value
# ATTR3 -> tolerance
# ATTR4 -> voltage
# ATTR5 -> for future use

db_filename = "inventory.db"

def db_add_order(backup_path, BOM_file):

    #ChatGPT wrote most of this :))))))

    # Assuming df is your DataFrame
    # Read your DataFrame from a file or create it in your code
    # For example:
    df = pd.read_csv(BOM_file)
    
    print("\nGot the following BOM:\n")
    print(df)

    # Define the columns to keep
    columns_to_keep = ['manufacturer part number', 'quantity', 'description']

    # Convert the column names in the DataFrame to lowercase
    df.columns = df.columns.str.lower()

    # Filter the DataFrame to keep only the desired columns
    filtered_columns = []
    for col in df.columns:
        value = df.iloc[0][col]       
        if col.strip().lower() in columns_to_keep:
            filtered_columns.append(col)

    # Delete the last row in the DataFrame (full of NaNs)
    df = df.drop(df.index[-1])

    df = df[filtered_columns]

    # Display or save the modified DataFrame
    print("\nCondensed it to:\n")
    print(df)
    df.to_csv(backup_path + '/curated_BOM.csv', index=False)

    # Read the modified CSV file
    df = pd.read_csv(backup_path + '/curated_BOM.csv')

    # Connect to the SQLite database
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()

    # Create the "inventory" table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            MANUFACTURER_PART_NUMBER TEXT,
            DESCRIPTION TEXT,
            QUANTITY INTEGER,
            TYPE TEXT,
            ATTR1 TEXT,
            ATTR2 TEXT,
            ATTR3 TEXT,
            ATTR4 TEXT,
            ATTR5 TEXT
        )
    ''')

    # Define a function to determine the type based on the description (ChatGPT wrote this)
    def determine_type_and_attributes(description):
        type_ = ""
        attr1 = None
        attr2 = None
        attr3 = None
        attr4 = None
        attr5 = None
        
        if "RES" in description.upper():
            type_ = "RES"
            attr1_match = re.search(r'\b\d{4}\b', description)
            if attr1_match:
                attr1 = attr1_match.group()
            attr2_match = re.search(r'\b\d{1,4}(?:\.\d+)?\s?[kKmM]?\s?OHM\b', description, re.IGNORECASE)
            if attr2_match:
                attr2 = attr2_match.group()
            attr3_match = re.search(r'\d+%', description)
            if attr3_match:
                attr3 = attr3_match.group()
        elif "CAP" in description.upper():
            type_ = "CAP"
            attr1_match = re.search(r'\b\d{4}\b', description)
            if attr1_match:
                attr1 = attr1_match.group()
            attr2_match = re.search(r'\b\d{1,4}(?:\.\d+)?\s?(?:UF|uF)', description, re.IGNORECASE)
            if attr2_match:
                attr2 = attr2_match.group()
            attr3_match = re.search(r'\d+(?=V)', description)
            if attr3_match:
                attr3 = attr3_match.group() + "V"
            attr4_match = re.search(r'[a-zA-Z]\d[a-zA-Z]', description)
            if attr4_match:
                attr4 = attr4_match.group()
        elif "DIODE" in description.upper():
            type_ = "DIODE"
            attr1_match = re.search(r'\d+(?=V)', description)
            if attr1_match:
                attr1 = attr1_match.group() + "V"
            attr2_match = re.search(r'\d+ ?(?:mA|A)\b', description, re.IGNORECASE)
            if attr2_match:
                attr2 = attr2_match.group().upper()
        elif "FUSE" in description.upper():
            type_ = "FUSE"
            attr1_match = re.search(r'\d+(?=V)', description)
            if attr1_match:
                attr1 = attr1_match.group() + "V"
            attr2_match = re.search(r'\d+ ?(?:mA|A)\b', description, re.IGNORECASE)
            if attr2_match:
                attr2 = attr2_match.group().upper()
        elif "CONN" in description.upper():
            type_ = "CONN"
            if "CRIMP" in description.upper():
                type_ = "CRIMP"
            attr1_match = re.search(r'\b\d+ ?POS\b', description, re.IGNORECASE)
            if attr1_match:
                attr1 = attr1_match.group().upper()
            attr2_match = re.search(r'\b\d+(\.\d+)? ?(?:MM|IN|")\b', description, re.IGNORECASE)
            if attr2_match:
                attr2 = attr2_match.group().upper()
        elif "MOSFET" in description.upper():
            type_ = "MOSFET"
            attr1_match = re.search(r'[PN]-\d', description)
            if attr1_match:
                attr1 = attr1_match.group()
            attr2_match = re.search(r'\d+(?=V)', description)
            if attr2_match:
                attr2 = attr2_match.group() + "V"
            attr2_match = re.search(r'\d+ ?(?:mA|A)\b', description, re.IGNORECASE)
            if attr2_match:
                attr2 = attr2_match.group().upper()
        else:
            type_ = "OTHER"
            attr1_match = re.search(r'\d+(?=V)', description)
            if attr1_match:
                attr1 = attr1_match.group() + "V"
            attr2_match = re.search(r'\d+ ?(?:mA|A)\b', description, re.IGNORECASE)
            if attr2_match:
                attr2 = attr2_match.group().upper()
        
        return type_, attr1, attr2, attr3, attr4, attr5

    for index, row in df.iterrows():
        # Determine the type and attributes based on the description
        type_, attr1, attr2, attr3, attr4, attr5 = determine_type_and_attributes(row['description'])
        
        # Check if the item already exists in the database
        cursor.execute('SELECT QUANTITY FROM inventory WHERE MANUFACTURER_PART_NUMBER = ?', (row['manufacturer part number'],))
        existing_quantity = cursor.fetchone()
        
        if existing_quantity:
            # If item exists, update the quantity
            new_quantity = existing_quantity[0] + row['quantity']
            cursor.execute('''
                UPDATE inventory 
                SET QUANTITY = ?
                WHERE MANUFACTURER_PART_NUMBER = ?
            ''', (new_quantity, row['manufacturer part number']))
        else:
            # If item doesn't exist, insert a new entry
            cursor.execute('''
                INSERT INTO inventory (MANUFACTURER_PART_NUMBER, DESCRIPTION, QUANTITY, TYPE, ATTR1, ATTR2, ATTR3, ATTR4, ATTR5)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (row['manufacturer part number'], row['description'], row['quantity'], type_, attr1, attr2, attr3, attr4, attr5))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def db_add_board(board_path, BOM_file):
    # Assuming df is your DataFrame
    # Read your DataFrame from a file or create it in your code
    # For example:
    df = pd.read_csv(BOM_file, encoding='unicode_escape')
    
    df.columns = df.columns.str.lower()

    print("\nGot the following BOM:\n")
    print(df)

    # Create a new column "preferred_name" that holds values from "manufacturer part number 1" if available, otherwise from "name"
    df['manufacturer_part_number'] = df['manufacturer part number 1'].fillna(df['name'])

    # Define the columns to keep
    columns_to_keep = ['manufacturer_part_number', 'description', 'quantity']

    # Convert the column names in the DataFrame to lowercase
    df.columns = df.columns.str.lower()

    # Filter the DataFrame to keep only the desired columns
    filtered_columns = []
    for col in df.columns:
        value = df.iloc[0][col]       
        if col.strip().lower() in columns_to_keep:
            filtered_columns.append(col)

    # Delete the last row in the DataFrame (full of NaNs)
    df = df.drop(df.index[-1])

    df = df[filtered_columns]

    # Display or save the modified DataFrame
    print("\nCondensed it to:\n")
    print(df)
    df.to_csv(board_path + '/curated_BOM.csv', index=False)