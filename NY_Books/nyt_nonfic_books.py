from pymongo import MongoClient
from datetime import datetime, timedelta
import time
import requests

# MongoDB connection details (make sure this matches your actual MongoDB credentials and address)
mongo_uri = 'mongodb://localhost:27017/'  # Use the same URI as in Script A
client = MongoClient(mongo_uri)

# Use the same database as in Script A
db = client['NY_ArticleSearch']  # Changed from 'NYT_project' to 'NY_ArticleSearch'

# Different collection name for non-fiction books
collection = db['nonfic_books']

# Set the initial date
current_date = datetime.strptime('2023-11-19', '%Y-%m-%d')

# Number of weeks to go back
weeks_to_fetch = 500

nonfic_books = []
no_apicalls = 0


for _ in range(weeks_to_fetch):

    api_url = f'https://api.nytimes.com/svc/books/v3/lists/{current_date.strftime("%Y-%m-%d")}/combined-print-and-e-book-nonfiction.json?api-key=dqilWz1jPGmXfYGUu1cxpdhJtIUSOfGl'
    response = requests.get(api_url)
    data = response.json()

    collection.insert_one(data)

    # Update the current date to the previous week
    current_date -= timedelta(weeks=1)

    time.sleep(12)

    no_apicalls = no_apicalls + 1


print("non-fiction bestseller data saved to mongoDB database")

print(f'The number of api calls: {no_apicalls}')
