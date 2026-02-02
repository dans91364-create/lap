"""API routes for governance analysis."""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.database.connection import get_db
from src.services.governanca_service import GovernancaService


router = APIRouter(prefix="/api/v1/governanca", tags=["Governança"])


@router.get("/kpis", response_model=dict)
async def kpis_governanca(
    municipio_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get governance KPIs."""
    service = GovernancaService(db)
    
    if municipio_id:
        # KPIs for specific municipality
        return {
            'municipio_id': municipio_id,
            'kpis': {
                'indice_transparencia': service.calcular_indice_transparencia(municipio_id),
                'taxa_sucesso': service.calcular_taxa_sucesso(municipio_id),
                'tempo_medio_dias': service.calcular_tempo_medio_processo(municipio_id),
                'indice_hhi': service.calcular_indice_concentracao_hhi(municipio_id),
                'participacao_meepp': service.calcular_participacao_meepp(municipio_id),
                'economia_media': service.calcular_economia_media(municipio_id)
            }
        }
    else:
        # Aggregate KPIs for all municipalities
        from src.models import Municipio
        municipios = db.query(Municipio).all()
        
        kpis_agregados = {
            'total_municipios': len(municipios),
            'kpis': []
        }
        
        for municipio in municipios:
            kpis_agregados['kpis'].append({
                'municipio_id': municipio.id,
                'municipio': municipio.municipio,
                'indice_transparencia': service.calcular_indice_transparencia(municipio.id),
                'taxa_sucesso': service.calcular_taxa_sucesso(municipio.id),
                'participacao_meepp': service.calcular_participacao_meepp(municipio.id)
            })
        
        return kpis_agregados


@router.get("/ranking", response_model=dict)
async def ranking_governanca(db: Session = Depends(get_db)):
    """Get municipality ranking by governance."""
    service = GovernancaService(db)
    
    ranking = service.gerar_ranking_municipios()
    
    return {
        'ranking': ranking,
        'total': len(ranking)
    }


@router.get("/municipio/{id}", response_model=dict)
async def governanca_municipio(
    id: int,
    periodo: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get governance details for a municipality."""
    service = GovernancaService(db)
    
    relatorio = service.gerar_relatorio_governanca(id, periodo)
    
    if not relatorio:
        raise HTTPException(status_code=404, detail="Município não encontrado")
    
    return relatorio


@router.get("/comparativo", response_model=dict)
async def comparativo_governanca(
    municipios: str = Query(..., description="Comma-separated municipality IDs"),
    db: Session = Depends(get_db)
):
    """Get comparative governance between municipalities."""
    # Parse municipality IDs
    try:
        municipio_ids = [int(id.strip()) for id in municipios.split(',')]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid municipality IDs")
    
    service = GovernancaService(db)
    
    comparativo = []
    for mun_id in municipio_ids:
        relatorio = service.gerar_relatorio_governanca(mun_id)
        if relatorio:
            comparativo.append(relatorio)
    
    return {
        'comparativo': comparativo,
        'total_municipios': len(comparativo)
    }


@router.post("/atualizar", response_model=dict)
async def atualizar_governanca(
    municipio_id: Optional[int] = None,
    periodo: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Update governance data for period."""
    service = GovernancaService(db)
    
    try:
        service.atualizar_governanca_periodo(municipio_id, periodo)
        
        return {
            'success': True,
            'municipio_id': municipio_id,
            'periodo': periodo or 'current'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/historico/{municipio_id}", response_model=dict)
async def historico_governanca(
    municipio_id: int,
    page: int = Query(1, ge=1),
    per_page: int = Query(12, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get historical governance data for a municipality."""
    from src.models import GovernancaMunicipio
    
    # Build query
    query = db.query(GovernancaMunicipio).filter(
        GovernancaMunicipio.municipio_id == municipio_id
    )
    
    # Count total
    total = query.count()
    
    # Paginate
    offset = (page - 1) * per_page
    historico = query.order_by(GovernancaMunicipio.periodo.desc()).offset(offset).limit(per_page).all()
    
    # Convert to dict
    items = []
    for h in historico:
        items.append({
            'periodo': h.periodo,
            'indice_transparencia': float(h.indice_transparencia) if h.indice_transparencia else None,
            'taxa_sucesso': float(h.taxa_sucesso) if h.taxa_sucesso else None,
            'tempo_medio_dias': h.tempo_medio_dias,
            'indice_hhi': float(h.indice_hhi) if h.indice_hhi else None,
            'participacao_meepp': float(h.participacao_meepp) if h.participacao_meepp else None,
            'economia_media': float(h.economia_media) if h.economia_media else None,
            'total_licitacoes': h.total_licitacoes,
            'valor_total': float(h.valor_total) if h.valor_total else None
        })
    
    return {
        'municipio_id': municipio_id,
        'items': items,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page
    }


@router.get("/indicadores/explicacao", response_model=dict)
async def explicacao_indicadores():
    """Get explanation of governance indicators."""
    return {
        'indicadores': {
            'indice_transparencia': {
                'nome': 'Índice de Transparência',
                'descricao': 'Mede a completude dos dados das licitações (0-100)',
                'interpretacao': 'Quanto maior, melhor. Indica que o município fornece informações completas.'
            },
            'taxa_sucesso': {
                'nome': 'Taxa de Sucesso',
                'descricao': 'Percentual de licitações concluídas vs desertadas/fracassadas',
                'interpretacao': 'Quanto maior, melhor. Indica eficiência no processo licitatório.'
            },
            'tempo_medio_dias': {
                'nome': 'Tempo Médio de Processo',
                'descricao': 'Dias médios entre publicação e homologação',
                'interpretacao': 'Quanto menor, melhor (dentro do legal). Indica agilidade processual.'
            },
            'indice_hhi': {
                'nome': 'Índice Herfindahl-Hirschman (HHI)',
                'descricao': 'Mede concentração de mercado (0-10000)',
                'interpretacao': 'Quanto menor, melhor. HHI < 1500 indica mercado competitivo, > 2500 indica alta concentração.'
            },
            'participacao_meepp': {
                'nome': 'Participação ME/EPP',
                'descricao': 'Percentual de vitórias de micro e pequenas empresas',
                'interpretacao': 'Quanto maior, melhor. Indica estímulo às pequenas empresas locais.'
            },
            'economia_media': {
                'nome': 'Economia Média',
                'descricao': 'Percentual médio de economia (valor estimado vs homologado)',
                'interpretacao': 'Positivo indica economia, negativo indica sobrepreço.'
            }
        }
    }
