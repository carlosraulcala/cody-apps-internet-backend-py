from sqlmodel import Session, select
from app.models.cart_item import CartItem, CartItemCreate, CartItemUpdate

# La Capa de Servicios se encarga EXCLUSIVAMENTE de la lógica de negocio.
# Jamás sabe qué es una "Request" o "HTTPException". Separación absoluta.

def add_item(*, session: Session, item_in: CartItemCreate) -> CartItem:
    db_item = CartItem.model_validate(item_in)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

def get_cart_by_user(*, session: Session, user_id: int, skip: int = 0, limit: int = 100) -> list[CartItem]:
    statement = select(CartItem).where(CartItem.user_id == user_id).offset(skip).limit(limit)
    return list(session.exec(statement).all())

def get_item_by_id(*, session: Session, item_id: int) -> CartItem | None:
    return session.get(CartItem, item_id)

def update_item(*, session: Session, db_item: CartItem, item_in: CartItemUpdate) -> CartItem:
    # model_dump(exclude_unset=True) ignora campos no enviados → soporta PATCH parcial
    update_data = item_in.model_dump(exclude_unset=True)
    db_item.sqlmodel_update(update_data)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

def remove_item(*, session: Session, db_item: CartItem) -> None:
    session.delete(db_item)
    session.commit()

def clear_cart(*, session: Session, user_id: int) -> int:
    """Elimina todos los items del carrito de un usuario. Retorna la cantidad eliminada."""
    items = session.exec(select(CartItem).where(CartItem.user_id == user_id)).all()
    count = len(items)
    for item in items:
        session.delete(item)
    session.commit()
    return count
