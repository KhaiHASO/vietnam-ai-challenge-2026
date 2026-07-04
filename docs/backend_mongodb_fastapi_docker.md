# Backend FastAPI + MongoDB Docker Guide

Tai lieu nay dung cho vai tro Backend trong du an VAIC 2026. FastAPI la bo nao dieu phoi giua Frontend, MongoDB va AI layer. MongoDB la source of truth cho operational state theo tung domain.

## 1. Chay MongoDB va FastAPI

Tai thu muc goc repo:

```powershell
docker compose up -d mongo
docker compose up -d --build backend
```

Neu image backend da build roi:

```powershell
docker compose up -d backend
```

## 2. Kiem tra container

```powershell
docker ps
```

Ban can thay:

```txt
vaic-mongo
vietnam-ai-challenge-2026-master-backend-1
```

## 3. Test FastAPI health

```powershell
Invoke-RestMethod http://localhost:8000/api/health | ConvertTo-Json -Depth 10
```

Ket qua dung se co:

```json
{
  "success": true,
  "service": "fastapi-orchestrator",
  "storage": {
    "backend": "mongo",
    "mongo_connected": true,
    "database": "vaic2026",
    "collection": "domain_states"
  }
}
```

## 4. Test database API

```powershell
Invoke-RestMethod http://localhost:8000/api/database | ConvertTo-Json -Depth 10
```

Endpoint nay tra ve state hien tai cua active domain. Frontend dashboard dang doc endpoint nay.

## 5. Xem du lieu trong MongoDB

```powershell
docker exec vaic-mongo mongosh --quiet --eval "db.getSiblingDB('vaic2026').domain_states.find().toArray()"
```

Moi domain duoc luu thanh mot document:

```js
{
  _id: "sme",
  state: {
    wallet: {},
    services: {},
    bookings: [],
    tickets: []
  }
}
```

## 6. Chuyen domain

```powershell
Invoke-RestMethod http://localhost:8000/api/domain/switch `
  -Method Post `
  -ContentType 'application/json' `
  -Body '{"domain":"education"}'
```

Domain hop le:

```txt
sme
education
agriculture
```

## 7. Reset database cua domain hien tai

```powershell
Invoke-RestMethod http://localhost:8000/api/database/reset -Method Post
```

## 8. Bat lai RAG seed khi demo AI day du

Trong `docker-compose.yml`, backend dang co:

```yaml
- SKIP_RAG_SEED=true
```

Gia tri nay giup backend khoi dong nhanh de test MongoDB/FastAPI. Khi can demo RAG day du, doi thanh:

```yaml
- SKIP_RAG_SEED=false
```

Sau do restart backend:

```powershell
docker compose up -d --force-recreate backend
```

Lan dau co the cham vi backend tai embedding model tu Hugging Face.

## 9. Vai tro kien truc

```txt
Frontend -> FastAPI -> Orchestrator -> MongoDB
                            |
                            +-> LLM/RAG/PyTorch/HITL
```

Khong cho Frontend goi MongoDB truc tiep. LLM khong tu ghi database. FastAPI va tool layer moi la noi validate, authorize va commit thay doi vao MongoDB.
