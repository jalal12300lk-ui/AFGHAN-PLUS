import os
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String

DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace(
            "postgres://", "postgresql+psycopg://", 1
        )
    elif DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace(
            "postgresql://", "postgresql+psycopg://", 1
        )

    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
else:
    os.makedirs("database", exist_ok=True)
    engine = create_engine(
        "sqlite:///database/orders.db",
        connect_args={"check_same_thread": False}
    )

metadata = MetaData()

orders = Table(
    "orders",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("phone", String),
    Column("operator", String),
    Column("amount", Integer),
    Column("status", String)
)

def init_db():
    metadata.create_all(engine)
