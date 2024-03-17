from fastapi import APIRouter,Response,Depends,BackgroundTasks,status,HTTPException
from sqlalchemy.orm import Session
from .. config import database as database
from .. schemas import input
from .. models import table
from datetime import date
from .. utils.oauth import create_access_token,get_client

router = APIRouter(tags=['client'])

@router.post("/clientlogin")
async def clientlogin(param: input.ClientLogin,db: Session = Depends(database.get_db)):
    user = db.query(table.Client).filter(table.Client.email == param.email).first()
    if not user:
        raise HTTPException(
                            status_code=403, detail=f"Client is not available , please register")
    else :
        print(user.password)
        if user.password != param.password:
            raise HTTPException(
                            status_code=403, detail=f"Email and Password doesn't match")
        access_token = create_access_token(data={"email": param.email})
        return {"code": 200, 
                "Message" : "Client Login successfully ",
                "data":{
                        "token": access_token,
                        "token_type":"bearer"}}
        

@router.get("/clientUniversity")
async def clientUniversity(fromdate:date,todate:date,db: Session = Depends(database.get_db),current_user=Depends(get_client)):
    results=[]
    client= db.query(table.Client).filter(table.Client.email==current_user).first()
    universityquery=f''' SELECT id from university where universityid='{client.universityid}';'''
    universityqueryresult=db.execute(universityquery).fetchall()
    selecteduniversity=f''' WITH RECURSIVE cte AS (SELECT DATE(mydate) as created_at FROM generate_series('{fromdate}', '{todate}', INTERVAL '1 day') d (mydate) ORDER BY created_at DESC) , data AS (SELECT ARRAY_AGG(selecteduniversity) as university,Date(created_at) as created_at FROM selecteduniversity where DATE(created_at) >= '{fromdate}' and DATE(created_at) <= '{todate}' GROUP BY DATE(created_at)) SELECT COALESCE(data.university, null)university,cte.created_at FROM cte LEFT JOIN data ON cte.created_at=data.created_at;'''
    selecteduniversityresult=db.execute(selecteduniversity).fetchall()
    for item in selecteduniversityresult:
        countdata=0
        for university in universityqueryresult:
            count_ru = f''' SELECT count(selecteduniversity) FROM selecteduniversity WHERE selecteduniversity LIKE '%{university[0]}%' AND DATE(created_at) ='{item[1]}';'''
            print(count_ru)
            count_ru_result=db.execute(count_ru).fetchall()
            countdata+=(count_ru_result[0])['count']
        results.append({
            "Date":item[1],
            "count":countdata
        })
    return results