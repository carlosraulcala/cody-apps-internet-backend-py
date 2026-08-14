from sqlmodel import Session, select
from app.models.product import Product, ProductCreate, ProductUpdate

# La Capa de Servicios se encarga EXCLUSIVAMENTE de la lógica de negocio.
# Jamás sabe qué es una "Request" o "HTTPException". Separación absoluta.

def create_product(*, session: Session, product_in: ProductCreate) -> Product:
    db_item = Product.model_validate(product_in)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

def get_products(*, session: Session, skip: int = 0, limit: int = 100) -> list[Product]:
    statement = select(Product).offset(skip).limit(limit)
    return list(session.exec(statement).all())

def get_product_by_id(*, session: Session, product_id: int) -> Product | None:
    return session.get(Product, product_id)

def update_product(*, session: Session, db_item: Product, product_in: ProductUpdate) -> Product:
    # model_dump(exclude_unset=True) ignora campos no enviados → soporta PATCH parcial
    update_data = product_in.model_dump(exclude_unset=True)
    db_item.sqlmodel_update(update_data)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

def delete_product(*, session: Session, db_item: Product) -> None:
    session.delete(db_item)
    session.commit()
