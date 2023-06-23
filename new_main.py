
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Session
from sqlalchemy import  Column, Integer, String, VARCHAR
from src.reg import exportUsers,Registration,RegStatus
from src.auth import authorize,AuthStatus
from src.ResPlace import PlaceReservation,ResStatus,FreeingUpParkingPlace
from src.search import CheckUserParkingPlaces

usersString = 'postgresql+psycopg2://postgres:1@localhost:5432/parking_information'

engineUsers = create_engine(usersString, echo=True)
connection_string = engineUsers.connect()

sessionUsers = sessionmaker(autoflush=False, bind=engineUsers)

data = {
        'email': 'tester5@example.com',
        'password': 'password123',
        'name': 'Johny Doe'
    }

dataRes = {
    'parking_id': 1,
    'user_id': 1
}


# проверка регистрации 
def test_Registration():
    session = sessionUsers()
    status = Registration(data, usersString)
    if status == RegStatus.NewUser:
        print("Registration successful")
    elif status == RegStatus.ExistMail:  # Почта занята, пишите новую 
        print("Email already exists")
    session.close()

# Проверка аутентификации 
def test_auth():
    session = sessionUsers()
    status = authorize(data, usersString)
    if status == AuthStatus.User:
        print("User auth") # Зашёл юзер
    elif status == AuthStatus.NoData: 
        print("Not Exists User") # Такого юзера нет 
    elif status == AuthStatus.IncorrectPassword:
        print("Incorrect Password") #Неверный пароль, но почта правильная 
    session.close()

# Проверка бронирования места 
def test_Reserve():
    session = sessionUsers()
    status=PlaceReservation(dataRes,usersString)
    if(status==ResStatus.SuccessRes):
        print("Место зарезирвировано")
    elif(status==ResStatus.UnsuccessRes):
        print("Мест нет")  #Когда заканчиваются места 
    session.close()

def test_FreeingUpPlaces(): #Освобождение мест (True or False) If true we will change BD!
    session = sessionUsers()
    status=FreeingUpParkingPlace(dataRes,usersString)
    if(status==True):
        print("Место освобождено")
    else:
        print("Неудачно")
    session.close()

def test_check():  # 
    session = sessionUsers()
    res=CheckUserParkingPlaces(dataRes,usersString)
    print(res)
    session.close()

# Run the tests
#test_exportUsers()
#test_Registration()
#test_auth()
#test_Reserve()
#test_FreeingUpPlaces()
test_check()