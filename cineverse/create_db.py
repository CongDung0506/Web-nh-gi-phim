import pyodbc

conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=.;DATABASE=master;Trusted_Connection=yes;', autocommit=True)
cur = conn.cursor()
cur.execute("IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'CineVerse_DB') CREATE DATABASE [CineVerse_DB];")
print("Database CineVerse_DB created successfully!")
conn.close()
