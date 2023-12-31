"""
@author: vincent onodu

"""
import sqlite3
from libraryData import LibraryDB
from User import User

conn = sqlite3.connect("libsystem.db")
c = conn.cursor()


class Libarian(User): 
    def __init__(self, id):
        self.id = id          # gets user current session from the mainSystem file

    def menu(self):
        print(f"""      Libarian Menu
                1. Option 1 ~view my Profile
                2. Option 2 ~Search book
                3. Option 3 ~Add Book 
                4. Option 4 ~Delete Book
                5. Option 5 ~Update Book
                6. Option 6 ~View All Books
                7. Option 7 ~View All borrowed Books
                8. Option 8 ~View All reserved Books
                9. Option 9 ~View All registered users
                q. Return
                """)
        while True:
            c = input("\nSelect Option (1-9|q): ")      # Action functions for each respective selected option on the libarian menu
            choice = {"1" :self.viewMyProfile,
                  "2" :self.searchBook,
                  "3" :self.addBook,
                  "4" :self.deleteBook,
                  "5" :self.updateBook,
                  "6" :self.viewAllBooks,
                  "7" :self.viewAllBorrowedBooks,
                  "8" :self.viewAllReservedBooks,
                  "9" :self.viewAllUsers,
                  "q" :"q"}.get(c,"invalid")        
            if choice == "q":
                print('Loging out...')
                break
            elif choice != "invalid":
                choice()
            else:
                print("Wrong input, Try again...")
                
                
    def searchBook(self):
        return LibraryDB.searchBook()           # gets the search book function from the LibraryDB class function gets input from user and returns search results
                    
    def viewMyProfile(self):
        c.execute("""
                  select first_name,role,dept from user
                  where user.id = :uid 
                  """,{'uid':self.id})
        result = c.fetchone()                        # returns user profile details(first name, role, dept) from the libsystem.db
        print(f'''First Name  -  {result[0]}''')
        print(f'''Role  -  {result[1]}''')
        print(f'''Department  -  {result[2]}''')
        conn.commit()
        # conn.close()
        
    def viewAllUsers(self):
        c.execute("""
                  select first_name,role,dept from user
                  """,{'uid':self.id})
        result = c.fetchall()        # returns all registered user details(first name, role, dept) from the user table in the  libsystem.db
        print('first name - role - department')
        i = 1
        for user in result:
            print(f"{i} - {user[0]} - {user[1]} - {user[2]}")
            i += 1
        conn.commit()
        # conn.close()
        

    def viewAllBooks(self):
        c.execute("""
                  select books.title from books
                  """,{'uid':self.id})
        result = c.fetchall()           # returns all book titles from the books table in the  libsystem.db
        print('Title')
        i = 1
        for book in result:
            print(f"{i} - {book[0]}")
            i += 1
        conn.commit()
        # conn.close()
    
    
    @staticmethod
    def getDeletedStatusByIsbn(isbn):
        c.execute("""
                  select isDeleted from books
                  where isbn = :is          
                  """,{'is':isbn})
        result = c.fetchone()       # returns the value of the isDeleted column for the provided isbn from the books table in the libsystem.db
        
        conn.commit()
        return result[0]
    
    def updateIsDeleted(isDeletedValue, isbn):        
        c.execute(""" 
                      update books set
                      isDeleted = :isDeleted
                      where isbn = :isbn
                      """ , {'isDeleted' :isDeletedValue, 'isbn':isbn})       # this updates the isDeleted value for respective book. function call requires the isDeleted value as present in the argument space
        conn.commit()
        # conn.close()
                
    def deleteBook(self):
        isbn = input("Enter Book's ISBN to be deleted:  ")
        isDeletedValue = Libarian.getDeletedStatusByIsbn(isbn)
        if isDeletedValue == False:            # checks an sets the isDeleetd field for respective book to TRUE to signify deleted if the field was  previously false
            Libarian.updateIsDeleted(True, isbn)
            print("The Selected Book has been successfully Deleted...")
        else:
            print("Book is already Deleted...")
        # conn.close()


    @staticmethod
    def getRatingsCountByIsbn(isbn):
        c.execute("""
                  select ratings_count from books
                  where isbn = :is          
                  """,{'is':isbn})
        result = c.fetchone()        # this returns the ratings count tied to the provided isbn present in the libsystem.db
        conn.commit()
        return result[0]
     
    def updateRatingsCount(ratingsCount, isbn):        
        c.execute(""" 
                      update books set
                      ratings_count = :ratingsCount
                      where isbn = :isbn
                      """ , {'ratingsCount' :ratingsCount, 'isbn':isbn})       # this updates the ratings_count value for respective book.
        conn.commit()
        # conn.close()
         
    def updateBook(self):
        isbn = input("Enter Book's ISBN:  ")
        oldRatingsCount = Libarian.getRatingsCountByIsbn(isbn)
        print(f'''old ratings count:{oldRatingsCount}''')
        newRatingsCount = input("Enter New Ratings Count Value:  ")
        print(f'''new ratings count:{newRatingsCount}''')
        Libarian.updateRatingsCount(newRatingsCount, isbn)
        print("The Selected Book has been successfully Updated...")     # updates the value for the ratings count for the respective book
    

    def addBook(self):
        conn = sqlite3.connect("libsystem.db")
        c = conn.cursor()
        print("Please Enter required book details to add a book to the Library...")
        bookId = input("Enter Book's bookId:  ")
        title = input("Enter Book's title:  ")
        author = input("Enter Book's author:  ")
        averageRating = input("Enter Book's averageRating:  ")
        isbn = input("Enter Book's ISBN:  ")
        isbnThirteen = input("Enter Book's isbnThirteen:  ")
        languageCode = input("Enter Book's languageCode:  ")
        noOfPages = input("Enter Book's noOfPages:  ")
        ratingsCount = input("Enter Book's ratingsCount:  ")
        textReviewsCount = input("Enter Book's textReviewsCount:  ")
        publicationDate = input("Enter Book's publicationDate:  ")
        publisher = input("Enter Book's publisher:  ")
        available = input("Enter Book's available:  ")
        deleted = False
        c.execute("INSERT INTO books VALUES(:bookID,:title,:authors,:average_rating,:isbn,:isbn13,:language_code,:num_pages,:ratings_count,:text_reviews_count,:publication_date,:publisher,:available,:isDeleted)",
                      {'bookID':bookId,'title':title,'authors':author,'average_rating':averageRating,'isbn':isbn,'isbn13':isbnThirteen,'language_code':languageCode,'num_pages':noOfPages,'ratings_count':ratingsCount,
                       'text_reviews_count':textReviewsCount,'publication_date':publicationDate,'publisher':publisher,'available':available,'isDeleted':deleted})
        conn.commit()
        # conn.close()
        print("Book has been successfully added to the system...")       # this adds a book record to the books table in the libsystem.db
        
    def viewAllBorrowedBooks(self):
        conn = sqlite3.connect("libsystem.db")
        c = conn.cursor()
        c.execute("""
                  select books.title from books
                  where books.bookID IN (select borrow.book_id from borrow)       
                  """,{'uid':self.id})
        result = c.fetchall()            # returns all borrowed books from the borrow table in the  libsystem.db
        print('Title')
        i = 1
        for book in result:
            print(f"{i} - {book[0]}")
            i += 1
        conn.commit()
        # conn.close()
        
    def viewAllReservedBooks(self):
        conn = sqlite3.connect("libsystem.db")
        c = conn.cursor()
        c.execute("""
                  select books.title from books
                  where books.bookID IN (select reserve.book_id from reserve)       
                  """,{'uid':self.id})
        result = c.fetchall()             # returns all reserved books from the reserved table in the  libsystem.db
        print('Title')
        i = 1
        for book in result:
            print(f"{i} - {book[0]}")
            i += 1
        conn.commit()
        # conn.close()