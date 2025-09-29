import pandas as pd
from sqlalchemy import create_engine
from sentence_transformers import SentenceTransformer
import chromadb

# -------------------------------
# Config
# -------------------------------
DB_NAME = "postgres"
TABLE_NAME = "argo_data"
DB_USER = "postgres"
DB_PASSWORD = ""
DB_HOST = "localhost"
DB_PORT = 5432
SAMPLE_LIMIT = 5000   # adjust if you want more/less

CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "argo_meta"
EMBED_MODEL = "all-MiniLM-L6-v2"   # small + free model

# -------------------------------
# Step 1. Load data from Postgres
# -------------------------------
engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

print(f"🔄 Connecting to Postgres ({DB_NAME}) and reading rows...")
with engine.connect() as conn:
    df = pd.read_sql(
        f'SELECT "TEMP","PSAL","LATITUDE","LONGITUDE","JULD" FROM {TABLE_NAME} LIMIT {SAMPLE_LIMIT}',
        conn,
    )

print(f"✅ Loaded {len(df)} rows")

# -------------------------------
# Step 2. Convert rows -> text docs
# -------------------------------
# Step 2. Convert rows -> text docs
docs, ids, metadatas = [], [], []

for i, row in df.iterrows():
    # Convert all metadata values to primitives (str/int/float/bool)
    meta = {k: (str(v) if hasattr(v, "isoformat") else v) for k, v in row.to_dict().items()}
    text = (
        f"Temperature {row['TEMP']}, Salinity {row['PSAL']}, "
        f"Latitude {row['LATITUDE']}, Longitude {row['LONGITUDE']}, Date {row['JULD']}"
    )
    docs.append(text)
    ids.append(str(i))
    metadatas.append(meta)


print(f"📝 Prepared {len(docs)} text docs")

# -------------------------------
# Step 3. Generate embeddings
# -------------------------------
print(f"🔄 Loading embedding model: {EMBED_MODEL}")
model = SentenceTransformer(EMBED_MODEL)

print("⚡ Generating embeddings (this may take a minute)...")
embeddings = model.encode(docs, show_progress_bar=True).tolist()

# -------------------------------
# Step 4. Store in Chroma
# -------------------------------
print(f"📦 Storing in Chroma at {CHROMA_PATH} ...")
client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection(COLLECTION_NAME)

# clear old stuff if re-running
if collection.count() > 0:
    print("⚠️ Clearing existing collection first")
    collection.delete(ids=collection.get()["ids"])

collection.add(
    documents=docs,
    embeddings=embeddings,
    ids=ids,
    metadatas=metadatas,
)

print(f"✅ Done. Stored {collection.count()} embeddings in collection '{COLLECTION_NAME}'")