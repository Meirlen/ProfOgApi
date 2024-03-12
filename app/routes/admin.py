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
from .. utils.uploadfiletospaces import uploadfile,deletefile
from fastapi import File, UploadFile,Form
from tempfile import NamedTemporaryFile
from urllib.parse import urlparse
from .. utils.oauth import get_user,get_current_token
import random,ast
from datetime import datetime


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
    query_data = f'''SELECT * FROM type WHERE id = {query.id};'''
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
    print(query.id)
    query_data = f'''SELECT * FROM test WHERE id={query.id} ;'''
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

@router.post("/deleteTest")
async def deleteTest(param:input.DeleteTest,db: Session = Depends(database.get_db)):
    query = f'''DELETE FROM test where id={param.id};'''
    print(query)
    db.execute(query)
    db.commit()
    return {"Msg" : "Test Deleted successfully"}
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
    averagesalary:int  = Form(...),
    db: Session = Depends(database.get_db)):
    datapartnersTitle = partnersTitle[0].split(',')
    datapartnersSalary = partnersSalary[0].split(',')
    lang=request.headers.get("lang")
    query = f''' INSERT INTO speciality (specialtyname,typeid,barcode,hardskills,softskills,description,about,language,averagesalary) VALUES ('{specialtyname}',{typeid},'{barcode}',ARRAY {hardskills},ARRAY {softskills},'{description}','{about}','{lang}',{averagesalary}) RETURNING ID'''
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
            obj.put_object_acl( ACL='public-read', Bucket='profogapi-stage',Key=uploadphotoname)
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
            obj.put_object_acl( ACL='public-read', Bucket='profogapi-stage',Key=uploadfilename)
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
            obj.put_object_acl( ACL='public-read', Bucket='profogapi-stage',Key=uploadpartnersimage)
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
    universityId:str  = Form(...),
    classification:str  = Form(...),
    speciality: List[str] = File(...),
    region:str  = Form(...),
    db: Session = Depends(database.get_db)):
    lang=request.headers.get("lang")
    datapartnersTitle = partnersTitle[0].split(',')
    datapartnersSalary = partnersSalary[0].split(',')
    if grant != '':
        query = f''' INSERT INTO university (universityname,city,description,about,language,grantdata,universityid,classification,speciality,region) VALUES ('{universityname}','{city}','{description}','{about}','{lang}','{grant}',{universityId},'{classification}',ARRAY {speciality},'{region}') RETURNING ID'''
    else:
        query = f''' INSERT INTO university (universityname,city,description,about,language,universityid,classification,speciality,region) VALUES ('{universityname}','{city}','{description}','{about}','{lang}',{universityId},'{classification}',ARRAY {speciality},'{region}') RETURNING ID'''
    print(query)
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
            obj.put_object_acl( ACL='public-read', Bucket='profogapi-stage',Key=uploadphotoname)
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
            obj.put_object_acl( ACL='public-read', Bucket='profogapi-stage',Key=uploadfilename)
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
            obj.put_object_acl( ACL='public-read', Bucket='profogapi-stage',Key=uploadpartnersimage)
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
            "grantdata":item[9],
            "universityID":item[10],
            "classification":item[11],
            "speciality":item[12],
            "region":item[13]
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
    universityid:int = Form(...),
    db: Session = Depends(database.get_db)):
    query = f'''INSERT INTO client (universityname,bin,email,reservephone,password,universityid) VALUES ('{universityname}','{BIN}','{email}','{reservePhone}','{password}',{universityid}) RETURNING ID ;'''
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
        obj.put_object_acl( ACL='public-read', Bucket='profogapi-stage',Key=uploadphotoname)
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
            "password":item[6],
            "universityid":item[7]
        })
    return result

@router.post("/deleteClientById")
async def deleteClientById(param:input.DeleteClient,db: Session = Depends(database.get_db)):
    query= f''' SELECT photos FROM client where id={param.id}'''
    queryresult=db.execute(query).fetchall()
    filename=f'''{queryresult[0]['photos']}'''
    parsed_url = urlparse(filename)
    object_key = parsed_url.path.lstrip('/')
    s3=deletefile()
    response=s3.delete_object(Bucket='profogapi-stage',Key=object_key)
    deletequery = f'''DELETE FROM client where id={param.id} '''
    db.execute(deletequery)
    db.commit()
    return {"Msg" : "Client Deleted successfully"}

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


