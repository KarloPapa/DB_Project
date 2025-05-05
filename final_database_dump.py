import mysql.connector

def dump_database(host, user, password, database, output_file):
    conn = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    cursor = conn.cursor()

    tables = ["BC_KP_DatabaseProject"] 

    with open(output_file, "w", encoding="utf-8") as f:
        for table in tables:
            # Dump CREATE TABLE
            cursor.execute(f"SHOW CREATE TABLE `{table}`")
            create_table_sql = cursor.fetchone()[1]
            f.write(f"DROP TABLE IF EXISTS `{table}`;\n")
            f.write(f"{create_table_sql};\n\n")

            # Dump data
            cursor.execute(f"SELECT * FROM `{table}`")
            rows = cursor.fetchall()
            if rows:
                columns = [desc[0] for desc in cursor.description]
                for row in rows:
                    values = []
                    for val in row:
                        if val is None:
                            values.append("NULL")
                        else:
                            escaped_val = str(val).replace("'", "\\'")
                            values.append(f"'{escaped_val}'")
                    f.write(f"INSERT INTO `{table}` ({', '.join(columns)}) VALUES ({', '.join(values)});\n")
                f.write("\n")

    cursor.close()
    conn.close()
    print(f"Dump completed to {output_file}")

if __name__ == "__main__":
    dump_database(
        host='comp373.cianci.io',
        user='kpapa',
        password='firm-limited-eye',
        database='comp373',
        output_file='final_database_dump.sql'
    )
