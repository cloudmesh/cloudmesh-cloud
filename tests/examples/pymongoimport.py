import sys
from bson import json_util # Comes with pymongo
from pymongo import MongoClient
from pprint import pprint
import json

client = MongoClient('mongodb://user:user123@ds033499.mongolab.com:33499/enron')
r = MongoClient('mongoimport -h ds033499.mongolab.com:33499 -p 33499'
                        ' -d enron -c spectrumplus -u user -p user123'
                        ' --file C:/Users/sachin/Documents/IPython'
                        '  /ch06-mailboxes/data/enron.mbox.json')
