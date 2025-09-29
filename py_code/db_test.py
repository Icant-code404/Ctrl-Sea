from sqlalchemy import create_engine, text

# No password, trust authentication
DATABASE_URL = "postgresql+psycopg2://postgres:@localhost:5432/ARGO"
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))  # Wrap the query in text()
    print(result.all())
