from fastapi import APIRouter,Response,Depends,BackgroundTasks,status,HTTPException
from sqlalchemy.orm import Session
from .. config import database as database
from .. config.database import engine,SQLALCHEMY_DATABASE_URL
from .. schemas import input
from .. models import table
import os
import string
from fastapi import Request
from typing import List,Optional
from .. utils.uploadfiletospaces import uploadfile
from fastapi import File, UploadFile,Form
from tempfile import NamedTemporaryFile

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
    limit =20
    offset = (limit*param.page) - limit
    lengthquery= f'''SELECT * FROM registration;'''
    lengthquerydata= db.execute(lengthquery).fetchall()
    result.append({
        "Total Registered Users": len(lengthquerydata)
    })
    if param.id != '' and param.region !='':
        query = f''' SELECT * FROM registration where id = {param.id} AND region = '{param.region}' LIMIT {limit} OFFSET {offset};'''
    elif param.id == '' and param.region !='':
        query = f''' SELECT * FROM registration where region = '{param.region}' LIMIT {limit} OFFSET {offset};'''
    elif param.id !='' and param.region == '':
        query = f''' SELECT * FROM registration where id = {param.id} LIMIT {limit} OFFSET {offset};'''
    else:
        query = f''' SELECT * FROM registration LIMIT {limit} OFFSET {offset} ;'''
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

@router.post("/createType")
async def createType(param:input.CreateType,db: Session = Depends(database.get_db)):
    result=[]
    query = table.Type(type=param.type)
    db.add(query)
    db.commit()
    db.refresh(query)
    query_data = f'''SELECT * FROM type WHERE type = '{param.type}';'''
    query_data_result=db.execute(query_data).fetchall()
    for item in query_data_result:
        result.append({
            "id": item[0],
            "type":item[1]
        })

    return result

@router.post("/createTestTitle")
async def createTestTitle(request:Request,param:input.CreateTitle,db: Session = Depends(database.get_db)):
    lang=request.headers.get("lang")
    result=[]
    query = table.Test(typeid=param.typeid,title=param.Title,language=lang)
    db.add(query)
    db.commit()
    db.refresh(query)
    query_data = f'''SELECT * FROM test WHERE typeid={param.typeid} AND title='{param.Title}';'''
    query_data_result=db.execute(query_data).fetchall()
    for item in query_data_result:
        result.append({
            "id":item[0],
            "typeid": item[1],
            "title":item[2],
            "language":item[3]
        })

    return result

@router.get("/getTypeAndTitle")
async def getTypeAndTitle(request:Request,page: int,db: Session = Depends(database.get_db)):
    lang=request.headers.get("lang")
    result=[]
    limit =20
    offset = (limit*page) - limit
    lengthquery=f'''SELECT test.id,type.type,test.title,test.language FROM type JOIN test ON type.id=test.typeid WHERE test.language='{lang}';'''
    lengthquerydata=db.execute(lengthquery).fetchall()
    result.append({
        "Total": len(lengthquerydata)
    })
    query = f'''SELECT test.id,type.type,test.title,test.language FROM type JOIN test ON type.id=test.typeid WHERE test.language='{lang}' LIMIT {limit} OFFSET {offset};'''
    query_data_result=db.execute(query).fetchall()
    for item in query_data_result:
        result.append({
            "id": item[0],
            "type":item[1],
            "title":item[2],
            "language":item[3]
        })

    return result

@router.get("/getAllTypeAndTitle")
async def getTypeAndTitle(db: Session = Depends(database.get_db)):
    result=[]
    query = f'''SELECT test.id,type.type,test.title,test.language FROM type JOIN test ON type.id=test.typeid;'''
    query_data_result=db.execute(query).fetchall()
    for item in query_data_result:
        result.append({
            "id": item[0],
            "type":item[1],
            "title":item[2],
            "language":item[3]
        })

    return result

