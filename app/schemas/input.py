from pydantic import BaseModel
from datetime import date
from typing import Optional

class Registration(BaseModel):
    firstName:str
    lastName:str
    phoneNumber:str
    email:str
    region:str
    locality:str
    district:str
    school:str
    classType:str
    classStream:str

class VerfiyMobileOtp(BaseModel):
    otp:int
class VerfiyMobilLogineOtp(BaseModel):
    otp:int

class VerifyEmailOtp(BaseModel):
    otp:str

class login(BaseModel):
    phoneNumber:str

class superadminlogin(BaseModel):
    email:str
    password:str

class clientlogin(BaseModel):
    email:str
    password:str

class PasswordRecovery(BaseModel):
    email:str

class UpdatePassword(BaseModel):
    password:str
    email:str


class CountUserOnEachDay(BaseModel):
    from_date: date
    to_date: date

class FilterByIdOrRegion(BaseModel):
    id: Optional[str]=None
    region: Optional[str]=None
    page :int

class CreateType(BaseModel):
    type:str

class CreateTitle(BaseModel):
    typeid:str
    Title:str

class UpdateType(BaseModel):
    id:int
    type:str

class DeleteType(BaseModel):
    id:int

class DeleteTest(BaseModel):
    id:int

class DeleteClient(BaseModel):
    id:int

class DeleteSpeciality(BaseModel):
    id:int

class CreateTypeDescription(BaseModel):
    typeid:int
    description:str

class DeleteTypeDescription(BaseModel):
    id:int

class TestComplete(BaseModel):
    mainTypeId:int
    numberOfPointsMainType:int
    additionalTypeId:int
    numberOfPointsadditionalType:int

class DeleteUniversityById(BaseModel):
    id:int

class ClientLogin(BaseModel):
    email:str
    password:str

class CareerGuidance(BaseModel):
    name:str
    phone:int
    barcode:str

class DeleteCareerGuidanceById(BaseModel):
    id:int