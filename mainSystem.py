"""
@author: vincent onodu

"""

from staff import Staff
from student import Student
from libarian import Libarian
from libraryData import LibraryDB
from User import User
import time



class LibManagementSystem:
    def __init__(self):
        LibraryDB.loadBooks()       #This is an action to load all books present in the books.json file into the system db (libsystem.db)
        User.loadUsers()         #This is an action to load all users present in the accounts.json file into the system db (libsystem.db)
        while True:
            LibManagementSystem.userConfirmation()    #This action launches a confirmation screen for new or existing users
            
    def userConfirmation():
        print(f"""    Select Login, If you are an existing user
                  1. Option 1 ~Login
                  2. Option 2 ~Register              
                  q. Return
            """)
        while True:
            c = input("\nSelect Option (1-2|q): ")
            choice = {"1" :LibManagementSystem.login,
                  "2" :LibManagementSystem.register,
                  "q" :"q"}.get(c,"invalid")        
            if choice == "q":
                print('See you next time...')
                break
            elif choice != "invalid":
                choice()
            else:
                print("Try again...")
                
    def register():
        id = input('Enter id: ')
        name = input('Enter name: ').capitalize()   #capitalize() to change the first letter to upper case letters
        password = input('Enter password: ')
        role = input('Enter role (staff/student/Libarian): ').capitalize()
        department = input('Enter department: ').capitalize()
        details = {'id': id,'password': password, 'first_name': name,  'role': role, 'dept': department}
        User.insertUser(details)    # inserts new user into the system db (libsystem.db)
        print('\n')
        print('*'*20,'Registration successful!','*'*20)
        print('\n')
        time.sleep(1)
        LibManagementSystem.login()   # Lanches the login screen upon registration success
    
    def login():        
        while True:
            print("\nWelcome to BCU Library management system")
            firstName = input("Enter first Name: ").capitalize()
            password = input("Enter your password: ")
            result = User.authenticate(firstName, password)   # calls authenticate function in the user class to confirm user input details
            print(result)
            if result['IsExist'] == True:
                print(f'''Welcome {result['First Name']}...''')
                if result['Role'] == 'Student':   # to check and launch the student menu from the student class if user role is of type 'student'
                    print(result['id'])
                    m = Student(result['id'])
                    menu = m.menu()
                elif result['Role'] == 'Staff':  # to check and launch the staff menu from the staff class if user role is of type 'staff'
                    n = Staff(result['id'])
                    menu = n.menu()
                elif result['Role'] == 'Libarian':   # to check and launch the libarian menu from the libarian class if user role is of type 'libarian'
                    o = Libarian(result['id'])
                    menu = o.menu()
            else:
                print('Wrong credentials, Login Failed...')
                

            
        

    
             
LibManagementSystem()
        