@router.get("/getSpeciality")
async def getSpeciality(typeid:int,db: Session = Depends(database.get_db)):
    result=[]
    query = f'''SELECT id,specialtyname FROM speciality where typeid={typeid};'''
    query_data_result=db.execute(query).fetchall()
    for item in query_data_result:
        result.append({
            "id": item[0],
            "specialtyname":item[1]
        })

    return result

@router.post("/deleteSpeciality")
async def deleteSpeciality(param:input.DeleteSpeciality,db: Session = Depends(database.get_db)):
    query = f'''DELETE FROM speciality where id={param.id};'''
    db.execute(query)
    db.commit()
    return {"Msg" : "speciality Deleted successfully"}

@router.post("/returnTest")
async def returnTest(db: Session = Depends(database.get_db), current_user=Depends(get_user),current_token: str = Depends(get_current_token)):
    user = db.query(table.StoringTestForUser).filter(table.StoringTestForUser.phonenumber == current_user).first()
    testdata=[]
    if not user:
        print('first block ')
        test=[3,4,6,7,8,9,10,11,12]
        for i in test:
            query = f'''SELECT * FROM test where typeid={i};'''
            #print(query)
            data = db.execute(query).fetchall()
            n=random.sample(range(0,(len(data))),5) 
            print(n)
            for a in n :
                testdata.append({
                    "typeid": i,
                    "question": (data[a])['title']
                })
        test=json.dumps(testdata, ensure_ascii=False)
        query= f''' INSERT INTO storingtestforuser (phonenumber,token,question) VALUES('{current_user}','{current_token}', '{test}');'''
        db.execute(query)
        db.commit()   
    elif user.phonenumber == current_user and user.token == current_token:
        print('elif')
        query = f''' SELECT question FROM storingtestforuser;'''
        data=db.execute(query).fetchall()
        testdata=((data[0])['question'])
        testdata = json.loads(testdata)
        # result_list=result.split('"')
        # # print(testdata)
        # testdata = [s for s in result_list if s.strip() and s != '{' and s != '}' and s != ',']
    elif user.phonenumber == current_user and user.token != current_token:
        print('last')
        test=[3,4,6,7,8,9,10,11,12]
        for i in test:
            query = f'''SELECT * FROM test where typeid={i};'''
            #print(query)
            data = db.execute(query).fetchall()
            n=random.sample(range(0,(len(data))),5) 
            print(n)
            for a in n :
                testdata.append({
                    "typeid": i,
                    "question": (data[a])['title']
                })
        test=json.dumps(testdata, ensure_ascii=False)
        query= f''' UPDATE storingtestforuser SET token = '{current_token}' , question =  '{test}' WHERE phonenumber = '{current_user}'; '''
        db.execute(query)
        db.commit()
    return testdata

@router.post("/createTypeDescription")
async def createTypeDescription(request:Request,param:input.CreateTypeDescription,db: Session = Depends(database.get_db)):
    lang=request.headers.get("lang")
    result=[]
    query = f'''INSERT INTO typedescription (typeid,description,lang) VALUES ({param.typeid},'{param.description}','{lang}') RETURNING ID ;'''
    data=db.execute(query).fetchall()
    db.commit()
    id=(data[0]['id'])
    query_data = f'''SELECT * FROM typedescription WHERE id={id} ;'''
    query_data_result=db.execute(query_data).fetchall()
    for item in query_data_result:
        result.append({
            "id":item[0],
            "typeid": item[1],
            "description":item[2],
            "language":item[3]
        })

    return result

@router.get("/getTypeDescription")
async def getTypeDescription(typeid:int,db: Session = Depends(database.get_db)):
    result=[]
    query = f'''SELECT * FROM typedescription where typeid={typeid};'''
    query_data_result=db.execute(query).fetchall()
    for item in query_data_result:
        result.append({
            "id":item[0],
            "typeid": item[1],
            "description":item[2],
            "language":item[3]
        })

    return result

@router.post("/deleteTypeDescription")
async def deleteTypeDescription(param:input.DeleteTypeDescription,db: Session = Depends(database.get_db)):
    query = f'''DELETE FROM typedescription where id={param.id};'''
    db.execute(query)
    db.commit()
    return {"Msg" : "Type Description Deleted successfully"}

