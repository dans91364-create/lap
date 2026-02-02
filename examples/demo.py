#!/usr/bin/env python
"""Example script demonstrating LAP usage."""

import asyncio
from src.services.coleta_service import ColetaService
from src.database.connection import init_db, get_db_context
from src.database.repositories import MunicipioRepository, LicitacaoRepository


async def main():
    """Run example workflow."""
    print("=" * 60)
    print("LAP - Example Script")
    print("=" * 60)
    
    # Initialize database
    print("\n1. Initializing database...")
    init_db()
    print("   ✓ Database initialized")
    
    # Load municipalities
    print("\n2. Loading municipalities...")
    service = ColetaService()
    count = await service.load_municipios_from_config()
    print(f"   ✓ Loaded {count} municipalities")
    
    # List municipalities
    print("\n3. Listing municipalities...")
    with get_db_context() as db:
        repo = MunicipioRepository(db)
        municipios = repo.get_all()
        print(f"   Total: {len(municipios)}")
        for m in municipios[:5]:
            print(f"   - {m.municipio} ({m.codigo_ibge})")
    
    print("\n" + "=" * 60)
    print("Example completed! Use 'python manage.py --help' for more commands")


if __name__ == "__main__":
    asyncio.run(main())
