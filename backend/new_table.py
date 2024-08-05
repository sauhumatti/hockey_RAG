import psycopg2

def get_table_schema(connection, table_name):
    cursor = connection.cursor()
    query = f"""
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_name = '{table_name}';
    """
    cursor.execute(query)
    schema = cursor.fetchall()
    cursor.close()
    return schema

def compare_schemas(schema1, schema2):
    schema1_set = set(schema1)
    schema2_set = set(schema2)
    
    if schema1_set == schema2_set:
        print("The schemas are identical.")
    else:
        print("The schemas are different.")
        print("\nColumns in the first table but not in the second:")
        for col in schema1_set - schema2_set:
            print(col)
        print("\nColumns in the second table but not in the first:")
        for col in schema2_set - schema1_set:
            print(col)

def main():
    db_params = {
        "dbname": "hockey_stats",
        "user": "sauhumatti",
        "host": "localhost"
    }

    try:
        connection = psycopg2.connect(**db_params)

        schema1 = get_table_schema(connection, 'player_stats_regular_season')
        schema2 = get_table_schema(connection, 'player_stats_playoffs')
        
        print("\nSchema of player_stats_regular_season:")
        for column in schema1:
            print(column)
        
        print("\nSchema of player_stats_playoffs:")
        for column in schema2:
            print(column)
        
        compare_schemas(schema1, schema2)

    except (Exception, psycopg2.Error) as error:
        print("Error while fetching table schema:", error)
    finally:
        if connection:
            connection.close()
            print("PostgreSQL connection is closed")

if __name__ == "__main__":
    main()


