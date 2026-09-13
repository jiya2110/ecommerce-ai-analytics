from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import URL

DB_USER = "root"
DB_PASSWORD = "UserJain@123"
DB_HOST = "localhost"
DB_PORT = 3306
DB_NAME = "my_database"

connection_url = URL.create(
    "mysql+mysqlconnector",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
)

engine = create_engine(connection_url)

# Test connection
with engine.connect() as conn:
    result = conn.exec_driver_sql("SELECT 1")
    print("Connected:", result.fetchone())

# Pull schema
inspector = inspect(engine)
schema_info = {}
for table_name in inspector.get_table_names():
    columns = inspector.get_columns(table_name)
    schema_info[table_name] = [col["name"] + " (" + str(col["type"]) + ")" for col in columns]

print("\n--- Your Database Schema ---")
for table, cols in schema_info.items():
    print(table)
    for c in cols:
        print("  -", c)