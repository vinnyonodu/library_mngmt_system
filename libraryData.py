"""
@author: vincent onodu

"""

import sqlite3
import json


conn = sqlite3.connect("libsystem.db", timeout=45)  # connects to the libsystem.db via sqlite3
c = conn.cursor() 

c.execute("DROP TABLE IF EXISTS books")     # deletes the books table in the libsystem.db for a fresh start for every project launch instance (to also prevent unique constraint issues upon loading books)
c.execute("""CREATE TABLE IF NOT EXISTS  books(  
    bookID	INTEGER PRIMARY KEY AUTOINCREMENT,
    title	TEXT(255),
    author	TEXT(255),
    average_rating	INTEGER(5),
    isbn	INTEGER(10),
    isbn13	INTEGER(15),
    language_code	TEXT(7),
    num_pages	INTEGER(5),
    ratings_count	INTEGER(10),
    text_reviews count	INTEGER(10),
    publication_date TEXT(20),
    publisher	TEXT(200),
    available	INTEGER(3),
    isDeleted  BOOLEAN
    )""")         # immediately creates the books table to get ready for accepting books from the json file into the db
print('Table is ready')

c.execute("DROP TABLE IF EXISTS borrow")
c.execute("""CREATE TABLE IF NOT EXISTS  borrow(  
    id 	INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id	INTEGER(10),
    book_id	INTEGER(10),
    isReturned BOOLEAN,
    date_borrowed INTEGER,
    date_returned INTEGER,
    fine_amount INTEGER,
    FOREIGN KEY("user_id") REFERENCES "user"("id"),
    FOREIGN KEY("book_id") REFERENCES "books"("bookID")
    )""")
print('Table is ready')

c.execute("DROP TABLE IF EXISTS reserve")
c.execute("""CREATE TABLE IF NOT EXISTS  reserve (  
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id	INTEGER(10),
    book_id	INTEGER(10),
    FOREIGN KEY("user_id") REFERENCES "user"("id"),
    FOREIGN KEY("book_id") REFERENCES "books"("bookID")
    )""")
print('Table is ready')

class LibraryDB:
    @staticmethod
    def insertBook(b):
        # with conn:
        c.execute("INSERT INTO books VALUES(:bookID,:title,:authors,:average_rating,:isbn,:isbn13,:language_code,:num_pages,:ratings_count,:text_reviews_count,:publication_date,:publisher,:available,:isDeleted)",
                  {'bookID':b['bookID'],'title':b['title'],'authors':b['authors'],'average_rating':b['average_rating'],'isbn':b['isbn'],'isbn13':b['isbn13'],'language_code':b['language_code'],'num_pages':b['num_pages'],'ratings_count':b['ratings_count'],
                   'text_reviews_count':b['text_reviews_count'],'publication_date':b['publication_date'],'publisher':b['publisher'],'available':b['available'], 'isDeleted':b['isDeleted']})
        

    @staticmethod
    def loadBooks():
        with open('books.json', 'r', encoding="utf-8") as data:
            books = json.load(data)
            for book in books:
                book['available'] = 1      # adds the value for the 'available' field that is not present in the books.json file for every book into the db
                book['isDeleted'] = False  # adds the value for the 'isDeleted' field that is not present in the books.json file for every book into the db
                LibraryDB.insertBook(book)      # to insert every book in the books.json file into the DB
        print('Inserting Books...') 
        print('*'*30 + '\n\n') 
        conn.commit()                # commits/saves the db execution
        # conn.close()

       
    @staticmethod
    def searchBook():
        searchValue = input('Please enter enter your search data:  ')             
        conn = sqlite3.connect("libsystem.db")
        c = conn.cursor()
        searchValue = '%' + searchValue + '%'
        c.execute(""" 
                  SELECT title,author,isbn,language_code,publication_date from books
                  WHERE title like :s
                  or author like :s
                  or isbn like :s
                  or language_code like :s
                  or publication_date like :s
                  """,{'s':searchValue})  # query to get the title,author and isbn from the books table in the libsystem.db
        result = c.fetchall()               # to get all items from the returned table selected in the query
        print('ISBN - Title - Authors - Language code - publication date')
        i = 1
        for book in result:        # for loop to iterate through each book to print value returned 
            print(f"{i} - {book[2]} - {book[0]} - {book[1]} - {book[3]} - {book[4]}")
            i += 1
        conn.commit()
        # conn.close()
        
    
    
    @staticmethod
    def getBookIdByIsbn(isbn):
        c.execute("""
                  select bookID from books
                  where isbn = :isbn          
                  """,{'isbn':isbn})
        result = c.fetchone()
        
        conn.commit()
        return result[0]      # returns the first bookID value in the selected query
    
    
    def checkBookAvailability(bookId):
        c.execute("""
                  select available from books
                  where bookID = :bid          
                  """,{'bid':bookId})
        availableValue = c.fetchone()[0]    # query to get the value of the available column for the selected bookID in the libsystem.db
        conn.commit()
        return availableValue



    def updateAvailibility(number, bookId):     
        c.execute(""" 
                      update books set
                      available = :availableValue
                      where bookID = :bid
                      """ , {'availableValue' :number, 'bid':bookId})       # query to update the value of the available column for the selected bookID in the libsystem.db
        conn.commit()
        # conn.close()
        
    
    @staticmethod
    def borrowBook(userId,bookId,isReturned,date_borrowed,date_returned,fine_amount):
        availableValue = LibraryDB.checkBookAvailability(bookId)   # query to get the value of the available column for the selected bookID in the libsystem.db (bookID is provided as an argument in the function call)
        if availableValue > 0 :                     # to check that only available books can be borrowed
            c.execute("""
                      insert into borrow(id,user_id,book_id,isReturned,date_borrowed,date_returned,fine_amount)
                      values(:id, :uid,:bid,:isReturned,:date_borrowed,:date_returned,:fine_amount)              
                      """,{'id':None,'uid':userId, 'bid':bookId,'isReturned':isReturned,'date_borrowed':date_borrowed,
                      'date_returned':date_returned,'fine_amount':fine_amount})
            conn.commit()                    
            LibraryDB.updateAvailibility(availableValue-1,bookId) # query reduce the value of the available column by 1 for the selected bookID in the libsystem.db
            print('Book is borrowed by you...')

        else:
            print('The book is not available')
            
    @staticmethod
    def reserveBook(userId,bookId):
        availableValue = LibraryDB.checkBookAvailability(bookId)
        if availableValue > 0:                  # to check that only books that are not available can be reserved
            print("Book is available, please proceed to borrow...")
        else:
            c.execute("""
                      insert into reserve(id,user_id,book_id)
                      values(:id, :uid,:bid)              
                      """,{'id':None,'uid':userId, 'bid':bookId})
            conn.commit()
            print('Book is reserved by you...')
            
    def getUserFineValue(userId,bookId):
        c.execute("""
                  select fine_amount from borrow
                  where borrow.user_id = :uid and book_id = :bid         
                  """,{'uid':userId,'bid':bookId})
        fine = c.fetchone()             # query to get the valye of the fine issued to user for the respected book selected
        conn.commit()
        if fine:
            return fine[0]
        else:
            print("You have no Borrow Record...")
        
