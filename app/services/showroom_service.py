from sqlalchemy.orm import Session

def get_showroom_by_slug(db: Session, slug: str):
    from app.models.showroom import Showroom
    return db.query(Showroom).filter(Showroom.slug == slug).first()

def get_all_showrooms(db: Session):
    from app.models.showroom import Showroom
    return db.query(Showroom).all()

def create_showroom(db: Session, data: dict):
    from app.models.showroom import Showroom
    showroom = Showroom(**data)
    db.add(showroom)
    db.commit()
    db.refresh(showroom)
    return showroom
