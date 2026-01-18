import sqlite3
import os

# Check both possible locations for the DB
db_paths = ['ats_history.db', 'instance/ats_history.db']
fixed = False

for db_path in db_paths:
    if os.path.exists(db_path):
        print(f"Found database at: {db_path}")
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if column exists
            cursor.execute("PRAGMA table_info(analysis)")
            columns = [info[1] for info in cursor.fetchall()]
            
            if 'file_data' not in columns:
                print("Adding missing column 'file_data'...")
                cursor.execute("ALTER TABLE analysis ADD COLUMN file_data BLOB")
                conn.commit()
                print("Column added successfully.")
                fixed = True
            else:
                print("Column 'file_data' already exists.")
                fixed = True
                
            conn.close()
        except Exception as e:
            print(f"Error modifying database {db_path}: {e}")

if not fixed:
    print("Could not find or fix any database file.")
else:
    print("Database fix completed.")
