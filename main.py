import json
from fastapi import FastAPI, Body, Request,Query
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Session
from sqlalchemy import  Column, Integer, String, VARCHAR
from pydantic import *
from typing import List
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
#import parkingDB
from pydantic import BaseModel
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from src.reg import exportUsers,Registration,RegStatus
from src.auth import authorize,AuthStatus
from src.ResPlace import PlaceReservation,ResStatus,FreeingUpParkingPlace
from src.search import CheckUserParkingPlaces, export, search_parking

usersString = 'postgresql+psycopg2://postgres:200210@localhost:5432/parking_information'

engineUsers = create_engine(usersString, echo=True)
connection_string = engineUsers.connect()

sessionUsers = sessionmaker(autoflush=False, bind=engineUsers)

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=['GET','POST'],
        allow_headers=['*']
    )
]
app = FastAPI(title="Trading apps",middleware=middleware)
Signed_User = []

#class для формы логина
class Login_User(BaseModel):
    email: str="None"
    password: str="None"

#class для формы регистрации
class Signup_User(BaseModel):
    name: str="None"
    email: str="None"
    password: str="None"

#class для поиска парковки
class Search(BaseModel):
    search: str="None"

#class с информацией о парковке
class Parking_place(BaseModel):
    name: str="None"
    location: str="None"
    size: str="None"


#class для выхода
class Ext(BaseModel):
    mes: str="None"

#class для резервирования/отрезервирования
class res_User(BaseModel):
    user_id: int = 0
    park_id: int=0


#форма регистрации ГОТОВО!
@app.post("/api/signup")
async def reg_person(*,data:Signup_User):
    session = sessionUsers()
    data_reg = {
    'name': data.name,
    'email':data.email,
    'password':data.password
    }
    status = Registration(data_reg, usersString )
    session.close()
    if status == RegStatus.NewUser:
        return{
            "SUCCESS":"SUCCESS"
        }
    elif status == RegStatus.ExistMail:  # Почта занята, пишите новую 
        return{
            "FAIL":"FAIL"
        }
    
 

#форма входа ГОТОВО!
@app.post("/api/login")
async def login_person(*,data:Login_User):
    session = sessionUsers()
    data_log = {
        'email':data.email,
        'password':data.password
    }
    status = authorize(data_log, usersString )
    session.close() 
    if status[0][0] == AuthStatus.User:
        del Signed_User [:]
        Signed_User.append(status[0][1])
        return{
            "SUCCESS":"SUCCESS" 
            # "SUCCESS":status[0][1] 
        }
    elif status[0][0] == AuthStatus.NoData: 
        return{
            "NOT FOUND":"NOT FOUND"
        } # Такого юзера нет 
    elif status[0][0] == AuthStatus.IncorrectPassword:
        return{
            "WRONG PASS":"WRONG PASS"
    }
    


    

#форма выгрузки всех парковок ГОТОВО!
@app.get("/api/home")
async def send_parkings():
    session = sessionUsers()
    parkings = export( usersString )
    try: 
        data_p = [] 
        for idx , x in enumerate(parkings):
            data_p.append({
                'id': idx, 
                'city':  parkings[idx][0],
                'street':  parkings[idx][1],
                'region':  parkings[idx][2],
                'places':  parkings[idx][3],
                 'link': parkings[idx][4]
                })
        session.close() 
        return {
            "prks":data_p,
            "user":Signed_User[0]
            }
    except:
        return {
            "F": len(parkings)
        }


@app.post("/api/homeq")
async def quit(*,data:Ext):
    del Signed_User[:]
    if(data.mes=="quit"):
        return {
            "OK":"OK"
        }
    else:
        return{
            "NONONO":"NONONO"
        }
    

@app.post("/api/homer")
def Reserve(*,data:res_User):
    session = sessionUsers()
    data_res = {
        'user_id': data.user_id,
        'parking_id': data.park_id
    }
    status=PlaceReservation(data_res,usersString)
    parkings = export( usersString )
    session.close()
    if(status==ResStatus.SuccessRes):
        try: 
            data_p = [] 
            for idx , x in enumerate(parkings):
                data_p.append({
                'id': idx, 
                'city':  parkings[idx][0],
                'street':  parkings[idx][1],
                'region':  parkings[idx][2],
                'places':  parkings[idx][3],
                 'link': parkings[idx][4]
                })
            return {
                "prks":data_p,
                "user": "RESERVED"
                }
        except:
            return {
                "F": "F"
            }
        print("Место зарезирвировано")
    elif(status==ResStatus.UnsuccessRes):
        return {

            "NOT RESERVED": "NOT RESERVED"
        }
    

@app.post("/api/homeu")
def FreeingUpPlaces(*,data:res_User): #Освобождение мест (True or False) If true we will change BD!
    session = sessionUsers()
    data_res = {
        'user_id': data.user_id,
        'parking_id': data.park_id
    }
    status=FreeingUpParkingPlace(data_res,usersString)
    parkings = export( usersString )
    session.close()
    if(status==True):
        try: 
            data_p = [] 
            for idx , x in enumerate(parkings):
                data_p.append({
                'id': idx, 
                'city':  parkings[idx][0],
                'street':  parkings[idx][1],
                'region':  parkings[idx][2],
                'places':  parkings[idx][3],
                 'link': parkings[idx][4]
                })
            return {
                "prks":data_p,
                "user": "FREE"
                }
        except:
            return {
                "F": "F"
            }
    else :
        return {

            "UNRESERVED": "UNRESERVED"
        }

@app.post("/api/homes")
async def Search_Park(*,data:Search):
    session = sessionUsers()
    parkings = search_parking({'search':data.search}, usersString )
    data_p = [] 
    for idx , x in enumerate(parkings):
            data_p.append({
                'id': idx, 
                'city':  parkings[idx][0],
                'street':  parkings[idx][1],
                'region':  parkings[idx][2],
                'places':  parkings[idx][3],
                'link': parkings[idx][4]
                })
    session.close() 
    try:
        if len(data_p) == 0 : 
            return {
                'NOT FOUND':'NOT FOUND'
            }
        
        else :
            return {'Data':data_p}
    except:
        return{
            "FAIL":"FAIL"
        }  
# print(export(usersString))

# if __name__ == "__main__":
#     uvicorn.run("app.api:app", host="0.0.0.0", port=8000, reload=True)

#для запуска сервака в терминале нужно перейти в папку с этим файлом и написать
# python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
# побаловаться запросами можно на http://127.0.0.1:8000/docs
