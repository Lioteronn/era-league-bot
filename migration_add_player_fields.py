# Migration script to add rating and position columns to users table
from sqlalchemy import create_engine, text
from config import DATABASE_URL

# Create database engine
engine = create_engine(DATABASE_URL)

# SQL to add rating column
sql_rating = text("ALTER TABLE users ADD COLUMN IF NOT EXISTS rating INTEGER;")

# SQL to add position column with enum
sql_create_enum = text("""
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'positiontype') THEN
        CREATE TYPE positiontype AS ENUM (
            'setter', 'opposite', 'middle_blocker', 'outside_hitter', 
            'defense_specialist', 'libero'
        );
    END IF;
END
$$;
""")

sql_position = text("ALTER TABLE users ADD COLUMN IF NOT EXISTS position positiontype;")

# Execute the SQL
with engine.connect() as conn:
    conn.execute(sql_rating)
    conn.execute(sql_create_enum)
    conn.execute(sql_position)
    conn.commit()
    print("Added 'rating' and 'position' columns to users table.")
