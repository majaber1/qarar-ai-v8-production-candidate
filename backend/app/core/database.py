from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase,sessionmaker
from app.core.config import settings
_sqlite=settings.database_url.startswith('sqlite')
engine=create_engine(
 settings.database_url,
 connect_args={'check_same_thread':False} if _sqlite else {},
 pool_pre_ping=True,
 **({} if _sqlite else {'pool_size':settings.database_pool_size,'max_overflow':settings.database_max_overflow}),
)
SessionLocal=sessionmaker(bind=engine,autoflush=False,autocommit=False)
class Base(DeclarativeBase): pass
def get_db():
 db=SessionLocal()
 try: yield db
 finally: db.close()
