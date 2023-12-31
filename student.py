"""
@author: vincent onodu

"""

import sqlite3
from libraryData import LibraryDB
from datetime import datetime
import time
from User import User


conn = sqlite3.connect("libsystem.db", timeout=45)  # connects to the libsystem.db via sqlite3
c = conn.cursor() 


class Student(User):
    def __init__(self, id):
        self.id = id            # gets user current session from the mainSystem file
    
       
    def menu(self):
        print(f"""          Student Menu
                  1. Option 1 ~Search book
                  2. Option 2 ~View My Profile
                  3. Option 3 ~Borrow book
                  4. Option 4 ~View my List of borrowed books
                  5. Option 5 ~Reserve book
                  6. Option 6 ~View my List of Reserved books
                  7. Option 7 ~Return Books
                  8. Option 8 ~View my Fine record per book
                  9. Option 9 ~Pay my Fine per book
                  q. Return
            """)
        while True:
            c = input("\nSelect Option (1-9|q): ")   # Action functions for each respective selected option on the student menu
            choice = {"1" :self.searchBook,
                  "2" :self.viewMyProfile,
                  "3" :self.borrowBook,
                  "4" :self.listOfBorrowedBooks,
                  "5" :self.reserveBook,
                  "6" :self.listOfReservedBooks,
                  "7" :self.returnBook,
                  "8" :self.viewFine,
                  "9" :self.finePayment,
                  "q" :"q"}.get(c,"invalid")        
            if choice == "q":
                print('Loging out..')
                break
            elif choice != "invalid":
                choice()
            else:
                print("Wrong input, Try again...")
            
    def searchBook(self):
        return LibraryDB.searchBook()     # gets the search book function from the LibraryDB class function gets input from user and returns search results
    
    
    def viewMyProfile(self):
        c.execute("""
                  select first_name,role,dept from user
                  where user.id = :uid 
                  """,{'uid':self.id})
        result = c.fetchone()               # returns user profile details(first name, role, dept) from the user table in the libsystem.db
        print(f'''First Name  -  {result[0]}''')
        print(f'''Role  -  {result[1]}''')
        print(f'''Department  -  {result[2]}''')       
        conn.commit()
        # conn.close()
    
    def borrowBook(self):
        isbn = input('Please enter isbn: ')
        bookId = LibraryDB.getBookIdByIsbn(isbn)    # this returns the bookID with the isbn provided
        isReturned = False
        c.execute("""
                  select user_id,book_id,isReturned from borrow
                  where user_id = :uid and book_id = :bid       
                  """,{'uid':self.id,'bid':bookId})
        result = c.fetchone()                                # gets the value of user_id,book_id,isReturned tied to the user and book details required from the libsystem.db
        conn.commit()
        dateBorrowed = datetime.now()                        # gets the current date and time that book is borrowed
        dateBorrowed1 = datetime.timestamp(dateBorrowed)            # converts current date and time to a timestamp form
        dateReturned = ""                                    # default value for date returned upon borrowing should be empty
        fineAmount = 0                                  # default value for fine amount upon borrowing should be 0                            
        if result:            
            if result[2] == True:              
                c.execute("""
                          UPDATE borrow SET isReturned = :isReturned, date_borrowed = :date_borrowed
                          where borrow.user_id = :uid     
                          """,{'uid':self.id, 'isReturned':isReturned, 'date_borrowed': dateBorrowed1})   # updates the borrow table with isReturned and date_borrowed columns with respective values for the user
                conn.commit()               # commits/saves the db execution
                print('Book is borrowed by you...')
            else:
                print("You have already borrowed book, return before you can borrow again...")  # this is printed in the console ,if the result[2] which is the isReturned value is False. this means the book has not been returned
        else:
            LibraryDB.borrowBook(self.id, bookId, isReturned,dateBorrowed1,dateReturned,fineAmount)    # runs borrow action when table is empty
            
           
    def listOfBorrowedBooks(self):
        c.execute("""
                  select books.title from books
                  where books.bookID IN (select borrow.book_id from borrow where borrow.user_id = :uid)       
                  """,{'uid':self.id})
        result = c.fetchall()    # returns the list of all the borrowed books by the user
        print('Title')
        i = 1
        for book in result:
            print(f"{i} - {book[0]}")
            i += 1
        conn.commit()
        # conn.close()
        
        
    def reserveBook(self):
        isbn = input('Please enter book isbn: ')
        bookId = LibraryDB.getBookIdByIsbn(isbn)
        LibraryDB.reserveBook(self.id, bookId)  # function in the LibraryDB class reserves book ONLY  when the book is not available
        
        
    def listOfReservedBooks(self):
        c.execute("""
                  select books.title from books
                  where books.bookID IN (select reserve.book_id from reserve where reserve.user_id = :uid)       
                  """,{'uid':self.id})
        result = c.fetchall()    # returns the list of all the reserved books by the user
        print('Title')
        i = 1
        for book in result:
            print(f"{i} - {book[0]}")
            i += 1
        conn.commit()
        # conn.close()
        

    
    def returnBook(self):
        isbn = input('Please enter book isbn: ')
        isReturned = True
        bookId = LibraryDB.getBookIdByIsbn(isbn)       # this returns the bookID with the isbn provided
        availabilityValue = LibraryDB.checkBookAvailability(bookId)      #  this returns the value of the available field tied to the respective book
        c.execute("""
                  select borrow.isReturned from borrow
                  where borrow.user_id = :uid and book_id = :bid      
                  """,{'uid':self.id,'bid':bookId})
        borrowRecord = c.fetchone()      # returns the isReturned value tied to the user and book details required from the borrow table in the libsystem.db
        conn.commit()
        if borrowRecord and borrowRecord[0] == False:   # this statement ONLY runs when there is a borrowed record and when the isReturned value is false. this signifies that the book has not yet been returned
            dateReturned = datetime.now()               # gets the current date and time that book is returned
            dateReturned1 = datetime.timestamp(dateReturned)            # converts current date and time to a timestamp form        
            LibraryDB.updateAvailibility(availabilityValue+1,bookId)             # increases the book availability by 1
            c.execute("""
                      UPDATE borrow SET isReturned = :isReturned, date_returned = :date_returned
                      where borrow.user_id = :uid and borrow.book_id = :bid 
                      """,{'uid':self.id, 'bid':bookId,'isReturned':isReturned, 'date_returned': dateReturned1})
            conn.commit()
            print("Book Return in process...")
            time.sleep(1)
            c.execute("""
                      select borrow.date_borrowed, borrow.date_returned, borrow.fine_amount from borrow
                      where borrow.user_id = :uid and book_id = :bid      
                      """,{'uid':self.id,'bid':bookId})
            result2 = c.fetchone()
            conn.commit()
            differenceBetweenDates = result2[1] - result2[0]    # gets the differences between the borrowed date and the returned date . This is required to calculate and issue a FINE
            print("Please Note: You will be issued a fine if you return book later than 15secs after borrowing")
            if differenceBetweenDates > 15.0:     # to check that ONLY users that returns books greater than the due period of 15secs is FINED
                fineIssued = 20                      # FLAT FINE RATE
                newTotalFine = result2[2] + fineIssued           # to get the new total after the addition of the fine
                c.execute("""
                          UPDATE borrow SET fine_amount = :fine_amount
                          where borrow.user_id = :uid and borrow.book_id = :bid   
                          """,{'uid':self.id,'bid':bookId, 'fine_amount': newTotalFine})
                conn.commit()                
                print(f'''
                      
                      Time taken before return :   {differenceBetweenDates}secs                      
                      Book has been successfully returned By you with {newTotalFine}GBP fine issued
                      ''')
            else:
                print(f'''Time taken before return :   {differenceBetweenDates}secs''')                
                print("Book has been successfully returned By you with 0GBP fine issued")
            # conn.close()            
        else:
            print("You did not borrow this book...")     # this statement runs when both or either the borrow record does not exist or if the isReturned value is true. this means the book has been returned or was never borrowed
          
            
          
    def viewFine(self):
        isbn = input('Please enter isbn: ')
        bookId = LibraryDB.getBookIdByIsbn(isbn)
        myFine = LibraryDB.getUserFineValue(self.id, bookId)     # this returns the fine present in the fine_amount column for respective user in the libsystem.db 
        if myFine == None:
            myFine = 0
        print(f'''Total fine to be payed for selected book:   {myFine}GB''')
        
        
        
    def finePayment(self):
        isbn = input('Please enter Book isbn: ')
        bookId = LibraryDB.getBookIdByIsbn(isbn)
        myFine = LibraryDB.getUserFineValue(self.id, bookId)     # this returns the fine present in the fine_amount column for respective user in the libsystem.db 
        print(f'''Total fine to be payed for selected book:   {myFine}GB''')
        paymentValue = int(input('Please enter exact fine amount to pay: '))       # requests user to input the exact FINE amount to pay fine
        if paymentValue == myFine:            
            myFine = 0
            c.execute("""
                      UPDATE borrow SET fine_amount = :fine_amount
                      where borrow.user_id = :uid and borrow.book_id = :bid  
                      """,{'uid':self.id,'bid':bookId, 'fine_amount': myFine})
            conn.commit()   # updates the db with the new value for fine_amount for the respective user
            print("You have successfully completed the fine payment.  current amount to be paid: 0GBP")
        else:
            print("Please enter correct fine amount to pay, restart process...")    # this prints to the console when user inputs a value that is NOT the fine amount
    

