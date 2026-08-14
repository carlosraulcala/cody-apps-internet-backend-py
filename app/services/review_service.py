from sqlmodel import Session, select
from app.models.review import Review, ReviewCreate

# La Capa de Servicios se encarga EXCLUSIVAMENTE de la lógica de negocio.
# Jamás sabe qué es una "Request" o "HTTPException". Separación absoluta.

def create_review(*, session: Session, review_in: ReviewCreate) -> Review:
    db_item = Review.model_validate(review_in)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

def get_reviews(*, session: Session, skip: int = 0, limit: int = 100) -> list[Review]:
    statement = select(Review).offset(skip).limit(limit)
    return list(session.exec(statement).all())

def get_reviews_by_product(*, session: Session, product_id: int, skip: int = 0, limit: int = 100) -> list[Review]:
    statement = select(Review).where(Review.product_id == product_id).offset(skip).limit(limit)
    return list(session.exec(statement).all())

def get_review_by_id(*, session: Session, review_id: int) -> Review | None:
    return session.get(Review, review_id)

def delete_review(*, session: Session, db_item: Review) -> None:
    session.delete(db_item)
    session.commit()
