from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float,Text,BIGINT
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text

from .. config.database import Base

class Registration(Base):
    __tablename__ = "registration"
    id = Column(Integer, primary_key=True, nullable=False)
    firstname = Column(String,nullable=False)
    lastname = Column(String,nullable=False)
    password = Column(String,nullable=False)
    phonenumber = Column(String,nullable=False)
    email= Column(String,nullable=False)
    region = Column(String,nullable=True)
    locality = Column(String,nullable=True)
    district = Column(String,nullable=True)
    school = Column(String,nullable=True)
    classtype = Column(String,nullable=True)
    classstream = Column(String,nullable=True)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()')) 

class MobileOtp(Base):
    __tablename__ = "mobile_otps"
    id = Column(Integer, primary_key=True, nullable=False)
    phone_number = Column(BIGINT, nullable=False)
    code = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))  

class EmailOtp(Base):
    __tablename__ = "email_otps"
    id = Column(Integer, primary_key=True, nullable=False)
    email_id = Column(String, nullable=False)
    code = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))  
    
class Type(Base):
    __tablename__ = "type"
    id = Column(Integer, primary_key=True, nullable=False)
    type = Column(String, nullable=False)

class Test(Base):
    __tablename__ = "test"
    id = Column(Integer, primary_key=True, nullable=False)
    typeid= Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    language=Column(String,nullable=False)