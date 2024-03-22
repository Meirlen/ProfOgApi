from fastapi import APIRouter,Response,Depends,BackgroundTasks,status,HTTPException
from sqlalchemy.orm import Session
from .. config import database as database
from .. schemas import input
from .. models import table
from datetime import date,datetime
from .. utils.oauth import create_access_token,get_client
from typing import Optional
from tempfile import NamedTemporaryFile
from fastapi import File, UploadFile,Form
from urllib.parse import urlparse
from .. utils.uploadfiletospaces import uploadfile,deletefile
import os
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
        ru_university_name=db.query(table.University).filter(table.University.language=='ru').filter(table.University.universityid==user.universityid).first()
        kz_university_name=db.query(table.University).filter(table.University.language=='kz').filter(table.University.universityid==user.universityid).first()
        return {"code": 200, 
                "Message" : "Client Login successfully ",
                "data":{
                        "UniversityNameRu": "null" if ru_university_name is None else ru_university_name.universityname,
                        "UniversityNameKz": "null" if kz_university_name is None else kz_university_name.universityname,
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
            count_ru_result=db.execute(count_ru).fetchall()
            countdata+=(count_ru_result[0])['count']
        results.append({
            "Date":item[1],
            "count":countdata
        })
    return results

@router.get("/getSeletedUniversityUsers")
async def getSeletedUniversityUsers(page:int,region:Optional[str]=None,id:Optional[int]=None,db: Session = Depends(database.get_db),current_user=Depends(get_client)):
    results,count_of_users=[],0
    limit =5
    offset = (limit*page) - limit
    client= db.query(table.Client).filter(table.Client.email==current_user).first()
    universityquery=f''' SELECT id from university where universityid='{client.universityid}';'''
    universityqueryresult=db.execute(universityquery).fetchall()
    for item in universityqueryresult:
        countuser= f''' SELECT id,firstname,lastname,phonenumber,email,region,locality,district,school,classtype,classstream FROM registration where university  LIKE '%{item[0]}%';'''
        countuserresult=db.execute(countuser).fetchall()
        count_of_users+=len(countuserresult)
    results.append({
        "Count of users": count_of_users
    })
    for item in universityqueryresult:
        if region !=None and id != None:
            registrationquery= f''' SELECT id,firstname,lastname,phonenumber,email,region,locality,district,school,classtype,classstream FROM registration where university  LIKE '%{item[0]}%' and region ='{region}' and id={id} LIMIT {limit} OFFSET {offset};'''
        elif region != None and id == None:
            registrationquery= f''' SELECT id,firstname,lastname,phonenumber,email,region,locality,district,school,classtype,classstream FROM registration where university  LIKE '%{item[0]}%' and region ='{region}'  LIMIT {limit} OFFSET {offset};'''
        elif region == None and id != None:
            registrationquery= f''' SELECT id,firstname,lastname,phonenumber,email,region,locality,district,school,classtype,classstream FROM registration where university  LIKE '%{item[0]}%' and id ={id}  LIMIT {limit} OFFSET {offset};'''
        else:
            registrationquery= f''' SELECT id,firstname,lastname,phonenumber,email,region,locality,district,school,classtype,classstream FROM registration where university  LIKE '%{item[0]}%'  LIMIT {limit} OFFSET {offset};'''
        registrationqueryresult=db.execute(registrationquery).fetchall()
        for data in registrationqueryresult:
            results.append ({
                "id":data[0],
                "firstname":data[1],
                "lastname":data[2],
                "phonenumber":data[3],
                "email":data[4],
                "region":data[5],
                "locality":data[6],
                "district":data[7],
                "school":data[8],
                "classtype":data[9],
                "classStream":data[10]
            })
    return results

@router.post("/createCareerguidance")
async def createCareerguidance(name :str = Form(...),
    qrcode: UploadFile = File(...),
    phone:int  = Form(...),
    barcode:str  = Form(...),
    db: Session = Depends(database.get_db),
    current_user=Depends(get_client)):
    user = db.query(table.CareerGuidance).filter(table.CareerGuidance.phone_number==phone).first()
    barcode_data = db.query(table.CareerGuidance).filter(table.CareerGuidance.barcode==barcode).first()
    if not user and not barcode_data:
        insertquery=f''' INSERT INTO careerguidance (name,phone_number,barcode,clientemail,created_at) VALUES ('{name}',{phone},'{barcode}','{current_user}','{datetime.now()}') RETURNING ID ;'''
        data=db.execute(insertquery).fetchall()
        db.commit()
        id=(data[0]['id'])
        uploadphotoname=f'{id}_qrcode'+'.jpeg'
        temp = NamedTemporaryFile(delete=False)
        try:
            try:
                contents = qrcode.file.read()
                with temp as f:
                    f.write(contents)
            except Exception:
                raise HTTPException(status_code=500, detail='Error on uploading the file')
            finally:
                qrcode.file.close()
            obj=uploadfile()
            obj.upload_file(temp.name,'profogapi-stage',uploadphotoname,ExtraArgs={'ContentType': "image/jpeg"})
            obj.put_object_acl( ACL='public-read', Bucket='profogapi-stage',Key=uploadphotoname)
        except Exception:
            raise HTTPException(status_code=500, detail='Something went wrong')
        finally:
            os.remove(temp.name)
        qrcodelink=f'https://profogapi-stage.blr1.digitaloceanspaces.com/profogapi-stage/{uploadphotoname}'
        query = f'''UPDATE careerguidance SET qrcode='{qrcodelink}' where id ={id};'''
        db.execute(query)
        db.commit()
        return {"code": 200, 
                "Message" : "Carrer Guidance created successfully"}
    elif user:
        raise HTTPException (
                            status_code=403, detail=f"Phone number is already available")
    elif barcode_data:
        raise HTTPException (
                            status_code=403, detail=f"Barcode is already available")
    

@router.get("/getCareerGuidance")
async def getCareerGuidance(page:int,id:Optional[int]=None,db: Session = Depends(database.get_db),current_user=Depends(get_client)):
    results=[]
    limit =10
    offset = (limit*page) - limit
    query=f''' SELECT * FROM careerguidance;'''
    result=db.execute(query).fetchall()
    results.append({
        "Count of Carrer guidance specialists" : len(result)
    })
    if id != None :
        query=f''' SELECT * FROM careerguidance where id ={id};'''
        result=db.execute(query).fetchall()
    else:
        query=f''' SELECT * FROM careerguidance LIMIT {limit} OFFSET {offset};'''
        result=db.execute(query).fetchall()
    for item in result:
        results.append({
            "id":item[0],
            "name":item[1],
            "phone":item[2],
            "barcode":item[3],
            "client_emai":item[4],
            "qrcode":item[5],
            "created_at":item[6]
        })
    return results

@router.post("/deleteCarrerGuidanceById")
async def deleteCarrerGuidanceById(param:input.DeleteCareerGuidanceById,db: Session = Depends(database.get_db),current_user=Depends(get_client)):
    carrer= db.query(table.CareerGuidance).filter(table.CareerGuidance.id==param.id).first()
    if not carrer:
        raise HTTPException (
            status_code=403, detail=f"Carrer Guidance Id is not available"
        )
    filename=carrer.qrcode
    parsed_url = urlparse(filename)
    object_key = parsed_url.path.lstrip('/')
    print(object_key)
    s3=deletefile()
    response=s3.delete_object(Bucket='profogapi-stage',Key=object_key)
    query = f''' DELETE FROM careerguidance where id = {param.id};'''
    db.execute(query)
    db.commit()
    return {"Msg" : "Career Guidance deleted successfully"}

@router.get("/getUserBasedOnBarcode")
async def getUserBasedOnBarcode(page:int,barcode:str,db: Session = Depends(database.get_db),current_user=Depends(get_client)):
    results=[]
    limit =10
    offset = (limit*page) - limit
    total_count_query= f''' SELECT user_phone FROM careerguidancebarcode where barcode = '{barcode}';'''
    total_count_query_result = db.execute(total_count_query).fetchall()
    results.append({
        "Total Users": len(total_count_query)
    })
    query=f''' SELECT user_phone FROM careerguidancebarcode where barcode = '{barcode}' LIMIT {limit} OFFSET {offset};'''
    result=db.execute(query).fetchall()
    for data in result:
        user_query=f'''SELECT * FROM registration where phonenumber = '{data[0]}';'''
        user_query_result=db.execute(user_query).fetchall()  
        print(user_query_result)      
        for item in user_query_result:
            results.append({
                "id": item[0],
                "First Name": item[1],
                "Last Name": item[2],
                "Phone Number": item[3],
                "Email": item[4],
                "Region":item[5],
                "Locality":item[6],
                "District":item[7],
                "School": item[8],
                "Class": item[9],
                "Class Stream": item[10],
                "test": item[11],
                "universityname": item[12],
                "specialityname":item[13],
                "created_at": item[14]
            })
    return results