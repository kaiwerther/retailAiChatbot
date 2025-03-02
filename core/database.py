# core/database.py
import os
from psycopg_pool import ConnectionPool
from langgraph.checkpoint.postgres import PostgresSaver

DB_URI = os.getenv("DB_URI", "postgresql://user:password@host:port/dbname")
connection_kwargs = {"autocommit": True, "prepare_threshold": 0}

def get_checkpointer():
    pool = ConnectionPool(conninfo=DB_URI, max_size=20, kwargs=connection_kwargs)
    checkpointer = PostgresSaver(pool)
    checkpointer.setup()  # Create tables if not already present.
    return checkpointer