@router.post("/testComplete")
async def testComplete(param:input.TestComplete,db: Session = Depends(database.get_db),current_user=Depends(get_user)):
    user=db.query(table.TestComplete).filter(table.TestComplete.phone_number == current_user).first()
    if not user:
        query= f'''INSERT INTO testcomplete (phone_number,maintypeid,numberofpointsmaintype,additionaltypeid,numberofpointsadditionaltype,created_at) VALUES ({current_user},{param.mainTypeId},{param.numberOfPointsMainType},{param.additionalTypeId},{param.numberOfPointsadditionalType},'{datetime.now()}') RETURNING ID;'''
        data=db.execute(query).fetchall()
        db.commit()
        id=(data[0]['id'])
        registration_query= f'''UPDATE registration SET test='{param.mainTypeId}' where phonenumber='{current_user}' ;'''
        db.execute(registration_query)
        db.commit()
        return {"id":id,
                "Msg" : "Test complete added successfully"}
    else :
        query = f'''UPDATE testcomplete SET maintypeid={param.mainTypeId}, numberofpointsmaintype={param.numberOfPointsMainType}, additionaltypeid={param.additionalTypeId}, numberofpointsadditionaltype={param.numberOfPointsadditionalType},created_at='{datetime.now()}' where phone_number={current_user}; '''
        db.execute(query)
        db.commit()
        registration_query= f'''UPDATE registration SET test='{param.mainTypeId}' where phonenumber='{current_user}' ;'''
        db.execute(registration_query)
        db.commit()
        return {"Msg" : "Test complete updated successfully"}
    

@router.get("/getTestResults")
async def getTestResults(db: Session = Depends(database.get_db),current_user=Depends(get_user)):
    result=[]
    query = f'''WITH RECURSIVE cte AS (SELECT phone_number,maintypeid,numberofpointsmaintype,additionaltypeid,numberofpointsadditionaltype FROM testcomplete where phone_number={current_user}) ,maintypename AS (SELECT type,phone_number FROM type JOIN testcomplete ON testcomplete.maintypeid=type.id where testcomplete.phone_number={current_user}) , additionaltypename AS (SELECT type,phone_number FROM type JOIN testcomplete ON testcomplete.additionaltypeid=type.id where testcomplete.phone_number={current_user}), maindescription AS (SELECT description, phone_number FROM typedescription JOIN testcomplete ON testcomplete.maintypeid=typedescription.typeid where phone_number={current_user} ), additionaldescription AS (SELECT description, phone_number FROM typedescription JOIN testcomplete ON testcomplete.additionaltypeid=typedescription.typeid where phone_number={current_user}) SELECT cte.maintypeid as maintypeid, cte.additionaltypeid as additionaltypeid, cte.numberofpointsmaintype as mainpoints, cte.numberofpointsadditionaltype as additionalpoints, maintypename.type as maintypename, additionaltypename.type as additionaltypename, maindescription.description as maindescription, additionaldescription.description as additionaldescription FROM cte JOIN maintypename ON cte.phone_number=maintypename.phone_number JOIN additionaltypename ON maintypename.phone_number=additionaltypename.phone_number JOIN maindescription ON additionaltypename.phone_number=maindescription.phone_number JOIN additionaldescription ON maindescription.phone_number=additionaldescription.phone_number; '''
    query_data_result=db.execute(query).fetchall()
    for item in query_data_result:
        result.append({
            "maintypeid":item[0],
            "additionaltypeid": item[1],
            "mainpoints":item[2],
            "additionalpoints":item[3],
            "maintypename":item[4],
            "additionaltypename": item[5],
            "maindescription":item[6],
            "additionaldescription":item[7]
        })

    return result

@router.get("/getSpecialityById")
async def getSpecialityById(id:int,db: Session = Depends(database.get_db)):
    result=[]
    query = f'''SELECT * FROM speciality JOIN type ON speciality.typeid=type.id where speciality.id={id} '''
    query_data_result=db.execute(query).fetchall()
    for item in query_data_result:
        result.append({
            "id":item[0],
            "specialtyname": item[1],
            "typeid":item[2],
            "photos":"https://profogapi-stage.blr1.digitaloceanspaces.com/profogapi-stage/"+item[3],
            "barcode":item[4],
            "hardskills": item[5],
            "softskills":item[6],
            "description":item[7],
            "about":item[8],
            "language": item[9],
            "videos":"https://profogapi-stage.blr1.digitaloceanspaces.com/profogapi-stage/"+item[10],
            "partners":json.loads(item[11]),
            "averagesalary":item[12],
            "typename":item[14]
        })

    return result

