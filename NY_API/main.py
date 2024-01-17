from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
from pymongo import MongoClient
from typing import List, Optional

#instantiate API using FastAPI, HTTPBasic
api = FastAPI()
security = HTTPBasic()

#encrypt passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#users database
users = {
    "daniel": {
        "username": "daniel",
        "name": "Daniel Datascientest",
        "hashed_password": pwd_context.hash('datascientest'),
    },
    "john" : {
        "username" :  "john",
        "name" : "John Datascientest",
        "hashed_password" : pwd_context.hash('secret'),
    }
}

# this dependency is used to authenticate the user using the HTTP method
def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    username = credentials.username
    if not(users.get(username)) or not(pwd_context.verify(credentials.password, users[username]['hashed_password'])):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# MongoDB connection settings
#MONGODB_URL = "mongodb://127.0.0.1:27017/" # Replace 27018 with actual port number of database

# PyMongo client and database
client = MongoClient('mongodb', 27017)
db = client['NY_Project']
collection = db['ny_articles']

# New endpoint to get average word count with authentication
@api.get("/average_word_count")
def get_average_word_count(current_user: str = Depends(get_current_user)):
    # Access the MongoDB collection
    # Perform your query to get the average word count
    result = collection.find_one({}, {"average_word_count": 1, "_id": 0})

    if result:
        return {"average_word_count": result["average_word_count"]}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Average word count not found",
        )


#webpage:    
#http://localhost:8000/docs

# requests to test api
#curl -X GET -i http://127.0.0.1:8000/average_word_count -u daniel:datascientest
#curl -X GET -i http://127.0.0.1:8000/average_word_count -H 'Authorization: Basic ZGFuaWVsOmRhdGFzY2llbnRlc3Q='