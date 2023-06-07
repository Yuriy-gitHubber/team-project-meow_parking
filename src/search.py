import psycopg2
from psycopg2 import sql
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..parkingsDB import Cities, FreePlaces, Parkings, Regions, Streets


def export(connection_string : str) -> list[str, str, str, int]: # city, street, region, free places
    engineParkings = create_engine(connection_string, echo=True)
    engineParkings.connect()

    sessionParkings = sessionmaker(autoflush=False, bind=engineParkings)

    res = []
    with sessionParkings(autoflush=False, bind=engineParkings) as db:
        strJoin = db.query(Cities.name.label('city_name'), Streets.name.label('street_name'), Regions.name.label('region_name'), FreePlaces.amount_free_places
                            ).select_from(Parkings).join(Streets, Parkings.street == Streets.id
                            ).join(Cities, Streets.city == Cities.id
                            ).join(Regions, Cities.region == Regions.id
                            ).join(FreePlaces, Parkings.id == FreePlaces.id_parking).all()
        for s in strJoin:
            res.append(s.city_name, s.street_name, s.region_name, s.amount_free_places)
    
    return res

def search_parking(d : dict, connection_string : str, result_limit : int) -> list[str, str, str, int]:
    lst = export(connection_string)
    query = str(d['query']).lower()
    l, r = 0, len(query)+1
    filtered = None
    while r-l>1:
        m = (l+r)//2
        filtered = filter(lambda elem: elem[:m][1].lower() == query, lst)
        if len(filtered)>0:
            l=m
        else:
            r=m
    if l==0:
        return []
    return filtered if len(filtered)<=result_limit else filtered[:result_limit] 


if __name__=='__main__':
    pass