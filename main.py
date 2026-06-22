from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Veri tabanı bağlantı URL'ini kontrol et (Şifren ve DB adın doğru olsun)
db_url = "mysql+pymysql://root:12345678@localhost:3306/akilli_tarim"

engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Tamamen senin veri tabanındaki sütun isimlerine göre tasarlanan model:
class Hayvan(Base):
    __tablename__ = "hayvanlar"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    hayvanid = Column(Integer, index=True, nullable=True) # Eşleşme hatası vermemesi için nullable yaptık
    kupe_numarasi = Column(String(50), unique=True, index=True)
    hayvan_irk = Column(String(50))
    dogum_tarihi = Column(Date)
    cinsiyet = Column(String(10))
    hayvan_durumu = Column(String(50))
    hayvan_konumu = Column(String(50))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(title="Hayvan Takip Sistemi API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/hayvan-ekle/")
def hayvan_ekle(
    kupe_numarasi: str = Query(...),
    hayvan_irk: str = Query(...),
    dogum_tarihi: str = Query(...),
    cinsiyet: str = Query(...),
    hayvan_durumu: str = Query(...),
    hayvan_konumu: str = Query(...),
    db: Session = Depends(get_db)
):
    # Küpe numarası kontrolü
    mevcut_hayvan = db.query(Hayvan).filter(Hayvan.kupe_numarasi == kupe_numarasi).first()
    if mevcut_hayvan:
        raise HTTPException(status_code=400, detail="Bu küpe numarası zaten mevcut!")

    try:
        # Sütun isimleri birebir senin verdiğin liste ile eşleşti
        yeni_hayvan = Hayvan(
            kupe_numarasi=kupe_numarasi,
            hayvan_irk=hayvan_irk,
            dogum_tarihi=dogum_tarihi,
            cinsiyet=cinsiyet,
            hayvan_durumu=hayvan_durumu,
            hayvan_konumu=hayvan_konumu
        )
        
        db.add(yeni_hayvan)
        db.commit() # Diske kalıcı yazma
        db.refresh(yeni_hayvan)
        
        return {"status": "success", "message": "Hayvan başarıyla eklendi."}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Hata: {str(e)}")

@app.get("/hayvanlar/")
def hayvanlari_listele(db: Session = Depends(get_db)):
    return db.query(Hayvan).all()