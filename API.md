# LAP - Documentação da API

## Base URL

```
http://localhost:8000/api/v1
```

## Autenticação

Atualmente a API não requer autenticação. Para produção, recomenda-se implementar OAuth2 ou JWT.

## Endpoints

### 📊 Estatísticas

#### GET /estatisticas/kpis

Retorna os principais indicadores do dashboard.

**Query Parameters:**
- `data_inicio` (opcional): Data início (ISO 8601)
- `data_fim` (opcional): Data fim (ISO 8601)
- `municipio_id` (opcional): ID do município

**Response:**
```json
{
  "total_licitacoes": 1250,
  "licitacoes_abertas": 35,
  "valor_total_estimado": 45678900.50,
  "valor_total_homologado": 42345600.25,
  "economia_gerada": {
    "valor": 3333300.25,
    "percentual": 7.3
  },
  "alertas_pendentes": 12,
  "anomalias_detectadas": 8
}
```

#### GET /estatisticas/por-mes

Retorna contagem de licitações por mês.

**Query Parameters:**
- `meses` (opcional, padrão: 12): Quantidade de meses

**Response:**
```json
{
  "meses": 12,
  "series": [
    {
      "periodo": "2024-01",
      "total": 45,
      "valor_total": 2500000.00
    }
  ]
}
```

---

### 📄 Licitações

#### GET /licitacoes/

Lista licitações com paginação.

**Query Parameters:**
- `page` (padrão: 1)
- `per_page` (padrão: 20, máx: 100)
- `search` (opcional): Busca por texto

**Response:**
```json
{
  "items": [...],
  "total": 1250,
  "page": 1,
  "per_page": 20,
  "pages": 63
}
```

#### GET /licitacoes/{id}

Retorna detalhes de uma licitação específica.

**Response:**
```json
{
  "id": 123,
  "numero_compra": "00001/2024",
  "objeto_compra": "Aquisição de material de escritório",
  "modalidade_nome": "Pregão Eletrônico",
  "valor_total_estimado": 50000.00,
  "data_publicacao_pncp": "2024-01-15T10:00:00",
  ...
}
```

---

### 🚨 Anomalias

#### GET /anomalias/

Lista anomalias detectadas.

**Query Parameters:**
- `tipo` (opcional): Tipo da anomalia
- `status` (opcional): pendente, analisada, descartada
- `municipio_id` (opcional)
- `page`, `per_page`

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "tipo": "PRECO_ACIMA_MEDIA",
      "descricao": "Preço 50% acima da média",
      "score_risco": 70.5,
      "percentual_desvio": 50.2,
      "status": "pendente"
    }
  ],
  "total": 45
}
```

#### POST /anomalias/executar-analise

Executa análise de anomalias manualmente.

**Request Body:**
```json
{
  "licitacao_id": 123  // opcional
}
```

**Response:**
```json
{
  "success": true,
  "total_anomalias_detectadas": 5,
  "anomalias": [...]
}
```

#### PUT /anomalias/{id}/status

Atualiza status de uma anomalia.

**Request Body:**
```json
{
  "status": "analisada",
  "observacoes": "Justificativa verificada",
  "analisado_por": "João Silva"
}
```

---

### 🔔 Alertas

#### GET /alertas/configuracoes

Lista configurações de alertas.

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "nome": "Licitações de TI",
      "ativo": true,
      "tipo": "palavra_chave",
      "palavras_chave": ["software", "computador"],
      "canal_notificacao": "email",
      "destinatario": "usuario@example.com"
    }
  ]
}
```

#### POST /alertas/configuracoes

Cria nova configuração de alerta.

**Request Body:**
```json
{
  "nome": "Licitações de TI",
  "ativo": true,
  "tipo": "palavra_chave",
  "palavras_chave": ["software", "computador"],
  "municipios": [1, 2, 3],
  "modalidades": ["Pregão Eletrônico"],
  "valor_minimo": 10000.00,
  "valor_maximo": 100000.00,
  "canal_notificacao": "email",
  "destinatario": "usuario@example.com"
}
```

---

### 🏆 Governança

#### GET /governanca/ranking

