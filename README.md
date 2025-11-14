# BangalorePropAI - Minimal

## Prepare
Place your files:
- data/bangalore_home_prices_model.pickle
- data/columns.json

## Run with Docker Compose
docker compose up --build

Frontend available via static serve or use the built static files served by FastAPI if you wire them.

## API
GET /api/metadata
POST /api/predict  (json body)
GET /healthz (X-API-KEY header required)
POST /admin/upload (X-API-KEY header required, multipart form)

Examples:
curl http://localhost:8000/api/metadata

curl -X POST http://localhost:8000/api/predict -H "Content-Type: application/json" -d '{"total_sqft":1000,"bhk":2,"bath":2,"location":"hsr layout"}'

curl -X POST http://localhost:8000/admin/upload -H "X-API-KEY: changeme" -F "model_file=@./data/bangalore_home_prices_model.pickle" -F "columns_file=@./data/columns.json"
