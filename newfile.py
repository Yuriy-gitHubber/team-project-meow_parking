from collections import UserString
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


# def Reserve():
#     session = sessionUsers()
#     data_res = {
#         'user_id': 12,
#         'parking_id': 1
#     }
#     status=FreeingUpParkingPlace(data_res,usersString)
#     if(status==ResStatus.SuccessRes):
#         print("Место зарезирвировано")
#     elif(status==ResStatus.UnsuccessRes):
#         print("Мест нет")  #Когда заканчиваются места 
#     session.close()
# Reserve()
def test_check():  # 
    session = sessionUsers()
    res=CheckUserParkingPlaces({'user_id':12},usersString)
    print(len(res))
    session.close()   

def test_search():
    session = sessionUsers()
    res=search_parking({'search':'Пушкина'},usersString)
    print(res)
    session.close()  
test_search()
# print(export(usersString))

