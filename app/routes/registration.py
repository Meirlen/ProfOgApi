from fastapi import APIRouter,Response,Depends,BackgroundTasks,status,HTTPException
from sqlalchemy.orm import Session
from .. config import database as database
from .. schemas import input
from .. models import table
import random
import string
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from .. utils.sendmail import *
from .. utils.sendsms import *


router = APIRouter(tags=['Login'])

#
@router.post("/registration" )
async def registration (param: input.Registration,background_tasks: BackgroundTasks,db: Session = Depends(database.get_db)):
    user = db.query(table.Registration).filter(table.Registration.phonenumber == param.phoneNumber).first()
    if not user:
        phone_otp = str(random.randint(100000,999999))
        characters = string.ascii_letters + string.digits 
        email_otp = ''.join(random.choice(characters) for i in range(6))
        print (phone_otp,email_otp)
        phone_otp = table.MobileOtp(phone_number=param.phoneNumber,code=phone_otp)
        email_otp = table.EmailOtp(email_id=param.email,code=email_otp)
        db.add(phone_otp)
        db.commit()
        db.add(email_otp)
        db.commit()
        background_tasks.add_task(send_in_background,email_otp,{param.email},background_tasks)
        background_tasks.add_task(send_sms,phone_otp,{param.phoneNumber})
        query=f'''INSERT INTO registration (firstName,lastName,password,phoneNumber,email,region,locality,district,school,classType,classStream) VALUES ('{param.firstName}','{param.lastName}','{param.password}','{param.phoneNumber}','{param.email}','{param.region}','{param.locality}','{param.district}','{param.school}','{param.classType}','{param.classStream}');'''
        db.execute(query)
        db.commit()
        return {"code":200,"Message": "Code sended"}
    else:
        return {"code": 200, "Message": "User has already registred , Please login"}


@router.post("/verify_mobile_otp")
async def verify_mobile_otp(param: input.VerfiyMobileOtp,db: Session = Depends(database.get_db)):
    query = f'''SELECT code from mobile_otps WHERE phone_number={param.phoneNumber};'''
    data = db.execute(query).fetchall()
    print (param.otp,(data[0])['code'])
    if str(param.otp)==((data[0])['code']):
        print (True)
        return {"code": 200, "Message" : "OTP verified successfully"}
    else :
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid OTP")
    
@router.post("/verify_email_otp")
async def verify_email_otp(param: input.VerifyEmailOtp,db: Session = Depends(database.get_db)):
    query = f'''SELECT code from email_otps WHERE email_id='{param.email}';'''
    data = db.execute(query).fetchall()
    if param.otp == ((data[0])['code']):
        return {"code": 200, "Message" : "OTP verified successfully"}
    else :
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid OTP")

    
@router.post("/login")
async def login(param: input.login,db: Session = Depends(database.get_db)):
    query = f'''SELECT password from registration WHERE phonenumber='{param.phoneNumber}';'''
    data = db.execute(query).fetchall()
    if param.password == ((data[0])['password']):
        return {"code": 200, "Message" : "Logged in Successfully"}
    else :
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid Credentials")
    
@router.post("/password_recovery")
async def password_recovery(param:input.PasswordRecovery,background_tasks:BackgroundTasks,db: Session = Depends(database.get_db)):
    user = db.query(table.Registration).filter(table.Registration.email == param.email).first() 
    if not user:
        return {"code": 200, "Message" : "Email ID is not available Please register"}
    else :
        characters = string.ascii_letters + string.digits 
        email_otp = ''.join(random.choice(characters) for i in range(6))
        email_otp_data = db.query(table.EmailOtp).filter(table.EmailOtp.email_id ==param.email)
        email_otp_data.update({"code": email_otp} ,synchronize_session=False)
        db.commit()
        background_tasks.add_task(send_in_background,email_otp,{param.email},background_tasks)
        return {"code":200,"Message": "Code sended"}
    
@router.post("/update_password")
async def update_password(param:input.UpdatePassword,db: Session = Depends(database.get_db)):
    user = db.query(table.Registration).filter(table.Registration.email == param.email).first() 
    if not user:
        return {"code": 200, "Message" : "Email ID is not available Please register"}
    else:
        data = db.query(table.Registration).filter(table.Registration.email ==param.email)
        data.update({"password": param.password},synchronize_session=False)
        return {"code": 200, "Messgae": "Updated password"}
    
@router.post("/resend_mobile_otp")
async def resend_mobile_otp(param:input.ResendMobileOtp,background_tasks:BackgroundTasks,db: Session = Depends(database.get_db)):
    phone_otp = str(random.randint(100000,999999))
    mobile_otp_data = db.query(table.MobileOtp).filter(table.MobileOtp.phone_number ==param.phoneNumber)
    mobile_otp_data.update({"code": phone_otp} ,synchronize_session=False)
    db.commit()
    background_tasks.add_task(send_sms,phone_otp,{param.phoneNumber})
    return {"code":200,"Message": "Code sended"}

@router.post("/resend_email_otp")
async def resend_email_otp(param:input.ResendEmailOtp,background_tasks:BackgroundTasks,db: Session = Depends(database.get_db)):
    characters = string.ascii_letters + string.digits 
    email_otp = ''.join(random.choice(characters) for i in range(6))
    email_otp_data = db.query(table.EmailOtp).filter(table.EmailOtp.email_id ==param.email)
    email_otp_data.update({"code": email_otp} ,synchronize_session=False)
    db.commit()
    background_tasks.add_task(send_in_background,email_otp,{param.email},background_tasks)
    return {"code":200,"Message": "Code sended"}
