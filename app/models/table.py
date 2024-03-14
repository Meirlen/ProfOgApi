from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float,Text,BIGINT,ARRAY,JSON
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text

from .. config.database import Base

class Registration(Base):
    __tablename__ = "registration"
    id = Column(Integer, primary_key=True, nullable=False)
    firstname = Column(String,nullable=False)
    lastname = Column(String,nullable=False)
    phonenumber = Column(String,nullable=False)
    email= Column(String,nullable=False)
    region = Column(String,nullable=True)
    locality = Column(String,nullable=True)
    district = Column(String,nullable=True)
    school = Column(String,nullable=True)
    classtype = Column(String,nullable=True)
    classstream = Column(String,nullable=True)
    test = Column(String,nullable=True)
    university = Column(String,nullable=True)
    speciality = Column(String,nullable=True)
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

class Speciality(Base):
    __tablename__ = "speciality"
    id = Column(Integer, primary_key=True, nullable=False)
    specialtyname = Column(String, nullable=True)
    typeid= Column(Integer, nullable=False)
    photos = Column(String, nullable=True)
    barcode=Column(String ,nullable=False)
    hardskills= Column(ARRAY(String), nullable=False)
    softskills = Column(ARRAY(String), nullable=False)
    description=Column(String,nullable=False)
    about=Column(String,nullable=False)
    language=Column(String,nullable=False)
    videos = Column(String, nullable=True)
    partners=Column(String,nullable=True)
    averagesalary=Column(Integer,nullable=False)
    
class University(Base):
    __tablename__ = "university"
    id = Column(Integer, primary_key=True, nullable=False)
    universityname = Column(String, nullable=True)
    photos = Column(String, nullable=True)
    city=Column(String ,nullable=False)
    description=Column(String,nullable=False)
    about=Column(String,nullable=False)
    language=Column(String,nullable=False)
    videos = Column(String, nullable=True)
    partners=Column(String,nullable=True)
    universityid = Column(String, nullable=True)
    classification = Column(String, nullable=True)
    speciality = Column(String, nullable=True)
    region = Column(String, nullable=True)


class Client(Base):
    __tablename__ = "client"
    id = Column(Integer, primary_key=True, nullable=False)
    photos = Column(String, nullable=True)
    bin=Column(String ,nullable=False)
    email=Column(String,nullable=False)
    reservephone=Column(String,nullable=False)
    password=Column(String,nullable=False)
    universityid=Column(String ,nullable=False)

class SuperAdmin(Base):
    __tablename__ = "superadmin"
    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    
class StoringTestForUser(Base):
    __tablename__ ="storingtestforuser"
    id = Column(Integer, primary_key=True, nullable=False)
    phonenumber = Column(String, nullable=False)
    token = Column(String, nullable=False)
    question = Column(String, nullable=False)

class TypeDescription(Base):
    __tablename__ ="typedescription"
    id = Column(Integer, primary_key=True, nullable=False)
    typeid = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    lang = Column(String, nullable=False)

class TestComplete(Base):
    __tablename__ ="testcomplete"
    id = Column(Integer, primary_key=True, nullable=False)
    phone_number = Column(BIGINT, nullable=False)
    maintypeid = Column(Integer, nullable=False)
    numberofpointsmaintype = Column(Integer, nullable=False)
    additionaltypeid = Column(Integer, nullable=False)
    numberofpointsadditionaltype = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    
class SelectedSpecialities(Base):
    __tablename__ ="selectedspecialities"
    id = Column(Integer, primary_key=True, nullable=False)
    phone_number = Column(BIGINT, nullable=False)
    selectedspecialities = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False)
    
class SelectedUniversity(Base):
    __tablename__ ="selecteduniversity"
    id = Column(Integer, primary_key=True, nullable=False)
    phone_number = Column(BIGINT, nullable=False)
    selecteduniversity = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False)