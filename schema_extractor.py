import sqlite3
import yaml
import os

DB_PATH = 'cashflo_sample.db'
OUTPUT_YAML = 'semantic_layer.yaml'

def extract_schema(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall() if row[0] != 'sqlite_sequence']
    
    schema_dict = {
        'tables': {}
    }
    
    for table in tables:
        schema_dict['tables'][table] = {
            'description': f'Auto-discovered table: {table}',
            'synonyms': [],
            'columns': {},
            'relationships': []
        }
        
        # Get columns
        cursor.execute(f"PRAGMA table_info({table});")
        columns = cursor.fetchall()
        for col in columns:
            col_name = col[1]
            col_type = col[2]
            schema_dict['tables'][table]['columns'][col_name] = {
                'type': col_type.lower() if col_type else 'any',
                'desc': f"Auto-discovered column: {col_name}"
            }
            
        # Get foreign keys (relationships)
        cursor.execute(f"PRAGMA foreign_key_list({table});")
        fks = cursor.fetchall()
        for fk in fks:
            # fk is a tuple: (id, seq, table, from, to, on_update, on_delete, match)
            target_table = fk[2]
            from_col = fk[3]
            to_col = fk[4]
            schema_dict['tables'][table]['relationships'].append({
                'table': target_table,
                'join': f"{table}.{from_col} = {target_table}.{to_col}"
            })
            
    conn.close()
    return schema_dict

def main():
    if not os.path.exists(DB_PATH):
        print(f"Error: {DB_PATH} not found.")
        return
        
    print(f"Extracting schema from {DB_PATH}...")
    schema = extract_schema(DB_PATH)
    
    # Dump to YAML
    with open(OUTPUT_YAML, 'w') as f:
        yaml.dump(schema, f, sort_keys=False, default_flow_style=False)
    
    print(f"Successfully wrote draft semantic layer to {OUTPUT_YAML}")

if __name__ == "__main__":
    main()
