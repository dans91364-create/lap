"""API routes for report generation."""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
import logging
from pathlib import Path

from src.services.relatorio_service import relatorio_service
from src.database.connection import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/relatorios", tags=["Relatórios"])


class GerarRelatorioRequest(BaseModel):
    """Request model for generating reports."""
    tipo: str  # diario, mensal, licitacoes, fornecedores, anomalias
    formato: str  # pdf, excel
    data_inicio: Optional[str] = None
    data_fim: Optional[str] = None
    municipio_id: Optional[int] = None


@router.post("/gerar")
async def gerar_relatorio(request: GerarRelatorioRequest):
    """
    Generate a report based on specified parameters.
    
    Args:
        request: Report generation parameters
        
    Returns:
        Report metadata with download information
    """
    try:
        filepath = None
        
        if request.tipo == "diario" and request.formato == "pdf":
            # Generate daily PDF report
            data = date.fromisoformat(request.data_inicio) if request.data_inicio else date.today()
            filepath = relatorio_service.gerar_relatorio_diario_pdf(data)
            
        elif request.tipo == "licitacoes" and request.formato == "excel":
            # Generate licitacoes Excel report
            data_inicio = date.fromisoformat(request.data_inicio) if request.data_inicio else date.today()
            data_fim = date.fromisoformat(request.data_fim) if request.data_fim else date.today()
            filepath = relatorio_service.gerar_relatorio_licitacoes_excel(
                data_inicio,
                data_fim,
                request.municipio_id
            )
            
        elif request.tipo == "fornecedores" and request.formato == "excel":
            # Generate fornecedores Excel report
            filepath = relatorio_service.gerar_relatorio_fornecedores_excel()
            
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Combinação não suportada: {request.tipo} / {request.formato}"
            )
        
        if not filepath:
            raise HTTPException(
                status_code=500,
                detail="Erro ao gerar relatório"
            )
        
        # Save to database
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("""
            INSERT INTO relatorios (tipo, formato, parametros, filepath, status)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (
            request.tipo,
            request.formato,
            {
                'data_inicio': request.data_inicio,
                'data_fim': request.data_fim,
                'municipio_id': request.municipio_id
            },
            filepath,
            'concluído'
        ))
        
        relatorio_id = cursor.fetchone()[0]
        db.commit()
        cursor.close()
        
        filename = Path(filepath).name
        
        return {
            'id': relatorio_id,
            'tipo': request.tipo,
            'formato': request.formato,
            'filename': filename,
            'download_url': f"/api/v1/relatorios/download/{filename}",
            'status': 'concluído'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erro ao gerar relatório"
        )


@router.get("/download/{filename}")
async def download_relatorio(filename: str):
    """
    Download a generated report.
    
    Args:
        filename: Report filename
        
    Returns:
        File response with the report
    """
    try:
        filepath = Path("/tmp/relatorios") / filename
        
        if not filepath.exists():
            raise HTTPException(
                status_code=404,
                detail="Relatório não encontrado"
            )
        
        # Determine media type
        if filename.endswith('.pdf'):
            media_type = 'application/pdf'
        elif filename.endswith('.xlsx'):
            media_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        else:
            media_type = 'application/octet-stream'
        
        return FileResponse(
            path=str(filepath),
            media_type=media_type,
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading report: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erro ao baixar relatório"
        )


@router.get("/listar")
async def listar_relatorios(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    List generated reports.
    
    Args:
        limit: Maximum number of results
        offset: Offset for pagination
        
    Returns:
        List of reports
    """
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("""
            SELECT 
                id,
                tipo,
                formato,
                parametros,
                filepath,
                status,
                created_at
            FROM relatorios
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """, (limit, offset))
        
        rows = cursor.fetchall()
        
        cursor.execute("SELECT COUNT(*) FROM relatorios")
        total = cursor.fetchone()[0]
        
        cursor.close()
        
        relatorios = []
        for row in rows:
            filepath = Path(row[4]) if row[4] else None
            filename = filepath.name if filepath else None
            
            relatorios.append({
                'id': row[0],
                'tipo': row[1],
                'formato': row[2],
                'parametros': row[3],
                'filename': filename,
                'download_url': f"/api/v1/relatorios/download/{filename}" if filename else None,
                'status': row[5],
                'created_at': row[6].isoformat() if row[6] else None
            })
        
        return {
            'total': total,
            'relatorios': relatorios
        }
        
    except Exception as e:
        logger.error(f"Error listing reports: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erro ao listar relatórios"
        )
