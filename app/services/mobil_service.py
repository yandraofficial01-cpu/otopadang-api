from sqlalchemy.orm import Session

def get_mobils_by_showroom(db: Session, showroom_id: int = None):
    from app.models.mobil import Mobil
    query = db.query(Mobil)
    if showroom_id:
        query = query.filter(Mobil.showroom_id == showroom_id)
    return query.all()

def create_mobil(db: Session, data: dict, showroom_id: int):
    from app.models.mobil import Mobil
    mobil = Mobil(**data, showroom_id=showroom_id)
    db.add(mobil)
    db.commit()
    db.refresh(mobil)
    return mobil
