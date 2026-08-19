from sqlmodel import Session, select
from app.models.user import User, UserCreate
from app.core.security import get_password_hash

# La Capa de Servicios se encarga EXCLUSIVAMENTE de la lógica.
# Jamás sabe qué es una "Request" o "FastAPI". Separación absoluta.

def get_user_by_username(session: Session, username: str) -> User | None:
    statement = select(User).where(User.username == username)
    return session.exec(statement).first()

def get_user_by_id(session: Session, user_id: int) -> User | None:
    return session.get(User, user_id)

def create_user(session: Session, user_create: UserCreate) -> User:
    # 1. Transformamos el password en plano a Hash seguro (Por ley general de Ciberseguridad)
    db_obj = User(
        username=user_create.username,
        email=user_create.email,
        hashed_password=get_password_hash(user_create.password),
    )
    # 2. Guardamos en Base de datos (Commit y refresco)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj
    