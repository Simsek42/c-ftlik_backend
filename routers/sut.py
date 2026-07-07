from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import get_db

router = APIRouter(prefix="/api/sut", tags=["Süt Üretimi"])


@router.get("/ozet")
def get_sut_ozet(db: Session = Depends(get_db)):
    # Bugün veri yoksa sistem boş kalmasın diye en son veri girilen günün özetini getirir
    toplam = db.execute(text("""
        SELECT COALESCE(SUM(sut_miktari), 0) as toplam
        FROM sut_uretimi
        WHERE sut_uretim_tarihi = (SELECT MAX(sut_uretim_tarihi) FROM sut_uretimi)
    """)).fetchone()

    sagmal = db.execute(text("""
        SELECT COUNT(DISTINCT hayvanid) as sagmal_sayisi
        FROM sut_uretimi
        WHERE sut_uretim_tarihi = (SELECT MAX(sut_uretim_tarihi) FROM sut_uretimi)
    """)).fetchone()

    return {
        "bugun_toplam_litre": float(toplam.toplam) if toplam and toplam.toplam else 0.0,
        "sagmal_sayisi": sagmal.sagmal_sayisi if sagmal and sagmal.sagmal_sayisi else 0
    }


@router.get("/grafik")
def get_sut_grafik(
    gun: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    rows = db.execute(text("""
        SELECT sut_uretim_tarihi, SUM(sut_miktari) as toplam
        FROM sut_uretimi
        WHERE sut_uretim_tarihi >= DATE_SUB(CURDATE(), INTERVAL :gun DAY)
        GROUP BY sut_uretim_tarihi
        ORDER BY sut_uretim_tarihi ASC
    """), {"gun": gun}).fetchall()

    # 🚀 DÜZELTİLDİ: O hatalı normal parantez süslü parantez ile değiştirildi!
    return {
        "grafik": [
            {
                "tarih": str(row.sut_uretim_tarihi),
                "toplam": float(row.toplam)
            }
            for row in rows
        ]
    }


@router.get("/en-cok-verenler")
def get_en_cok_verenler(
    limit: int = Query(default=3, ge=1, le=20),
    db: Session = Depends(get_db)
):
    # Genel olarak en çok süt üreten inekleri başarıyla listeler
    rows = db.execute(text("""
        SELECT h.kupe_numarasi, SUM(s.sut_miktari) as toplam
        FROM sut_uretimi s
        JOIN hayvanlar h ON s.hayvanid = h.id
        GROUP BY s.hayvanid, h.kupe_numarasi
        ORDER BY toplam DESC
        LIMIT :limit
    """), {"limit": limit}).fetchall()

    return {
        "liste": [
            {
                "kupe_numarasi": row.kupe_numarasi,
                "toplam_litre": float(row.toplam)
            }
            for row in rows
        ]
    }


@router.post("/ekle")
def sut_ekle(
    hayvanid: int,
    sut_miktari: float,
    tarih: date = None,
    db: Session = Depends(get_db)
):
    if tarih is None:
        tarih = date.today()

    db.execute(text("""
        INSERT INTO sut_uretimi (sut_uretim_tarihi, hayvanid, sut_miktari)
        VALUES (:tarih, :hayvanid, :miktar)
    """), {"tarih": tarih, "hayvanid": hayvanid, "miktar": sut_miktari})
    db.commit()

    return {"mesaj": "Süt kaydı eklendi", "tarih": str(tarih)}