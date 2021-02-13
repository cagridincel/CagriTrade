import psycopg2

con = psycopg2.connect(database="postgres", user="cagridb", password="1234", host="127.0.0.1", port="5432")

print("Database opened successfully")