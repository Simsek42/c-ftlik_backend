from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import get_db

router = APIRouter(prefix="/api/ureme", tags=["Üreme Takibi"])


@router.get("/ozet")
def get_ureme_ozet(db: Session = Depends(get_db)):
    # ureme_kaydi tablosundaki durumlara göre sayıları alıyoruz
    gebe = db.execute(text("SELECT COUNT(*) FROM ureme_kaydi WHERE durum = 'Gebe'")).scalar() or 0
    tohumlu = db.execute(text("SELECT COUNT(*) FROM ureme_kaydi WHERE durum = 'Tohumlu'")).scalar() or 0
    sorunlu = db.execute(text("SELECT COUNT(*) FROM ureme_kaydi WHERE durum = 'Sorunlu'")).scalar() or 0
    
    return {
        "gebe_sayisi": gebe,
        "tohumlu_sayisi": tohumlu,
        "sorunlu_sayisi": sorunlu
    }


@router.get("/grafik")
def get_gebelik_grafik(db: Session = Depends(get_db)):
    # tohumlama_tarihi ile bugün arasındaki ay farkını buluyoruz
    rows = db.execute(text("""
        SELECT TIMESTAMPDIFF(MONTH, tohumlama_tarihi, CURDATE()) as ay_farki, COUNT(*) as miktar
        FROM ureme_kaydi 
        WHERE durum = 'Gebe' AND tohumlama_tarihi IS NOT NULL
        GROUP BY ay_farki
    """)).fetchall()
    
    grafik_data = {"1-3": 0, "4-6": 0, "7": 0, "8": 0, "9": 0}
    for row in rows:
        ay = row.ay_farki
        if 1 <= ay <= 3:
            grafik_data["1-3"] += row.miktar
        elif 4 <= ay <= 6:
            grafik_data["4-6"] += row.miktar
        elif ay == 7:
            grafik_data["7"] += row.miktar
        elif ay == 8:
            grafik_data["8"] += row.miktar
        elif ay >= 9:
            grafik_data["9"] += row.miktar

    return {"bar_grafik": [{"grup": k, "miktar": v} for k, v in grafik_data.items()]}


@router.get("/yaklasan-dogumlar")
def get_yaklasan_dogumlar(db: Session = Depends(get_db)):
    # 280 gün gebelik süresine göre doğuma 30 gün ve daha az kalan inekleri getirir
    # Küpe numarasını çekebilmek için 'hayvanlar' tablosuyla JOIN yapıyoruz
    rows = db.execute(text("""
        SELECT h.kupe_numarasi, 
               DATEDIFF(DATE_ADD(u.tohumlama_tarihi, INTERVAL 280 DAY), CURDATE()) as kalan_gun
        FROM ureme_kaydi u
        JOIN hayvanlar h ON u.hayvanid = h.id
        WHERE u.durum = 'Gebe' AND u.tohumlama_tarihi IS NOT NULL
        HAVING kalan_gun BETWEEN 0 AND 30
        ORDER BY kalan_gun ASC
    """)).fetchall()
    
    return {"liste": [{"kupe_numarasi": r.kupe_numarasi, "kalan_gun": r.kalan_gun} for r in rows]}


@router.get("/yaklasan-ilaclar")
def get_yaklasan_ilaclar(db: Session = Depends(get_db)):
    # hayvan_sagligi tablosunda tarihi bugünden ileri olan (gelecekteki) ilaç/aşı/tedavi planlarını getirir
    rows = db.execute(text("""
        SELECT h.kupe_numarasi, hs.ilac as detay, DATEDIFF(hs.tarih, CURDATE()) as kalan_gun
        FROM hayvan_sagligi hs
        JOIN hayvanlar h ON hs.hayvanid = h.id
        WHERE hs.tarih >= CURDATE()
        ORDER BY hs.tarih ASC
        LIMIT 10
    """)).fetchall()
    
    return {"liste": [{"kupe_numarasi": r.kupe_numarasi, "detay": r.detay, "kalan_gun": r.kalan_gun} for r in rows]}