@router.get("/getAllType")
async def getAllType(db: Session = Depends(database.get_db)):
    result=[]
    query = f'''SELECT * FROM type'''
    query_data_result=db.execute(query).fetchall()
    for item in query_data_result:
        result.append({
            "id": item[0],
            "type":item[1]
        })

    return result


@router.post("/updateType")
async def updateType(param:input.UpdateType,db: Session = Depends(database.get_db)):
    query = f'''UPDATE type SET type='{param.type}' where id={param.id};'''
    db.execute(query)
    db.commit()
    return {"Msg" : "Type updated successfully"}

@router.post("/deleteType")
async def deleteType(param:input.DeleteType,db: Session = Depends(database.get_db)):
    query = f'''DELETE FROM type where id={param.id};'''
    db.execute(query)
    db.commit()
    return {"Msg" : "Type Deleted successfully"}
import json
@router.post("/createSpecialty")
async def createSpecialty(request:Request,
    specialtyname :str = Form(...),
    photos: List[UploadFile] = File(...),
    typeid:int  = Form(...),
    barcode:str  = Form(...),
    hardskills: List[str] = Form(...),
    softskills :List[str] = Form(...),
    description :str  = Form(...),
    about:str = Form(...),
    video: List[UploadFile] = File(...),
    partnersImage: List[UploadFile] = File(...),
    partnersTitle: List[str] = Form(...),
    partnersSalary: List[str] = Form(...),
    db: Session = Depends(database.get_db)):
    datapartnersTitle = partnersTitle[0].split(',')
    datapartnersSalary = partnersSalary[0].split(',')
    lang=request.headers.get("lang")
    query = f''' INSERT INTO speciality (specialtyname,typeid,barcode,hardskills,softskills,description,about,language) VALUES ('{specialtyname}',{typeid},'{barcode}',ARRAY {hardskills},ARRAY {softskills},'{description}','{about}','{lang}') RETURNING ID'''
    # print(query)
    data=db.execute(query).fetchall()
    db.commit()
    id=(data[0]['id'])
    for files in (photos):  
        uploadphotoname=f'{id}_photo'+'.jpeg'
        print((uploadphotoname))
        temp = NamedTemporaryFile(delete=False)
        try:
            try:
                contents = files.file.read()
                with temp as f:
                    f.write(contents)
            except Exception:
                raise HTTPException(status_code=500, detail='Error on uploading the file')
            finally:
                files.file.close()
            obj=uploadfile()
            obj.upload_file(temp.name,'profogapi-stage',uploadphotoname,ExtraArgs={'ContentType': "image/jpeg"})
        except Exception:
            raise HTTPException(status_code=500, detail='Something went wrong')
        finally:
            os.remove(temp.name)
    for files in (video):  
        uploadfilename=f'{id}_video'+'.mp4'
        print(type(photos))
        temp = NamedTemporaryFile(delete=False)
        try:
            try:
                contents = files.file.read()
                with temp as f:
                    f.write(contents)
            except Exception:
                raise HTTPException(status_code=500, detail='Error on uploading the file')
            finally:
                files.file.close()
            obj=uploadfile()
            obj.upload_file(temp.name,'profogapi-stage',uploadfilename,ExtraArgs={'ContentType': "image/jpeg"})
        except Exception:
            raise HTTPException(status_code=500, detail='Something went wrong')
        finally:
            os.remove(temp.name)
    partnerImgaeList=[]
    for a,files in enumerate(partnersImage):  
        uploadpartnersimage=f'{id}_partnersimage_{datapartnersTitle[a]}'+'.jpeg'
        partnerImgaeList.append(uploadpartnersimage)
        print((uploadpartnersimage))
        temp = NamedTemporaryFile(delete=False)
        try:
            try:
                contents = files.file.read()
                with temp as f:
                    f.write(contents)
            except Exception:
                raise HTTPException(status_code=500, detail='Error on uploading the file')
            finally:
                files.file.close()
            obj=uploadfile()
            obj.upload_file(temp.name,'profogapi-stage',uploadpartnersimage,ExtraArgs={'ContentType': "image/jpeg"})
        except Exception:
            raise HTTPException(status_code=500, detail='Something went wrong')
        finally:
            os.remove(temp.name)
    print(partnerImgaeList)
    partnersdata=[]
    for a,item in enumerate(partnerImgaeList):
        partnersdata.append({
            "Image": f'https://profogapi-stage.blr1.digitaloceanspaces.com/profogapi-stage/{item}',
            "Title": datapartnersTitle[a],
            "Salary": datapartnersSalary[a]
        })
    partnersdata = json.dumps(partnersdata)
    print((partnersdata) )
    query = f'''UPDATE speciality SET photos='{uploadphotoname}',videos='{uploadfilename}',partners='{partnersdata}' where id ={id};'''
    print(query)
    db.execute(query)
    db.commit()
    return {"ID": id,
            "Msg" : "Speciality created successfully"}

