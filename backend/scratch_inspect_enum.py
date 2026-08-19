import os
from sqlalchemy import create_engine, text

# Get DB url from .env
with open(".env") as f:
    lines = f.readlines()
db_url = None
for l in lines:
    if l.startswith("DATABASE_URL="):
        db_url = l.split("DATABASE_URL=")[1].strip().strip('"')

if not db_url:
    db_url = "postgresql://postgres:postgres@127.0.0.1:5432/cyber_shield"

engine = create_engine(db_url)
with engine.connect() as conn:
    # Get values of user_role enum
    res = conn.execute(text("""
        SELECT enumlabel FROM pg_enum
        JOIN pg_type ON pg_enum.enumtypid = pg_type.oid
        WHERE pg_type.typname = 'user_role';
    """))
    print("Enum values in DB:")
    for row in res:
        print(row[0])
