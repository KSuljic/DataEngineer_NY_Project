'''Adel Chouadria's NYT Newswire API Calls
When used as a cron job, please set
0 */4 * * * <full filename>
to avoid Error 429: Too Many Requests
'''

import requests
import pymongo
import datetime
import time
from tqdm import tqdm
import os

API_KEY = os.getenv('NYTIMES_API_KEY') #If None, will prompt the user to get a key.

MONGO_LABEL = os.environ.get('MONGODB_ADDRESS','localhost') #Unless you have your own address
MONGO_PORT = int(os.environ.get('MONGODB_PORT',27017)) #Unless you have a specific port, default is 27017

DB_CLIENT = pymongo.MongoClient('mongodb', 27017) #pymongo.MongoClient(host=MONGO_LABEL, port=MONGO_PORT)
WAIT_TIME = 12 #Waiting time for our requests set at 12 seconds. We want to avoid Error 429: Too many requests and Error 429: Rate Limit Exceeded

#I'm aware that we have a bunch of API keys and DB addresses laying around, and we'll probably pass it as an environment
#variable instead (os.getenv() hello)
#import os

#For the sake of cleanliness, I'll hard-implement the time limitations of the API in my requests.
def nyt_requests_get(url, endpoint, payload=None):
    '''All requests will have a 12-second wait timer attached to them.
    I could use requests.get(...) then a time.sleep() everywhere, but it's better to simplify readability.'''
    global WAIT_TIME
    re = requests.get(f'{url}{endpoint}',params=payload)
    time.sleep(WAIT_TIME)
    return re

def add_section_output(section:str, batch_size:int = 500):
    '''We provide a section name, and we receive the output for that specific section here.'''

    global API_KEY
    global DB_CLIENT
    global WAIT_TIME

    db = DB_CLIENT['NY_Project']
    nw_collection = db['times_newswire']

    endp_section = f'/nyt/{section}.json'
    url = 'https://api.nytimes.com/svc/news/v3/content'

    #We will receive 500 outputs from the API (potentially).
    #That said, we could be wiser adjusting the limit and offset accordingly if we need to.
    #Rule of thumb: resp_size must be a multiple of 20, and must be 20 at least.
    if batch_size % 20 != 0:
        batch_size = batch_size - (batch_size % 20)

    if batch_size > 500:
        batch_size = 500
    elif batch_size < 20:
        batch_size = 20

    #Autocalculating the offsets after making sure that our response size was compliant with the Times API:
    offset_steps = range(0,1000,batch_size)

    payload = {
        'api-key':API_KEY,
        'limit':batch_size
    }

    sec_output = []

    for offset in offset_steps:
        payload.update({'offset':offset})
        re_sec = nyt_requests_get(url,endp_section,payload)

        try:
            sec_output.extend(re_sec.json()['results'])
        except:
            print(f'There was an error while acquiring data for the section {section}:\n{re_sec.status_code} - {re_sec.content} on loop {1 + (offset % 500)}')
            if offset == 0:
                return None #We did not get any data, or there was a brutal error in there.
            else:
                break #If we did get at least the first wave, we will consider that we have data to process.

    #To do if needed: filter the data before shipping it to MongoDB.
    #<Insert code here>


    #Progress bar says hello for CLI clarity
    pbar = tqdm(range(len(sec_output)), total=len(sec_output), desc=section)

    #Convert the datetime fields? Yay or nay.
    convert_dts = False #Change to True if we want to convert, left at dev discretion.

    #In case we want to check for updated articles.
    unupdated_streak = 0

    #If we have data, let's send it to MongoDB.
    for item in sec_output:

        #We will switch the ISO-formatted datetime strings to datetime types if we chose that option previously.
        if convert_dts:
            for field in ['updated_date', 'created_date', 'published_date', 'first_published_date']:
                try:
                    item[field] = datetime.datetime.fromisoformat(item[field])
                except:
                    continue #skip to the next if there is nothing in that field

        #Query MongoDB to check if the item already exists + get the update date if it does:
        mongo_check = nw_collection.find_one({"uri":item['uri']},{"uri":1,"updated_date":1})
        pbar.update()

        #If the item does not exist: add it
        if mongo_check is None:
            nw_collection.insert_one(item)
            unupdated_streak = 0

        else:
            #Do we already have the item? Check if there was a change.
            #Domain-specific knowledge: check if the 'updated_date' field has changed to determine that.
            if mongo_check['updated_date'] != item['updated_date']:
                nw_collection.update_one({"uri":item['uri']}, {"$set":item}, upsert=True)
                unupdated_streak = 0

            #No else needed here if there was no update, it's like else: skip
            #Eventualy, one thing we can do is "return None" on the ELSE section if there's a streak of unupdated articles.
            #We could set a threshold of "if we get 5 un-updated articles in a row, we call it a wrap."
            #I will pre-emptively include this.
            else:
                unupdated_streak += 1

                if unupdated_streak > 10:
                    pbar.close()
                    return None


def get_full_newswire_output():
    '''This function allows us to send a request and get the latest news articles
    via the News Wire API.'''
    global DB_CLIENT
    db = DB_CLIENT['NYT_project']

    #This will tick on the first runtime: did we create the collection yet? If not, create it.
    #if 'times_newswire' not in db.list_collection_names():
    #    db.createCollection('times_newswire')

    #Call the global variable: API_KEY (TO DO: choose one key in our code)
    global API_KEY

    #Step 1: Get our list of sections
    url = 'https://api.nytimes.com/svc/news/v3/content'
    endpoint_section_list = '/section-list.json'
    res = nyt_requests_get(url,endpoint_section_list,{'api-key':API_KEY})
    sec_names_json = res.json().get('results')

    sec_names_list = []

    #Checking if the API returned the expected output (this code will break if it doesn't)
    try:
        sec_names_list = [sec['section'] for sec in sec_names_json]
        #Removing sections that we may not want to document (see: 'admin')
        sec_names_list.remove('admin')
        sec_names_list.remove('multimedia/photos') #Seems like an error 400 hitting this.
        #These values seem to return valid null results, and their removal is purely cosmetic.
        sec_names_list.remove('universal')
        sec_names_list.remove("today’s paper")
        sec_names_list.remove("the weekly")
        full_pbar = tqdm(range(len(sec_names_list)),desc="Overall progress")
    except:
        print('The API malfunctioned and did not return any results. Data acquisition postponed.')


    #Step 2: Get an output for each section and send it to MongoDB.

    for sec in sec_names_list:

        print(f'\n\nProcessing the section "{sec}" from the NYT Newswire API')
        add_section_output(sec)
        full_pbar.update()
        #print(f'Section "{sec}" processed.\n')

if __name__=='__main__':
    if API_KEY is None:
        print('''Please generate an API key at https://developer.nytimes.com/ and add it to your environment variables as follows:

    export "NYTIMES_API_KEY=<your_api_key>"

Please run this script after performing this step.''')
    else:
        print("Performing data acquisition routines from the New York Times' TimesWire API.")
        get_full_newswire_output()