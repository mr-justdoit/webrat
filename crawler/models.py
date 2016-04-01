from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Page(Base):
    __tablename__ = 'page'
    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True)

class Content(Base):
    __tablename__ = 'content'
    id = Column(Integer, primary_key=True)
    page_id = Column(Integer, ForeignKey('page.id'))
    html = Column(String, unique=True)
    page = relationship(Page)


engine = create_engine('sqlite:///web.db')
Base.metadata.create_all(engine)
