from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ÖNEMLİ: 'root:sifre' kısmını kendi MySQL kullanıcı adın ve şifrenle değiştir.
# Veritabanı adının MySQL'de 'hayvan_takip' olduğundan emin ol.
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:12345678@localhost:3305/akilli_tarim" 

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Veritabanı bağlantısı açıp kapatan yardımcı fonksiyon
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()