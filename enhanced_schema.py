#!/usr/bin/env python3
"""
Enhanced script to extract comprehensive database schema information
"""
import os
import psycopg
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
db_config = {
    'host': os.getenv('DB_SERVER', 'localhost'),
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'sslmode': 'prefer'
}

def get_comprehensive_schema():
    """Extract comprehensive database schema information"""
    try:
        conn = psycopg.connect(**db_config)
        cursor = conn.cursor(row_factory=psycopg.rows.dict_row)

        # Get all tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()

        print("=== COMPREHENSIVE DATABASE SCHEMA ===")
        print(f"Database: {db_config['dbname']}")
        print(f"Tables found: {len(tables)}")
        print("="*50)

        for table in tables:
            table_name = table['table_name']
            print(f"\nTable: {table_name}")
            print("-" * (len(table_name) + 7))

            # Get columns for this table
            cursor.execute("""
                SELECT 
                    column_name,
                    data_type,
                    character_maximum_length,
                    numeric_precision,
                    numeric_scale,
                    is_nullable,
                    column_default,
                    ordinal_position
                FROM information_schema.columns 
                WHERE table_name = %s 
                AND table_schema = 'public'
                ORDER BY ordinal_position;
            """, (table_name,))

            columns = cursor.fetchall()

            for col in columns:
                col_info = f"  {col['column_name']}"

                # Handle different data types
                if col['data_type'] in ['character varying', 'varchar']:
                    if col['character_maximum_length']:
                        col_info += f" VARCHAR({col['character_maximum_length']})"
                    else:
                        col_info += f" VARCHAR"
                elif col['data_type'] == 'character':
                    col_info += f" CHAR({col['character_maximum_length']})"
                elif col['data_type'] == 'numeric' and col['numeric_precision']:
                    if col['numeric_scale'] and col['numeric_scale'] > 0:
                        col_info += f" NUMERIC({col['numeric_precision']},{col['numeric_scale']})"
                    else:
                        col_info += f" NUMERIC({col['numeric_precision']})"
                elif col['data_type'] == 'timestamp with time zone':
                    col_info += " TIMESTAMPTZ"
                elif col['data_type'] == 'timestamp without time zone':
                    col_info += " TIMESTAMP"
                else:
                    col_info += f" {col['data_type'].upper()}"

                if col['is_nullable'] == 'NO':
                    col_info += " NOT NULL"

                if col['column_default']:
                    col_info += f" DEFAULT {col['column_default']}"

                print(col_info)

            # Get primary keys
            cursor.execute("""
                SELECT a.attname
                FROM pg_index i
                JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
                JOIN pg_class c ON c.oid = i.indrelid
                WHERE c.relname = %s AND i.indisprimary;
            """, (table_name,))

            pks = cursor.fetchall()
            if pks:
                pk_columns = [pk['attname'] for pk in pks]
                print(f"  PRIMARY KEY: ({', '.join(pk_columns)})")

            # Get foreign keys
            cursor.execute("""
                SELECT
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name,
                    rc.constraint_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                    AND ccu.table_schema = tc.table_schema
                JOIN information_schema.referential_constraints AS rc
                    ON tc.constraint_name = rc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
                    AND tc.table_name = %s
                    AND tc.table_schema = 'public';
            """, (table_name,))

            foreign_keys = cursor.fetchall()
            if foreign_keys:
                print("  FOREIGN KEYS:")
                for fk in foreign_keys:
                    print(f"    {fk['column_name']} -> {fk['foreign_table_name']}.{fk['foreign_column_name']}")

            # Get indexes (excluding primary key)
            cursor.execute("""
                SELECT
                    i.relname AS index_name,
                    array_agg(a.attname ORDER BY array_position(ix.indkey, a.attnum)) AS column_names,
                    ix.indisunique
                FROM pg_class t
                JOIN pg_index ix ON t.oid = ix.indrelid
                JOIN pg_class i ON i.oid = ix.indexrelid
                JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(ix.indkey)
                WHERE t.relname = %s
                    AND NOT ix.indisprimary
                    AND t.relkind = 'r'
                GROUP BY i.relname, ix.indisunique
                ORDER BY i.relname;
            """, (table_name,))

            indexes = cursor.fetchall()
            if indexes:
                print("  INDEXES:")
                for idx in indexes:
                    unique_str = "UNIQUE " if idx['indisunique'] else ""
                    print(f"    {unique_str}INDEX {idx['index_name']} ({', '.join(idx['column_names'])})")

        print("\n" + "="*50)
        print("SCHEMA EXTRACTION COMPLETE")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error extracting schema: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    get_comprehensive_schema()
