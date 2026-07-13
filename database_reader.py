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

        cursor.execute(f"PRAGMA foreign_key_list({table_name})")
        foreign_keys = cursor.fetchall()

        foreign_key_map = {}

        for foreign_key in foreign_keys:

            foreign_key_map[foreign_key[3]] = (
                f"{foreign_key[2]}.{foreign_key[4]}"
            )

        columns = []

        for column in column_info:

            column_name = column[1]

            columns.append({

                "name": column_name,
                "type": column[2],
                "nullable": "No" if column[3] else "Yes",
                "default": column[4] if column[4] else "-",
                "primary_key": "Yes" if column[5] else "No",
                "foreign_key": foreign_key_map.get(column_name, "-")

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