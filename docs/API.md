# LAP API Documentation

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication.

## Interactive Documentation

Visit the following URLs for interactive API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Main Endpoints

### Health Check
- `GET /health` - Check API status

### Municipalities
- `GET /api/v1/municipios/` - List all municipalities
- `GET /api/v1/municipios/{codigo_ibge}` - Get municipality by IBGE code

### Biddings
- `GET /api/v1/licitacoes/` - List all biddings
- `GET /api/v1/licitacoes/{id}` - Get bidding details
- `POST /api/v1/licitacoes/search` - Search biddings
- `GET /api/v1/licitacoes/stats/count` - Count biddings

For detailed API documentation, visit http://localhost:8000/docs
