# -*- coding: utf-8 -*-
# @Date    : 2022-12-26 15:31
# @Author  : chenxuepeng
from pymongo import MongoClient

Client = MongoClient()
myclient = MongoClient('localhost', 27010)

my_database = myclient["mytasks"]
my_collection = my_database["tasks"]

# number of documents in the collection
mydoc = my_collection.count_documents({})

print("The number of documents in collection : ", mydoc)