"""API routes for CEIS/CNEP integration."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.database.connection import get_db
from src.models import EmpresaImpedida
from src.services.ceis_cnep_service import CEISCNEPService


router = APIRouter(prefix="/api/v1/ceis-cnep", tags=["CEIS/CNEP"])


@router.get("/verificar/{cnpj}", response_model=dict)
async def verificar_impedimento(cnpj: str, db: Session = Depends(get_db)):
    """Check if company is restricted."""
    service = CEISCNEPService(db)
    
    try:
        resultado = await service.verificar_impedimento(cnpj)
        
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/empresas-impedidas", response_model=dict)
async def listar_empresas_impedidas(
    fonte: Optional[str] = Query(None, description="CEIS ou CNEP"),
    uf: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List restricted companies."""
    from datetime import date
    
    # Build query
    query = db.query(EmpresaImpedida)
    
    # Filter by source
    if fonte:
        query = query.filter(EmpresaImpedida.fonte == fonte.upper())
    
    # Filter by UF
    if uf:
        query = query.filter(EmpresaImpedida.uf_orgao == uf.upper())
    
    # Only active sanctions
    hoje = date.today()
    query = query.filter(
        (EmpresaImpedida.data_fim_sancao.is_(None)) | 
        (EmpresaImpedida.data_fim_sancao >= hoje)
    )
    
    # Count total
    total = query.count()
    
    # Paginate
    offset = (page - 1) * per_page
    empresas = query.order_by(EmpresaImpedida.created_at.desc()).offset(offset).limit(per_page).all()
    
    # Convert to dict
    items = []
    for empresa in empresas:
        items.append({
            'id': empresa.id,
            'cnpj': empresa.cnpj,
            'razao_social': empresa.razao_social,
            'fonte': empresa.fonte,
            'tipo_sancao': empresa.tipo_sancao,
            'data_inicio_sancao': empresa.data_inicio_sancao.isoformat() if empresa.data_inicio_sancao else None,
            'data_fim_sancao': empresa.data_fim_sancao.isoformat() if empresa.data_fim_sancao else None,
            'orgao_sancionador': empresa.orgao_sancionador,
            'uf_orgao': empresa.uf_orgao,
            'fundamentacao_legal': empresa.fundamentacao_legal
        })
    
    return {
        'items': items,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page
    }


@router.post("/atualizar-base", response_model=dict)
async def atualizar_base_ceis_cnep(db: Session = Depends(get_db)):
    """Update local database of restricted companies."""
    service = CEISCNEPService(db)
    
    try:
        await service.atualizar_base_local()
        
        return {
            'success': True,
            'message': 'Base atualizada com sucesso'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/licitacao/{licitacao_id}/verificar", response_model=dict)
async def verificar_fornecedores_licitacao(
    licitacao_id: int,
    db: Session = Depends(get_db)
):
    """Check if any supplier in the bidding is restricted."""
    service = CEISCNEPService(db)
    
    try:
        alertas = await service.verificar_fornecedores_licitacao(licitacao_id)
        
        return {
            'licitacao_id': licitacao_id,
            'total_impedimentos': len(alertas),
            'alertas': alertas
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fornecedor/{cnpj}/local", response_model=dict)
async def verificar_fornecedor_local(cnpj: str, db: Session = Depends(get_db)):
    """Check if supplier is in local database of restricted companies."""
    service = CEISCNEPService(db)
    
    impedimentos = service.verificar_fornecedor_local(cnpj)
    
    if not impedimentos:
        return {
            'cnpj': cnpj,
            'impedido': False,
            'impedimentos': []
        }
    
    return {
        'cnpj': cnpj,
        'impedido': True,
        'impedimentos': [
            {
                'fonte': imp.fonte,
                'tipo_sancao': imp.tipo_sancao,
                'data_inicio_sancao': imp.data_inicio_sancao.isoformat() if imp.data_inicio_sancao else None,
                'data_fim_sancao': imp.data_fim_sancao.isoformat() if imp.data_fim_sancao else None,
                'orgao_sancionador': imp.orgao_sancionador,
                'uf_orgao': imp.uf_orgao
            }
            for imp in impedimentos
        ]
    }


@router.get("/estatisticas", response_model=dict)
async def estatisticas_ceis_cnep(db: Session = Depends(get_db)):
    """Get CEIS/CNEP statistics."""
    from sqlalchemy import func
    from datetime import date
    
    hoje = date.today()
    
    # Total by source
    por_fonte = db.query(
        EmpresaImpedida.fonte,
        func.count(EmpresaImpedida.id).label('total')
    ).group_by(EmpresaImpedida.fonte).all()
    
    # Active sanctions
    sancoes_ativas = db.query(func.count(EmpresaImpedida.id)).filter(
        (EmpresaImpedida.data_fim_sancao.is_(None)) | 
        (EmpresaImpedida.data_fim_sancao >= hoje)
    ).scalar()
    
    # Total companies
    total_empresas = db.query(func.count(func.distinct(EmpresaImpedida.cnpj))).scalar()
    
    return {
        'total_registros': db.query(EmpresaImpedida).count(),
        'total_empresas': total_empresas,
        'sancoes_ativas': sancoes_ativas,
        'por_fonte': {item.fonte: item.total for item in por_fonte}
    }
