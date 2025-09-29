# demo.py
from project_repo.py_code.floatchat_agents.sql_agent import run_template
from retriever import ingest_dataframe, query_text
import pandas as pd

# SQL Agent demo
rows = run_template("latest_floats", {"limit": 5})
print("SQL Agent result:", rows)

# Retriever Agent demo
df = pd.DataFrame({"id": [1,2], "text": ["Argo floats measure salinity.", "They also record ocean temperature."]})
ingest_dataframe(df)
print("Retriever result:", query_text("What do floats measure?", n=2))
