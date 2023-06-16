from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQL_ALCHEMY_DATABASE_URL = 'postgresql://btfmmyqn:HLZklAMpjQnHH2--N2Nj1U-11oTT3L1E@mahmud.db.elephantsql.com/btfmmyqn'

engine = create_engine(SQL_ALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
