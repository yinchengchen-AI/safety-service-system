import os

DATABASE_URL = "postgresql://postgres:postgres123@localhost:5432/safety_service"
from sqlalchemy import create_engine, text

engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    result = conn.execute(
        text(
            "SELECT column_name FROM information_schema.columns WHERE table_name='payments' AND column_name='status'"
        )
    )
    if result.fetchone():
        print("status 字段已存在，无需添加")
    else:
        conn.execute(
            text("ALTER TABLE payments ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'confirmed'")
        )
        conn.execute(text("COMMENT ON COLUMN payments.status IS '收款状态'"))
        conn.commit()
        print("已添加 status 字段到 payments 表")
