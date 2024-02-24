from fastapi import APIRouter,Response,Depends,BackgroundTasks,status,HTTPException
from sqlalchemy.orm import Session
from .. config import database as database
from .. config.database import engine
from .. schemas import input
from .. models import table
import random
import string


router = APIRouter(tags=['admin'])


@router.post("/count_user_on_each_day")
async def count_user_on_each_day(param:input.CountUserOnEachDay):

    query=f'''WITH RECURSIVE cte AS (SELECT DATE(mydate) as created_at FROM generate_series('{param.from_date}', '{param.to_date}', INTERVAL '1 day') d (mydate) ORDER BY created_at DESC) , data AS (SELECT count(id) as id,DATE(created_at) as created_at FROM registration WHERE created_at > '{param.from_date}' AND created_at < '{param.to_date}' GROUP BY DATE(created_at)) SELECT cte.created_at,COALESCE(data.id, 0)count_registration FROM cte LEFT JOIN data ON cte.created_at=data.created_at;'''
    connection = engine.connect()    
    data = connection.execute(query).fetchall()
    connection.close()
    engine.dispose()
    return data

@router.post("/filterbyidorregion")
async def filterbyidorregion(param:input.FilterByIdOrRegion,db: Session = Depends(database.get_db)):
    result=[]

    if param.id != '' and param.region !='':
        query = f''' SELECT * FROM registration where id = {param.id} AND region = '{param.region}';'''
    elif param.id == '' and param.region !='':
        query = f''' SELECT * FROM registration where region = '{param.region}';'''
    elif param.id !='' and param.region == '':
        query = f''' SELECT * FROM registration where id = {param.id};'''
    else:
        query = f''' SELECT * FROM registration;'''
    data = db.execute(query).fetchall()
    for item in data:
        result.append({
            "id": item[0],
            "First Name": item[1],
            "Last Name": item[2],
            "Phone Number": item[4],
            "Email": item[5],
            "Region":item[6],
            "Locality":item[7],
            "District":item[8],
            "School": item[9],
            "Class": item[10],
            "Class Stream": item[11],
            "created_at": item[12]
        })
    return result