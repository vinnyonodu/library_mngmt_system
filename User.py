"""
@author: vincent onodu

"""

import sqlite3
import json


conn = sqlite3.connect('libsystem.db', timeout=45) # connects to the libsystem.db via sqlite3
c = conn.cursor()

c.execute("DROP TABLE IF EXISTS user")   # deletes the user table in the llibsystem.db for a fresh start for every project launch instance (to also prevent unique constraint issues upon loading users)
c.execute("""CREATE TABLE IF NOT EXISTS  user(  
    id  INTEGER(10) PRIMARY KEY,
    password	TEXT(255),
    first_name	TEXT(255),
    role	TEXT(255),
    dept	TEXT(255)
    )""")                               # immediately creates the user table to get ready for accepting users from the json file into the db
print('Table is ready')

class User:    
    def __init__(self, id):
        self.id = id
        
    @staticmethod
    def authenticate(firstName, password):
        conn = sqlite3.connect("libsystem.db")
        c = conn.cursor()
        c.execute(""" 
                  select id,first_name,role from user
                  where first_name = :firstName
                  and password = :pass
                  """,{'firstName':firstName , 'pass':password})  # query to get the id,first name and role fromt the user table in the libsystem.db
        result = c.fetchone()  # to get just one item (the first item) from the returned table selected in the query
        
        if result:                              # if result gives a value in the db, return the value in the dictionary statement
            return {'IsExist' : True , 'id': result[0] , 'First Name': result[1], 
                    'Role': result[2]}     
        else:
            return {'IsExist' : False}
        conn.commit()             # commits/saves the db execution

        
    @staticmethod
    def insertUser(b): 
        # with conn:
        c.execute("INSERT INTO user VALUES(:id,:password,:first_name,:role,:dept)", {'id':b['id'],'password':b['password'],'first_name':b['first_name'],'role':b['role'],'dept':b['dept']})
        conn.commit()
        

    @staticmethod
    def loadUsers():
       with open('accounts.json', 'r', encoding="utf-8") as data:
           accounts = json.load(data)
           for account in accounts:
               User.insertUser(account)    # to insert every user in the accounts.json file into the DB
       print('Inserting Users...') 
       print('*'*30 + '\n\n') 
       conn.commit()
       # conn.close()
       
       
