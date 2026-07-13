import os
import sqlite3


def analyze_database(database_path):

    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    database_name = os.path.basename(database_path)

    database_size = round(
        os.path.getsize(database_path) / 1024,
        2
    )

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)

    table_names = [row[0] for row in cursor.fetchall()]

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='view'
    """)

    total_views = len(cursor.fetchall())

    total_columns = 0
    total_rows = 0

    tables = []

    for table_name in table_names:

        cursor.execute(f"PRAGMA table_info({table_name})")
        column_info = cursor.fetchall()

        columns = []

        for column in column_info:

            columns.append({

                "name": column[1],
                "type": column[2],
                "nullable": "No" if column[3] else "Yes",
                "default": column[4] if column[4] else "-",
                "primary_key": "Yes" if column[5] else "No"

            })

        total_columns += len(columns)

        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]

        total_rows += row_count

        tables.append({

            "table_name": table_name,
            "row_count": row_count,
            "columns": columns

        })

    connection.close()

    return {

        "database_name": database_name,
        "database_size": database_size,
        "total_tables": len(table_names),
        "total_views": total_views,
        "total_columns": total_columns,
        "total_rows": total_rows,
        "tables": tables

    }