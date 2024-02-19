import os
from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dotenv import load_dotenv
from starlette.responses import JSONResponse

# conf = ConnectionConfig(
#     MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
#     MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
#     MAIL_FROM=os.getenv('MAIL_FROM'),
#     MAIL_PORT=os.getenv('MAIL_PORT'),
#     MAIL_SERVER=os.getenv('MAIL_SERVER'),
#     MAIL_FROM_NAME=os.getenv('MAIL_FROM_NAME'),
#     MAIL_TLS=True,
#     MAIL_SSL=False,
#     USE_CREDENTIALS=True)

def send_in_background(otp:str,email:str,background_tasks: BackgroundTasks)-> JSONResponse :
    conf = ConnectionConfig(
        MAIL_USERNAME='sathyanmanickam1015@gmail.com',
        MAIL_PASSWORD='iudukwufljxsimrz',
        MAIL_PORT=587,
        MAIL_SERVER='smtp.gmail.com',
        MAIL_STARTTLS=True,
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=True)
    # message = MessageSchema(
    #     subject="Fastapi mail module",
    #     recipients=email.dict().get("email"),
    #     body="Simple background task",
    #     subtype=MessageType.plain)
    message = MessageSchema(
        subject='test',
        recipients=[email],
        body=otp,
        subtype='plain'
    )   
    fm = FastMail(conf)

    background_tasks.add_task(fm.send_message,message)

    