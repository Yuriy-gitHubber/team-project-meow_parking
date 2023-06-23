import hashlib
from enum import Enum
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from usersDB import Management, Rights, Roles, Users

# authorize status
class AuthStatus(Enum):
    NoData = 1
    IncorrectPassword = 2
    User = 3
    Admin = 4
  

def export(connection_string : str) -> list[str, str, str, int]:
    engineParkings = create_engine(connection_string, echo=True)
    engineParkings.connect()

    sessionParkings = sessionmaker(autoflush=False, bind=engineParkings)
    res = []
    with sessionParkings(autoflush=False, bind=engineParkings) as db:
        strJoin = db.query(Users.email, Users.password, Roles.role_name, Users.id).select_from(Users).join(Roles, Users.role==Roles.id)
        for sj in strJoin:
            res.append((sj.email, sj.password, sj.role_name, sj.id))
    return res

def authorize(d : dict, connection_string : str) ->list[AuthStatus,int]:
    given = d['email']
    data = export(connection_string)
    res = []
    if not given in [i[0] for i in data]:
        res.append((AuthStatus.NoData, 0 ))
        return res
    
    original = next(filter(lambda elem: elem[0]==given, data))
    salt = original[0]
    hashed = hashlib.md5((d['password']+salt).encode())
    
    if hashed.hexdigest() != original[1]:
        res.append((AuthStatus.IncorrectPassword, 0 ))
        return res
    if str(original[2]).lower() == 'user':
        res.append((AuthStatus.User, original[3] ))
    else:
         res.append((AuthStatus.Admin, original[3] ))
    return res

if __name__=='__main__':
    pass
