from fastapi import FastAPI
from . routes import registration
from . models import table
from . config.database import engine
app = FastAPI()
app.include_router(registration.router)

table.Base.metadata.create_all(bind=engine)


@app.get("/")
async def root():

    return{"message":"profOg"}