@router.get("/getSpecialityByToken")
async def getSpecialityByToken(db: Session = Depends(database.get_db),current_user=Depends(get_user)):
    result=[]
    type_id =db.query(table.TestComplete).filter(table.TestComplete.phone_number == current_user).first()
    query=f'''SELECT id,specialtyname,photos,averagesalary FROM speciality where typeid={type_id.maintypeid};'''
    query_result=db.execute(query).fetchall()
    for item in query_result:
        result.append({
            "id": item[0],
            "specialtyname" : item[1],
            "photos":"https://profogapi-stage.blr1.digitaloceanspaces.com/profogapi-stage/"+item[2],
            "averagesalary":item[3]
        })
    return result

@router.post("/addSpecialityInRegistration")
async def addSpecialityInRegistration(
    specialityID: List[str] = Form(...),
    db: Session = Depends(database.get_db),
    current_user=Depends(get_user)):
    print(specialityID)
    user=db.query(table.SelectedSpecialities).filter(table.SelectedSpecialities.phone_number==current_user).first()
    if not user:
        insertquery = f''' INSERT INTO selectedspecialities (phone_number,selectedspecialities,created_at) VALUES ({current_user}, ARRAY {specialityID},'{datetime.now()}');'''
        db.execute(insertquery)
        db.commit()
    selectedspecialitiesquery=f''' UPDATE selectedspecialities SET  selectedspecialities= ARRAY {specialityID},created_at='{datetime.now()}' where phone_number='{current_user}';'''
    db.execute(selectedspecialitiesquery)
    db.commit()
    query = f'''UPDATE registration SET speciality= ARRAY {specialityID} where phonenumber='{current_user}';'''
    db.execute(query)
    db.commit()
    return {
        "msg": "Added Speciality in Registration Table"
    }

@router.post("/getSelectedSpecialities")
async def getSelectedSpecialities(
    db: Session = Depends(database.get_db),
    current_user=Depends(get_user)):
    results=[]
    user=db.query(table.SelectedSpecialities).filter(table.SelectedSpecialities.phone_number==current_user).first()
    cleaned_string = (user.selectedspecialities.strip('{}')).replace('"','')
    speciality_list = ast.literal_eval('[' + cleaned_string + ']')
    for item in speciality_list:
        speciality_query=f'''SELECT id,specialtyname,photos,averagesalary FROM speciality where id = {item};'''
        speciality_query_result=db.execute(speciality_query).fetchall()
        for item in speciality_query_result:
            results.append({
                "id":item[0],
                "specialtyname":item[1],
                "photos":"https://profogapi-stage.blr1.digitaloceanspaces.com/profogapi-stage/"+item[2],
                "averagesalary":item[3]
            })

    return results

@router.get("/getUniversityBySpecialityIdAndRegion")
async def getUniversityBySpecialityIdAndRegion(
    specialityId:str,
    region:str,
    db: Session = Depends(database.get_db),
    current_user=Depends(get_user)):
    results=[]
    query=f''' SELECT id,universityname,about,description,photos,city,grantdata,speciality FROM university where region='{region}';'''
    result=db.execute(query).fetchall()
    for item in result:
        present = specialityId in item[7]
        if present:
            results.append({
                "id":item[0],
                "universityname":item[1],
                "about":item[2],
                "description":item[3],
                "photos":"https://profogapi-stage.blr1.digitaloceanspaces.com/profogapi-stage/"+item[4],
                "city":item[5],
                "grant":item[6]
            })

    return results

@router.get("/getTestSpecialityUniversity")
async def getTestSpecialityUniversity(
    db: Session = Depends(database.get_db),
    current_user=Depends(get_user)):
    results=[]
    query=f''' SELECT test,university,speciality FROM registration  where phonenumber='{current_user}';'''
    result=db.execute(query).fetchall()
    for item in result:
        print(item)
        results.append({
            "test": True if item[0] is not None else False,
            "university":True if item[1] is not None else False,
            "speciality":True if item[2] is not None else False
        })

    return results