@router.post("/createUniversity")
async def createUniversity(request:Request,
    universityname :str = Form(...),
    photos: List[UploadFile] = File(...),
    city:str  = Form(...),
    grant: Optional[str]= Form(None),
    description :str  = Form(...),
    about:str = Form(...),
    video: List[UploadFile] = File(...),
    partnersImage: List[UploadFile] = File(...),
    partnersTitle: List[str] = Form(...),
    partnersSalary: List[str] = Form(...),
    db: Session = Depends(database.get_db)):
    lang=request.headers.get("lang")
    datapartnersTitle = partnersTitle[0].split(',')
    datapartnersSalary = partnersSalary[0].split(',')
    if grant != '':
        query = f''' INSERT INTO university (universityname,city,description,about,language,grantdata) VALUES ('{universityname}','{city}','{description}','{about}','{lang}','{grant}') RETURNING ID'''
    else:
        query = f''' INSERT INTO university (universityname,city,description,about,language) VALUES ('{universityname}','{city}','{description}','{about}','{lang}') RETURNING ID'''
    data=db.execute(query).fetchall()
    db.commit()
    id=(data[0]['id'])
    for files in (photos):  
        uploadphotoname=f'{id}_universityphoto'+'.jpeg'
        print((uploadphotoname))
        temp = NamedTemporaryFile(delete=False)
        try:
            try:
                contents = files.file.read()
                with temp as f:
                    f.write(contents)
            except Exception:
                raise HTTPException(status_code=500, detail='Error on uploading the file')
            finally:
                files.file.close()
            obj=uploadfile()
            obj.upload_file(temp.name,'profogapi-stage',uploadphotoname,ExtraArgs={'ContentType': "image/jpeg"})
        except Exception:
            raise HTTPException(status_code=500, detail='Something went wrong')
        finally:
            os.remove(temp.name)
    for files in (video):  
        uploadfilename=f'{id}_universityvideo'+'.mp4'
        print(type(photos))
        temp = NamedTemporaryFile(delete=False)
        try:
            try:
                contents = files.file.read()
                with temp as f:
                    f.write(contents)
            except Exception:
                raise HTTPException(status_code=500, detail='Error on uploading the file')
            finally:
                files.file.close()
            obj=uploadfile()
            obj.upload_file(temp.name,'profogapi-stage',uploadfilename,ExtraArgs={'ContentType': "image/jpeg"})
        except Exception:
            raise HTTPException(status_code=500, detail='Something went wrong')
        finally:
            os.remove(temp.name)
    
    partnerImgaeList=[]
    for a,files in enumerate(partnersImage):  
        uploadpartnersimage=f'{id}_universitypartnersimage_{datapartnersTitle[a]}'+'.jpeg'
        partnerImgaeList.append(uploadpartnersimage)
        print((uploadpartnersimage))
        temp = NamedTemporaryFile(delete=False)
        try:
            try:
                contents = files.file.read()
                with temp as f:
                    f.write(contents)
            except Exception:
                raise HTTPException(status_code=500, detail='Error on uploading the file')
            finally:
                files.file.close()
            obj=uploadfile()
            obj.upload_file(temp.name,'profogapi-stage',uploadpartnersimage,ExtraArgs={'ContentType': "image/jpeg"})
        except Exception:
            raise HTTPException(status_code=500, detail='Something went wrong')
        finally:
            os.remove(temp.name)
    partnersdata=[]
    for a,item in enumerate(partnerImgaeList):
        partnersdata.append({
            "Image": f'https://profogapi-stage.blr1.digitaloceanspaces.com/profogapi-stage/{item}',
            "Title": datapartnersTitle[a],
            "Salary": datapartnersSalary[a]
        })
    partnersdata = json.dumps(partnersdata)
    print((partnersdata) )
    query = f'''UPDATE university SET photos='{uploadphotoname}',videos='{uploadfilename}',partners='{partnersdata}' where id ={id};'''
    print(query)
    db.execute(query)
    db.commit()
    return {"ID": id,
            "Msg" : "University created successfully"}


