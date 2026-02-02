#!/usr/bin/env python
"""CLI script for LAP management tasks."""

import asyncio
import sys
import logging
from typing import Optional

import click

from src.services.coleta_service import ColetaService
from src.database.connection import init_db

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@click.group()
def cli():
    """LAP - Licitações Aparecida Plus CLI"""
    pass


@cli.command()
def init():
    """Initialize database."""
    try:
        click.echo("Initializing database...")
        init_db()
        click.echo("✓ Database initialized successfully!")
    except Exception as e:
        click.echo(f"✗ Error initializing database: {e}", err=True)
        sys.exit(1)


@cli.command()
def load_municipios():
    """Load municipalities from config file."""
    async def _load():
        service = ColetaService()
        count = await service.load_municipios_from_config()
        return count
    
    try:
        click.echo("Loading municipalities from config...")
        count = asyncio.run(_load())
        click.echo(f"✓ Loaded {count} municipalities!")
    except Exception as e:
        click.echo(f"✗ Error loading municipalities: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--municipio', '-m', help='Municipality IBGE code')
@click.option('--years', '-y', default=2, help='Number of years to collect')
def collect(municipio: Optional[str], years: int):
    """Collect bidding data."""
    async def _collect():
        service = ColetaService()
        
        if municipio:
            click.echo(f"Collecting data for municipality {municipio}...")
            count = await service.collect_licitacoes_for_municipio(municipio, years)
            click.echo(f"✓ Collected {count} biddings!")
        else:
            click.echo("Collecting data for all municipalities...")
            stats = await service.collect_all_municipios(years)
            click.echo(f"✓ Collection complete!")
            click.echo(f"  - Municipalities: {stats['total_municipios']}")
            click.echo(f"  - Biddings: {stats['total_licitacoes']}")
            click.echo(f"  - Errors: {stats['errors']}")
    
    try:
        asyncio.run(_collect())
    except Exception as e:
        click.echo(f"✗ Error collecting data: {e}", err=True)
        sys.exit(1)


@cli.command()
def run_api():
    """Run the API server."""
    import uvicorn
    from config.settings import settings
    
    click.echo(f"Starting API server on {settings.API_HOST}:{settings.API_PORT}...")
    uvicorn.run(
        "src.api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )


@cli.command()
def status():
    """Show system status."""
    from src.database.connection import get_db_context
    from src.database.repositories import (
        MunicipioRepository,
        LicitacaoRepository,
        FornecedorRepository
    )
    
    try:
        with get_db_context() as db:
            municipio_repo = MunicipioRepository(db)
            licitacao_repo = LicitacaoRepository(db)
            fornecedor_repo = FornecedorRepository(db)
            
            municipios_count = len(municipio_repo.get_all())
            licitacoes_count = licitacao_repo.count()
            fornecedores_count = fornecedor_repo.count()
            
            click.echo("=== LAP System Status ===")
            click.echo(f"Municipalities: {municipios_count}")
            click.echo(f"Biddings: {licitacoes_count}")
            click.echo(f"Suppliers: {fornecedores_count}")
    except Exception as e:
        click.echo(f"✗ Error getting status: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()
