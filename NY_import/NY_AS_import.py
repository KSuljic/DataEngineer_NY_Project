#!/usr/bin/env python3

#Initial imports
import os
import requests
import json
import pymongo
from pymongo import ReplaceOne

import time
import random
import numpy as np

import logging

logging.basicConfig(level=logging.INFO)

  


def natural_variation_delay(min_delay=20, max_delay=30):
    """
    Waits for a random amount of time between `min_delay` and `max_delay` seconds.
    """
    t_wait = random.uniform(min_delay, max_delay)
    print(t_wait)
    time.sleep(t_wait)



def main():
    logging.info("Starting the import process...")

    # Access API
    #API_KEY = 'PAKnickrXf68F5WPgbBgEe2Ine6vI7oi'
    API_KEY = os.getenv('NYTIMES_API_KEY')
    url = 'https://api.nytimes.com/svc/search/v2/'
    endpoint = 'articlesearch.json'


    logging.info('Accessing client')
    # Access DB
    from pymongo import MongoClient
    # Create a connection to the MongoDB server
    client = MongoClient('mongodb', 27017)
    # Access the database
    db = client['NY_Project']
    collection = db['ny_articles']


    ##

    #DOCS = []

    # Get the maximum _id value from the collection
    max_id = collection.find_one(sort=[("ny_id", -1)])
    index_counter = max_id['ny_id'] + 1 if max_id else 0

    # Main loop
    page = 0
    attempts = 0
    
    logging.info('Starting while loop')

    while page < 100:
        DOCS = []

        #while attempts < 5:
        try:
            logging.info(f"Trying page {page}, attempt {attempts + 1}")

            res = requests.get(f'{url}/{endpoint}?page={page}&api-key={API_KEY}')
            res.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code

            articles_names_json = res.json()
            documents = articles_names_json.get('response')['docs']

            # Assign a new _id to each document
            for doc in documents:
                doc['ny_id'] = index_counter
                index_counter += 1

            DOCS.extend(documents)

            natural_variation_delay()

            page += 1

            #break

        except TypeError:
                # TypeError handling here
            print(f"TypeError occurred on page {page}, attempt {attempts + 1}")
            attempts += 1
            natural_variation_delay()  # Wait before retrying
            natural_variation_delay()

        # except requests.HTTPError as http_err:
        #     # Handle HTTP errors here
        #     print(f"HTTPError occurred: {http_err}")
        #     break  # Exit the attempts loop and go to the next page


        # except requests.RequestException as req_err:
        #     # Handle other requests exceptions here
        #     print(f"RequestException occurred: {req_err}")
        #     break  # Exit the attempts loop and go to the next page


    # insert all at once
    # try:
    #     collection.insert_many(DOCS, ordered=False)
    # except pymongo.errors.BulkWriteError as bwe:
    #     print(bwe.details)
            

        # insert articles by updating
        for doc in DOCS:
            # Assuming 'uri' is the unique identifier field in your article data
            article_uri = doc['uri']

            # rename the _id as there is a immutable _id field in mongodb
            if '_id' in doc:
                #doc['ny_id'] = doc['_id']
                del doc['_id']


            # Update the article if it exists, otherwise insert it
            collection.update_one({'uri': article_uri}, {'$set': doc}, upsert=True)



    logging.info("Import process completed.")


if __name__ == "__main__":
    main()