@router.get("/getUniversityById")
async def getUniversityById(id:int,db: Session = Depends(database.get_db)):
    result=[]
    query = f'''SELECT * FROM university where id = {id}'''
    query_data_result=db.execute(query).fetchall()
    for item in query_data_result:
        result.append({
            "id": item[0],
            "universityname":item[1],
            "photos":item[2],
            "city":item[3],
            "description":item[4],
            "about":item[5],
            "language":item[6],
            "videos":item[7],
            "partners":item[8],
            "grantdata":item[9]
        })
    return result

@router.get("/getAllUniversity")
async def getAllUniversity(db: Session = Depends(database.get_db)):
    result=[]
    query = f'''SELECT id,universityname FROM university '''
    query_data_result=db.execute(query).fetchall()
    for item in query_data_result:
        result.append({
            "id": item[0],
            "universityname":item[1],
        })
    return result

@router.post("/createClient")
async def createClient(
    universityname :str = Form(...),
    photos: UploadFile = File(...),
    BIN:str  = Form(...),
    email: str= Form(...),
    reservePhone :str  = Form(...),
    password:str = Form(...),
    db: Session = Depends(database.get_db)):
    query = f'''INSERT INTO client (universityname,bin,email,reservephone,password) VALUES ('{universityname}','{BIN}','{email}','{reservePhone}','{password}') RETURNING ID ;'''
    data=db.execute(query).fetchall()
    db.commit()
    id=(data[0]['id'])
    uploadphotoname=f'{id}_client'+'.jpeg'
    print((uploadphotoname))
    temp = NamedTemporaryFile(delete=False)
    try:
        try:
            contents = photos.file.read()
            with temp as f:
                f.write(contents)
        except Exception:
            raise HTTPException(status_code=500, detail='Error on uploading the file')
        finally:
            photos.file.close()
        obj=uploadfile()
        obj.upload_file(temp.name,'profogapi-stage',uploadphotoname,ExtraArgs={'ContentType': "image/jpeg"})
    except Exception:
        raise HTTPException(status_code=500, detail='Something went wrong')
    finally:
        os.remove(temp.name)
    imagelink=f'https://profogapi-stage.blr1.digitaloceanspaces.com/profogapi-stage/{uploadphotoname}'
    query = f'''UPDATE client SET photos='{imagelink}' where id ={id};'''
    db.execute(query)
    db.commit()
    return {"ID": id,
            "Msg" : "Client created successfully"}

@router.get("/getAllClient")
async def getAllClient(page:int,db: Session = Depends(database.get_db)):
    result=[]
    limit =20
    offset = (limit*page) - limit
    lengthquery = f'''SELECT * FROM client'''
    lengthquerydata= db.execute(lengthquery).fetchall()
    result.append({
        "Total Registered Users": len(lengthquerydata)
    })
    query = f'''SELECT * FROM client LIMIT {limit} OFFSET {offset} '''
    query_data_result=db.execute(query).fetchall()
    for item in query_data_result:
        result.append({
            "id": item[0],
            "universityname":item[1],
            "photos":item[2],
            "bin":item[3],
            "email":item[4],
            "reservephone":item[5],
            "password":item[6]
        })
    return result