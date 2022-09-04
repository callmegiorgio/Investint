from investint import database

__all__ = [
    'Base'
]

Base = database.mapper_registry.generate_base()