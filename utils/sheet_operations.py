from datetime import datetime
import datetime


def get_common_month_year(conn):
    """
    Finds the most frequent month and year from the Timestamp column.
    
    Returns:
        A tuple (year, month) representing the most common month-year combo.
    """
    cursor = conn.cursor()
    
    try:
        # SQLite's strftime is used here. For other databases, the syntax may differ.
        cursor.execute(
            """
            SELECT strftime('%Y', Timestamp), strftime('%m', Timestamp), COUNT(*) 
            FROM transactions 
            GROUP BY 1, 2 
            ORDER BY 3 DESC 
            LIMIT 1
            """
        )
        result = cursor.fetchone()
        
        if result:
            common_year = int(result[0])
            common_month = int(result[1])
            return common_year, common_month
        else:
            # If no data exists, default to the current month and year.
            now = datetime.datetime.now()
            return now.year, now.month
            
    except Exception as e:
        print(f"Error finding common month/year: {e}")
        # Default to current month/year on error
        now = datetime.datetime.now()
        return now.year, now.month
    finally:
        conn.close()


# Assumes get_db_connection() is available and returns a database connection.
def archive_and_create_new_table(new_title,conn):
    """
    Renames the current 'transactions' table and creates a new one
    with the exact same schema using the LIKE keyword.
    
    Args:
        new_title: The name to use for the archived table (e.g., transactions_2025_08).
    """
    cursor = conn.cursor()

    try:
        # Step 1: Rename the old table to the new, archived title.
        # This table will now serve as a template for the new one.
        print(f"Archiving current 'transactions' table to '{new_title}'...")
        cursor.execute(f"ALTER TABLE transactions RENAME TO {new_title}")
        
        # Step 2: Create a new, empty 'transactions' table
        # using the schema of the newly archived table.
        print("Creating a new 'transactions' table with the same schema...")
        cursor.execute(f"CREATE TABLE transactions LIKE {new_title}")
        
        conn.commit()
        print("✅ Tables archived and new table created successfully.")
    
    except Exception as e:
        conn.rollback() # Rollback on error
        print(f"❌ Error during table archiving: {e}")
    finally:
        cursor.close()