Retorna ranking de municípios por score de governança.

**Response:**
```json
{
  "ranking": [
    {
      "municipio_id": 1,
      "municipio": "Goiânia",
      "uf": "GO",
      "score_governanca": 85.5,
      "indice_transparencia": 90.0,
      "taxa_sucesso": 95.0,
      "participacao_meepp": 35.0,
      "economia_media": 8.5
    }
  ]
}
```

#### GET /governanca/municipio/{id}

Retorna relatório completo de governança de um município.

**Query Parameters:**
- `periodo` (opcional): YYYY-MM

**Response:**
```json
{
  "municipio": {
    "id": 1,
    "nome": "Goiânia",
    "uf": "GO"
  },
  "kpis": {
    "indice_transparencia": 90.0,
    "taxa_sucesso": 95.0,
    "tempo_medio_dias": 45,
    "indice_hhi": 1200.5,
    "participacao_meepp": 35.0,
    "economia_media": 8.5
  },
  "score_governanca": 85.5
}
```

---

### ⚠️ CEIS/CNEP

#### GET /ceis-cnep/verificar/{cnpj}

Verifica se empresa está impedida.

**Response:**
```json
{
  "cnpj": "12345678000190",
  "impedido": true,
  "ceis": {...},
  "cnep": null,
  "detalhes": [...]
}
```

#### GET /ceis-cnep/empresas-impedidas

Lista empresas impedidas.

**Query Parameters:**
- `fonte` (opcional): CEIS ou CNEP
- `uf` (opcional): UF do órgão sancionador

---

### 💰 Preços

#### GET /precos/estatisticas

Retorna estatísticas de preço de um item.

**Query Parameters:**
- `descricao` (obrigatório): Descrição do item
- `periodo_meses` (opcional, padrão: 24)

**Response:**
```json
{
  "descricao": "Notebook",
  "total_registros": 150,
  "estatisticas": {
    "media": 2500.00,
    "mediana": 2450.00,
    "desvio_padrao": 350.00,
    "minimo": 1800.00,
    "maximo": 4200.00,
    "q1": 2200.00,
    "q3": 2800.00
  }
}
```

#### GET /precos/sugestao

Sugere preço de referência para um item.

**Query Parameters:**
- `descricao` (obrigatório)

**Response:**
```json
{
  "descricao": "Notebook",
  "preco_sugerido": 2450.00,
  "intervalo_confianca": {
    "minimo": 2100.00,
    "maximo": 2800.00
  },
  "total_registros": 150
}
```

#### GET /precos/benchmark

Compara preços entre municípios.

**Response:**
```json
{
  "descricao": "Notebook",
  "media_geral": 2500.00,
  "benchmark": [
    {
      "municipio_id": 1,
      "preco_medio": 2300.00,
      "total_itens": 45,
      "diferenca_media_geral": -8.0
    }
  ]
}
```

## Códigos de Status

- `200` - OK
- `201` - Created
- `400` - Bad Request
- `404` - Not Found
- `500` - Internal Server Error

## Rate Limiting

Atualmente não há limite de requisições. Para produção, recomenda-se implementar rate limiting.

## Paginação

Endpoints que retornam listas usam paginação padrão:

```json
{
  "items": [...],
  "total": 1000,
  "page": 1,
  "per_page": 20,
  "pages": 50
}
```

## Filtros de Data

Datas devem estar no formato ISO 8601:
- `2024-01-15` (data)
- `2024-01-15T10:30:00` (data e hora)

## Exemplos de Uso

### Python

```python
import requests

# Obter KPIs
response = requests.get('http://localhost:8000/api/v1/estatisticas/kpis')
kpis = response.json()
print(f"Total de licitações: {kpis['total_licitacoes']}")
```

### JavaScript

```javascript
// Listar licitações
fetch('http://localhost:8000/api/v1/licitacoes/')
  .then(response => response.json())
  .then(data => console.log(data.items));
```

### cURL

```bash
# Executar análise de anomalias
curl -X POST http://localhost:8000/api/v1/anomalias/executar-analise \
  -H "Content-Type: application/json" \
  -d '{"licitacao_id": 123}'
```
