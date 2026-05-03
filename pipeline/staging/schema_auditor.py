import sqlite3

def check_gold_schema(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Fetch all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = cursor.fetchall()
    
    print(f"--- PUO GOLD LAYER SCHEMA AUDIT: {db_path} ---")
    
    for table_name in tables:
        table_name = table_name[0]
        print(f"\n[TABLE: {table_name}]")
        
        # Get column details
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        
        # Header for columns
        print(f"{'CID':<4} {'Name':<20} {'Type':<15} {'NotNull':<8} {'PK':<3}")
        print("-" * 55)
        
        for col in columns:
            cid, name, dtype, notnull, dflt, pk = col
            print(f"{cid:<4} {name:<20} {dtype:<15} {notnull:<8} {pk:<3}")
            
        # Check for Foreign Keys
        cursor.execute(f"PRAGMA foreign_key_list({table_name});")
        fks = cursor.fetchall()
        if fks:
            print(f"-> Foreign Keys: {fks}")
            
    conn.close()

if __name__ == "__main__":
    check_gold_schema("data/puo_gold.db")
