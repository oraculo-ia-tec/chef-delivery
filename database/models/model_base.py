import sqlalchemy.orm
from datetime import datetime, timezone


ModelBase = sqlalchemy.orm.declarative_base()


def utcnow():
    """Retorna datetime UTC atual (compatível com Python 3.12+)."""
    return datetime.now(timezone.utc)