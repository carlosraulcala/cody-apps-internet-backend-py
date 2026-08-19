from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from app.api.deps import SessionDep, CurrentUser
from app.core.security import verify_password, create_access_token
from app.models.user import UserCreate, UserPublic
from app.services import user_service

router = APIRouter()

# Schema nativo de FastAPI par JWT (Para la respuesta)
class Token(UserPublic):
    access_token: str   
    token_type: str = "bearer"

@router.post("/login", response_model=Token)
def login_access_token(
    session: SessionDep, 
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """OAuth2 compatible token login."""
    # 1. Buscamos al usuario en SQLite delegando al servicio
    user = user_service.get_user_by_username(session=session, username=form_data.username)
    
    # 2. Re-encriptamos su envío y lo macheamos 
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Usuario o Contraseña incorrecto")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
        
    # 3. Todo bien. Emite el Pase de Visita firmado
    access_token_expires = None # Usa el tiempo por defecto del .env
    token = create_access_token(subject=user.id, expires_delta=access_token_expires)
    
    # Nota: También enviamos de vuelta todo el Objeto Usuario (UserPublic)
    return Token(access_token=token, id=user.id, email=user.email, username=user.username, is_active=user.is_active)


@router.post("/register", response_model=UserPublic)
def register_user(session: SessionDep, user_in: UserCreate) -> UserPublic:
    """Registra nuevo usuario."""
    # Valida duplicados
    if user_service.get_user_by_username(session, user_in.username):
        raise HTTPException(status_code=400, detail="El username ya está ocupado")
    
    return user_service.create_user(session, user_in)


@router.get("/me", response_model=UserPublic)
def read_perfil_mio(current_user: CurrentUser) -> UserPublic:
    """RUTA PROTEGIDA: Solo devuelve mis datos si poseo un JWT firmado legal."""
    # FastAPI hizo tooooda la magia de decodificar y cruzar con la BD al ver 'CurrentUser'
    return current_user
