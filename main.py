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
from src.search import CheckUserParkingPlaces, export

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
#массив в котрый передаются данные о пользователях которые хотят зарегестрироваться



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
        return{
            "SUCCESS":status[0][1] 
        }
    elif status[0][0] == AuthStatus.NoData: 
        return{
            "NOT FOUND":"NOT FOUND"
        } # Такого юзера нет 
    elif status[0][0] == AuthStatus.IncorrectPassword:
        return{
            "WRONG PASS":"WRONG PASS"
    }
    


#форма поиска
@app.post("/api/search")
async def search_parking(*,data:Search):
    session = sessionUsers()
    parkings = search_parking(data, usersString )
    data_p = [] 
    for s in parkings:
        data_p.append({
            'city':  s[0],
            'street': s[1],
            'region': s[2],
            'places': s[3],
            'link': s[4]
            })
    session.close()
    try:
        return data_p
    except:
        return{
            "FAIL":"FAIL"
        }  
   #тут я проверяю типо по названию наличие парковки в базе
    

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
                'places':  parkings[idx][3]
                })
        session.close() 
        return data_p   
    except:
        return {
            "F": len(parkings)
        }

# @app.post("/api/reserved")
# def Reserve():
#     session = sessionUsers()
#     data_res = {

#     }
#     status=PlaceReservation(data_res,usersString)
#     if(status==ResStatus.SuccessRes):
#         print("Место зарезирвировано")
#     elif(status==ResStatus.UnsuccessRes):
#         print("Мест нет")  #Когда заканчиваются места 
#     session.close()

# @app.post("/api/unreserved")
# def FreeingUpPlaces(): #Освобождение мест (True or False) If true we will change BD!
#     session = sessionUsers()
#     status=FreeingUpParkingPlace(dataRes,usersString)
#     if(status==True):
#         print("Место освобождено")
#     else:
#         print("Неудачно")
#     session.close()


print(export(usersString))
# if __name__ == "__main__":
#     uvicorn.run("app.api:app", host="0.0.0.0", port=8000, reload=True)

#для запуска сервака в терминале нужно перейти в папку с этим файлом и написать
# python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
# побаловаться запросами можно на http://127.0.0.1:8000/docs
