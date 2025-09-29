import pandas as pd
from sqlalchemy import create_engine, text  # <-- import text

# Create dummy dataset
data = {
    "id": [1, 2, 3],
    "latitude": [19.07, 18.52, 21.15],
    "longitude": [72.87, 73.85, 79.09],
    "temperature": [27.5, 28.0, 26.8]
}
df = pd.DataFrame(data)

# Create SQLAlchemy engine
engine = create_engine("postgresql+psycopg2://postgres:@localhost:5432/ARGO")

# Load dataframe to PostgreSQL
df.to_sql("dummy_argo", engine, if_exists="replace", index=False)

# Verify by querying
with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM dummy_argo"))  # <-- wrap string in text()
    for row in result:
        print(row)
