@router.post("/", response_model=schemas.MobilResponse)
def create_car(mobil: schemas.MobilCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # 1. Cek role harus showroom
    if current_user.role.lower() != "showroom":
        raise HTTPException(status_code=403, detail="Hanya showroom yang bisa input mobil")

    # 2. AMBIL SHOWROOM DARI current_user.showroom_id. BUKAN DARI FILTER
    if not current_user.showroom_id:
        raise HTTPException(status_code=404, detail="Akun ini belum terhubung ke showroom. Hubungi admin")
        
    showroom = db.query(models.Showroom).filter(models.Showroom.id == current_user.showroom_id).first()
    if not showroom:
        raise HTTPException(status_code=404, detail="Data showroom tidak ditemukan")

    # 3. Validasi wajib di backend juga
    if not mobil.nama_mobil or not mobil.merek or not mobil.harga or not mobil.foto_url_1:
        raise HTTPException(status_code=400, detail="Lengkapi Nama, Merek, Harga & Foto Cover")

    # 4. Simpan ke DB
    db_car = models.Car(
        **mobil.dict(),
        showroom_id = showroom.id,
        status = "pending"
    )
    db.add(db_car)
    db.commit()
    db.refresh(db_car)
    
    # 5. Cast ke response biar ada showroom_nama
    data = {c.name: getattr(db_car, c.name) for c in db_car.__table__.columns}
    data['showroom_nama'] = showroom.nama_showroom
    
    return schemas.MobilResponse(**data)
