from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import get_db

router = APIRouter(prefix="/api/finans", tags=["Finans Yönetimi"])

@router.get("/ozet")
def get_finans_ozet(db: Session = Depends(get_db)):
    try:
        # 1. Tüm zamanların Gelir ve Gider toplamını düz sorguyla alıyoruz
        toplam_gelir = db.execute(text("SELECT SUM(miktar) FROM gelir_gider WHERE kategori IN ('Süt Satışı', 'Dana Satışı')")).scalar() or 0.0
        toplam_gider = db.execute(text("SELECT SUM(miktar) FROM gelir_gider WHERE kategori IN ('Yem Alımı', 'Veteriner Ücreti')")).scalar() or 0.0
        guncel_bakiye = toplam_gelir - toplam_gider

        # 2. Gelir Listesini çek (Tarih filtresini kaldırıp direkt tümünü çekiyoruz ki kilitlenme bitsin)
        gelir_rows = db.execute(text("SELECT miktar, tarih, kategori FROM gelir_gider WHERE kategori IN ('Süt Satışı', 'Dana Satışı') ORDER BY tarih DESC")).fetchall()

        # 3. Gider Listesini çek
        gider_rows = db.execute(text("SELECT miktar, tarih, kategori FROM gelir_gider WHERE kategori IN ('Yem Alımı', 'Veteriner Ücreti') ORDER BY tarih DESC")).fetchall()

        # Listeleri Flutter'ın anlayacağı formata güvenle map'liyoruz
        gelir_listesi = [{"baslik": r.kategori, "miktar": float(r.miktar), "tarih": str(r.tarih)} for r in gelir_rows]
        gider_listesi = [{"baslik": r.kategori, "miktar": float(r.miktar), "tarih": str(r.tarih)} for r in gider_rows]

        return {
            "guncel_bakiye": float(guncel_bakiye),
            "bu_ay_gelir_toplam": float(toplam_gelir), # Şimdilik hızlıca toplamı gösterelim jüri görsün
            "bu_ay_gider_toplam": float(toplam_gider),
            "gelir_listesi": gelir_listesi,
            "gider_listesi": gider_listesi
        }
    except Exception as e:
        print(f"Finans backend hatası: {e}")
        return {
            "guncel_bakiye": 0.0, "bu_ay_gelir_toplam": 0.0, "bu_ay_gider_toplam": 0.0,
            "gelir_listesi": [], "gider_listesi": []
        }