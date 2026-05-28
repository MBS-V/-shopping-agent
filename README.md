# AI Shopping Agent

A multimodal AI shopping agent built on Google Cloud. Upload any product image and the system identifies what it is, finds similar items from a 2,638-product fashion catalogue, and returns a plain-English recommendation.

**Live demo:** https://shopping-agent-142290822636.us-central1.run.app

---

## What it does

1. Upload a product photo — shoe, shirt, watch, bag, any fashion item
2. Gemini 2.5 Flash reads the image and extracts structured attributes: category, colour, style, material, brand, confidence score
3. Text Embedding 005 converts those attributes into a vector
4. Cosine similarity search finds the top 5 matching products from the catalogue
5. A LangGraph agent runs three tools in sequence: search, price filter, recommendation
6. Results appear with real product images, prices, and a plain-English recommendation

---

## Tech stack

| Layer | Technology |
|---|---|
| Multimodal AI | Gemini 2.5 Flash |
| Embeddings | Text Embedding 005 (Vertex AI) |
| Vector Search | Cosine similarity with disk-cached index |
| Agent Orchestration | LangGraph |
| Frontend | Streamlit |
| Image Storage | Google Cloud Storage |
| Deployment | Cloud Run |
| Platform | Vertex AI (Google Cloud) |
| Language | Python 3.11 |

---

## Architecture
User uploads image
↓
Gemini 2.5 Flash — image → structured JSON attributes
↓
Text Embedding 005 — attributes → vector
↓
Cosine similarity search — 2,638 products, 143 categories
↓
LangGraph agent — search → price filter → recommend
↓
Results + recommendation

---
---

## Dataset

[Fashion Product Images Dataset](https://www.kaggle.com/datasets/paramaggarwal/fashion-product-images-dataset) — paramaggarwal, Kaggle

44,000 fashion products. I use stratified sampling — 25 products per category across 143 categories — giving 2,638 balanced products regardless of how the source CSV is sorted. Product images are hosted on Google Cloud Storage.

---

## A few decisions worth noting

**Gemini 2.5 Flash over heavier models** — Response time matters for search UX. Flash is sub-second and accurate enough for attribute extraction at a fraction of the cost.

**Similarity threshold at 0.5** — Results below 0.5 cosine similarity are dropped. Returning a backpack when the user uploaded a watch is worse than returning nothing.

**LangGraph over plain LangChain** — The agent passes state between tools: search results feed into price filtering, which feeds into the recommender. LangGraph's stateful graph handles this cleanly without passing data through function arguments manually.

**Disk-cached index** — Building embeddings for 2,638 products takes 5 minutes and costs API calls. The catalogue doesn't change between sessions, so the index is built once and saved with pickle. Subsequent loads are instant.

**Stratified sampling** — Taking the first N rows of a dataset risks heavily skewing results toward whatever categories appear first. Equal sampling per category keeps search balanced.

---

## Run locally

```bash
git clone https://github.com/MBS-V/-shopping-agent.git
cd shopping-agent
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
```

Set up `.env`:
GCP_PROJECT_ID=your-project-id
GCP_REGION=us-central1
GCS_BUCKET_NAME=your-bucket-name
GEMINI_MODEL=gemini-2.5-flash

Download `styles.csv` from the Kaggle dataset link above and place at `data/fashion-dataset/styles.csv`.

```bash
gcloud auth application-default login
gcloud config set project your-project-id
streamlit run app.py
```

First load downloads the pre-built embedding index from Google Cloud Storage (~18MB, 10-15 seconds). Cached to disk after that — subsequent loads are instant.

---

## Project structure
shopping-agent/
├── app.py                      # Streamlit frontend
├── src/
│   ├── vision/
│   │   └── extractor.py        # Gemini Vision — image → attributes
│   ├── search/
│   │   ├── catalogue.py        # Dataset loading + stratified sampling
│   │   ├── embedder.py         # Vertex AI text embeddings
│   │   └── vector_store.py     # Cosine similarity search + disk cache
│   └── agent/
│       ├── tools.py            # Search, price filter, recommendation tools
│       └── graph.py            # LangGraph agent definition
├── Dockerfile
└── requirements.txt
---
---

## What I'd add next

- Vertex AI Vector Search to handle the full 44,000 product catalogue at scale
- Conversational follow-ups: "show me this in blue" or "under Rs.2000"
- Firestore session memory for persistent search history across sessions

---

Built using [Google Cloud Skills](https://cloudskillsboost.google) labs and resources, 2026.


