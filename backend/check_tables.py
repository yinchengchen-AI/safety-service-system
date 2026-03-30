from sqlalchemy import create_engine, text

engine = create_engine("postgresql://rbac_user:rbac_password@localhost:5433/rbac_db")
conn = engine.connect()
result = conn.execute(
    text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
)
tables = [row[0] for row in result]
print("Tables in database:", tables)
