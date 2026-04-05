"""
Pacote database do Chef Delivery.

Exports de conveniência para uso rápido:

    from database import create_tables, create_session, get_session
    from database.models import Usuario, Pedido, Pagamento, ...
"""

import database.models.__all_models  # noqa: F401 – registra todos os modelos

from database.config.connection import (  # noqa: F401
    create_tables,
    create_session,
    get_session,
    get_engine,
    get_session_factory,
)
