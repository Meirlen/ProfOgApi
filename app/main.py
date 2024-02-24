from fastapi import FastAPI
from . routes import registration,admin
from . models import table
from . config.database import engine
app = FastAPI()
app.include_router(registration.router)
app.include_router(admin.router)

table.Base.metadata.create_all(bind=engine)


@app.get("/")
async def root():

    return{"message":"profOg1"}