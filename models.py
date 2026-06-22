from sqlalchemy import Column, Integer, String, Date, Text, Float, DECIMAL
from database import Base

# 1. HAYVANLAR TABLOSU
class Hayvan(Base):
    __tablename__ = "hayvanlar"

    hayvanid = Column(Integer, primary_key=True, index=True)
    dogum_tarihi = Column(Date)
    hayvan_irk = Column(String(100))
    cinsiyet = Column(String(20))
    kupe_numarasi = Column(String(50), unique=True, index=True) # Genelde küpe no String olur
    hayvan_durumu = Column(String(100))
    hayvan_konumu = Column(String(100))
    not_alani = Column("not", Text)

# 2. GELİR GİDER TABLOSU
class GelirGider(Base):
    __tablename__ = "gelir_gider"

    id = Column(Integer, primary_key=True, index=True)
    hayvanid = Column(Integer)
    kategori = Column(String(45))
    miktar = Column(Float) # 'float' yerine 'Float'
    tarih = Column(Date)

# 3. BİLDİRİM TABLOSU
class Bildirim(Base):
    __tablename__ = "bildirim"

    id = Column(Integer, primary_key=True, index=True)
    hayvanid = Column(Integer)
    mesaj = Column(String(255))
    hatirlatma_tarihi = Column(Date) # 'date' yerine 'Date'
    tarih = Column(Date)
    tamamlandi_mi = Column(String(45))

# 4. HAYVAN SAĞLIĞI TABLOSU
class HayvanSagligi(Base):
    __tablename__ = "hayvan_sagligi"

    id = Column(Integer, primary_key=True, index=True)
    hayvanid = Column(Integer)
    tedavi = Column(String(100))
    ilac = Column(String(100))
    tarih = Column(Date)
    veteriner_adi = Column(String(100))

# 5. SÜT ÜRETİMİ TABLOSU
class SutUretimi(Base):
    __tablename__ = "sut_uretimi"

    sut_id = Column(Integer, primary_key=True, index=True)
    sut_uretim_tarihi = Column(Date)
    hayvanid = Column(Integer)
    sut_miktari = Column(Float) # 'double' yerine 'Float'

# 6. ÜREME KAYDI TABLOSU
class UremeKaydi(Base):
    __tablename__ = "ureme_kaydi"

    id = Column(Integer, primary_key=True, index=True)
    hayvanid = Column(Integer)
    durum = Column(String(45)) # 'varchar' yerine 'String'
    tohumlama_tarihi = Column(Date)
    islem_tipi = Column(String(45))
    fiyat = Column(DECIMAL(10, 2)) # 'decimal' yerine 'DECIMAL'
    aciklama = Column(Text)