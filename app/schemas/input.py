from pydantic import BaseModel

class Registration(BaseModel):
    firstName:str
    lastName:str
    password:str
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
    phoneNumber:int
class VerifyEmailOtp(BaseModel):
    email:str
    otp:str

class login(BaseModel):
    phoneNumber:int
    password:str

class PasswordRecovery(BaseModel):
    email:str

class UpdatePassword(BaseModel):
    password:str
    email:str

class ResendMobileOtp(BaseModel):
    phoneNumber:int

class ResendEmailOtp(BaseModel):
    email:str