from sqlalchemy import create_engine, text

engine = create_engine("postgresql://rbac_user:rbac_password@localhost:5433/postgres")
conn = engine.connect()
result = conn.execute(text("SELECT datname FROM pg_database"))
dbs = [row[0] for row in result]
print("Databases:", dbs)
