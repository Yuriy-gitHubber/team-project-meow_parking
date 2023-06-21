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
import usersDB
import src.auth as auth

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
people_to_signup=[Signup_User(name="aaa",email="aboba@mail.ru",password="sussus")]
#массив с данными о парковках
parkings=[Parking_place(name="aboba",location="Ierusalim",size="4")]

#функция для поиска по email
def is_user(email):
    for a in people_to_signup:
        if a.email==email:
            return True
    return False
#функция для проверки правильности входа (пароль)
def is_user_r(email,password):
    for a in people_to_signup:
        if a.email==email:
            if a.password==password:
                return True
            return False
    return False
#функция для поиска парковок
def is_parkplace(search):
    for a in parkings:
        if a.name==search:
            return True
    return False

#форма регистрации
@app.post("/api/signup")
async def login_person(*,data:Signup_User):
    #тут я проверяю типо по email нету ли такго пользователя
    if is_user(data.email)==False:
        person = Signup_User(name=data.name,email=data.email,password=data.password)
        people_to_signup.append(person)
        return{
            "SUCCESS":"SUCCESS",
            "data":data,
            "someshit" :people_to_signup
        }
    else:
        return{
            "FAILURE":"FAILURE",
        }

#форма входа

@app.post("/api/login")
async def login_person(*,data:Login_User):
    #person = Login_User(email=data.email,password=data.password)
    #тут я проверяю типо по email есть ли такой пользователь
    if(auth.authorize(data = data.email) == 1):
         return{
            "False":"False"
        }
    elif auth.authorize(data = data.email) == 2:
         return{
            "False":"False"
        }
    elif auth.authorize(data = data.email) == 3:
         return{
            "YesU":"YesU",
            "data":data,
            "someshit" :people_to_signup
        }
    elif auth.authorize(data = data.email) == 4:
         return{
            "YesA":"YesA",
            "data":data,
            "someshit" :people_to_signup
        }    
#форма поиска
@app.post("/api/search")
async def search_parking(*,data:Search):
   #тут я проверяю типо по названию наличие парковки в базе
    if is_parkplace(data.search)==True:
        return{
            "status":"1",            
        }
    else:
        return{
            "status":"0",
        }

if __name__ == "__main__":
    uvicorn.run("app.api:app", host="0.0.0.0", port=8000, reload=True)

#для запуска сервака в терминале нужно перейти в папку с этим файлом и написать
# python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
# побаловаться запросами можно на http://127.0.0.1:8000/docs
