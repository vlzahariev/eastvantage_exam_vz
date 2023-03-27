from math import radians, sin, cos, atan2, sqrt
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

'''
this function engages the DB which allows us to add and commit to it, and then close it after a certain operation.
'''


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


'''
Below class is the base class for the addresses. 
It contains latitude and longitude which must be less than or equal and greater than or equal -90 and 90 for latitude 
and -180 and 180 for longitude.
'''


class Address(BaseModel):
    name: Optional[str]
    loc_lat: float = Field(gte=-90.0, lte=90.0, description="Latitude must be between -90.0 and 90.0")
    loc_lon: float = Field(gte=-180.0, lte=180.0, description="Longitude must be between -180.0 and 180.0")


# getting all the objects from the DB
@app.get("/")
async def read_all(db: Session = Depends(get_db)):
    return db.query(models.Addresses).all()

'''
Below function is designed to receive coordinates of a certain address and a certain distance from it 
and returns all the addresses in the DB which are within that distance.

First it checks if provided coordinates are related to an address in the DB, else it raise an exception.
If we have that address in our DB, then using for loop it start compare the distance between the two locations and 
the provided at the beginning distance. If current distance is less than or equal then 
the object we are comparing is added to a list which will store all location which match our request.

In order to avoid adding the location from the request in that list, during the for loop we are checking
if coordinates of compared location match exactly the coordinates of the requested location. 
If so, we are just skipping it.

At the end the function return the list with all the location which meet criteria for the distance.
'''


@app.get('/addresses/')
async def read_address_by_given_coordinates_and_distance(loc_lat: float,
                                                         loc_lon: float,
                                                         distance: float,
                                                         db: Session = Depends(get_db)):

    address_model = db.query(models.Addresses) \
        .filter(models.Addresses.loc_lat == loc_lat, models.Addresses.loc_lon == loc_lon) \
        .first()

    if address_model is None:
        raise http_exception()

    locations_in_db = db.query(models.Addresses).all()
    location_list_within_distance = []
    lat1 = address_model.loc_lat
    lon1 = address_model.loc_lon

    for x in range(len(locations_in_db)):
        lat2 = locations_in_db[x].loc_lat
        lon2 = locations_in_db[x].loc_lon
        if lat1 == lat2 and lon1 == lon2:
            continue
        else:
            current_distance = get_distance(lat1, lon1, lat2, lon2)
            if current_distance <= distance:
                location_list_within_distance.append(locations_in_db[x])
    return location_list_within_distance

"""
I added additional functionality which is similar to the above 
but to check which locations from our DB are in a requested distance.

To perform that I used nested for loops in order to get coordinates of two objects.
Add the end function returns all locations that are away from each other less than or equal the provided distance
under the following format [ [a,b], [a,c], [b,c] ].
"""


@app.get('/addresses/{distance}')
async def read_address_by_distance_between_them(distance: float, db: Session = Depends(get_db)):
    locations_in_db = db.query(models.Addresses).all()
    location_list_within_distance = []

    for x in range(0, len(locations_in_db)):
        for y in range(x+1, len(locations_in_db)):
            lat1 = locations_in_db[x].loc_lat
            lon1 = locations_in_db[x].loc_lon
            lat2 = locations_in_db[y].loc_lat
            lon2 = locations_in_db[y].loc_lon
            current_distance = get_distance(lat1, lon1, lat2, lon2)
            if current_distance <= distance:
                location_list_within_distance.append([locations_in_db[x], locations_in_db[y]])
    return location_list_within_distance

"""
Below function is creating new address in the DB. 
Initially it creates an empty object,
and on the below lines it fill out fields of the table in the DB with provided information from the user.
"""


@app.post('/')
async def create_address(address: Address, db: Session = Depends(get_db)):
    address_model = models.Addresses()
    address_model.name = address.name
    address_model.loc_lat = address.loc_lat
    address_model.loc_lon = address.loc_lon

    db.add(address_model)
    db.commit()

    return successful_response(201)

"""
Below function is designed to update an object(record) in the DB.
It`s filtering through all the objects in DB and pick up only the one with request ID. Then it updates the object,
and update the DB. If there is no object with requested ID, then the function raise an exception for "Address not found" 
"""


@app.put('/{address_id}')
async def update_address(address_id: int, address: Address, db: Session = Depends(get_db)):
    address_model = db.query(models.Addresses)\
        .filter(models.Addresses.id == address_id)\
        .first()

    if address_model is None:
        raise http_exception()

    address_model.name = address.name
    address_model.loc_lat = address.loc_lat
    address_model.loc_lon = address.loc_lon

    db.add(address_model)
    db.commit()

    return successful_response(200)


'''The function below is filtering through all the objects in DB. 
If an object with requested ID is found, then it delete it from DB and return response message that it`s done,
else - it throw an exception.
'''


@app.delete('/{address_id}')
async def delete_address(address_id: int, db: Session = Depends(get_db)):
    address_model = db.query(models.Addresses)\
        .filter(models.Addresses.id == address_id)\
        .first()

    if address_model is None:
        raise http_exception()

    db.query(models.Addresses)\
        .filter(models.Addresses.id == address_id)\
        .delete()

    db.commit()

    return successful_response(200)


# successful response handler
def successful_response(status_code: int):
    return {
        "status": status_code,
        "transaction": "Successful"
    }


# exception handler
def http_exception():
    return HTTPException(status_code=404, detail="Address not found")


# formula for calculation distance from internet
def get_distance(loc_lat1, loc_lon1, loc_lat2, loc_lon2):
    # radius of the earth
    earth_r = 6373.0

    lat1 = radians(loc_lat1)
    lon1 = radians(loc_lon1)
    lat2 = radians(loc_lat2)
    lon2 = radians(loc_lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = earth_r * c
    return distance
