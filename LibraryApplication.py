import sqlite3
conn = sqlite3.connect('library.db')

def get_number_input(prompt):
    while True:
        try:
            user_input = int(input(prompt))
            return user_input
        except ValueError:
            print("Invalid input. Please follow the provided format.")

def askIfUser():
    end_loop = 0
    while end_loop == 0:
        ifUser = input("Are you a user in the system? Enter 1 for yes, 2 for no: ")
        if ifUser == "1":
            userID = input("Enter your user ID: ")
            return userID
        elif ifUser == "2":
            cur = conn.cursor()
            print("Opened database successfully \n")

            cur.execute("SELECT MAX(userID) FROM Users")

            newID = cur.fetchone()[0] + 1
            name = input("You must first register as a user, enter your name: ")
            email = input("Enter your email: ")
            phoneNumber = get_number_input("Enter your phone number, only enter numbers: ")
    
            cur.execute("INSERT INTO Users (userID, userName, email, phoneNumber) VALUES (?, ?, ?, ?)",(newID, name, email, phoneNumber))
            conn.commit()
            print("You have been successfully added into the system")
            return [newID, name, email, phoneNumber]

        else:
            print("Incorrect input, try again")

def findItem():
    cur = conn.cursor()
    print("Opened database successfully \n")
    print("All items in library (Some may be borrowed): \n")
    itemsQuery = "SELECT * FROM Items WHERE itemID NOT IN (SELECT itemID FROM FutureItems)"
    cur.execute(itemsQuery)
    items = cur.fetchall()
    if items:
        for item in items:
            print("Name: " + item[1])
            print("Creator: " + item[2] + "\n")
    else:
        print("We do not have any items at this time\n")
    
    itemName = input("Enter the item's name: ")
    myQuery = "SELECT * FROM Items WHERE itemTitle=:itemName AND itemID NOT IN (SELECT itemID FROM FutureItems) AND itemID NOT IN (SELECT itemID FROM Borrowing)"
    cur.execute(myQuery,{"itemName":itemName})
    rows = cur.fetchall()
    if rows:
        print("We do have the item: " + itemName)
        for row in rows:
            print("ID: " + str(row[0]))
            print("Name: " + row[1])
            print("Creator: " + row[2])
            print("Genre: " + row[3])
            print("Format: " + row[4])
    else:
        print("Unfortunately, we do not have " + itemName + ", it has been borrowed")
    return

def findAvailableItem():
    cur = conn.cursor()
    print("Opened database successfully \n")
    availItemsQuery = "SELECT * FROM Items WHERE itemID NOT IN (SELECT itemID FROM FutureItems) AND itemID NOT IN (SELECT itemID FROM Borrowing)"
    cur.execute(availItemsQuery)
    rows = cur.fetchall()
    if rows:
        for row in rows:
            print("ID: " + str(row[0]))
            print("Name: " + row[1])
            print("Creator: " + row[2] + "\n")

    else:
        print("Unfortunately, there are no available items")
    return

def borrowItem():
    cur = conn.cursor()
    print("Opened database successfully \n")
    itemID = input("Enter the item's ID, if you do not have it use the find item function: ")

    cur.execute("SELECT * FROM Items WHERE itemID = ? AND itemID NOT IN (SELECT itemID FROM FutureItems) AND itemID NOT IN (SELECT itemID FROM Borrowing)", (itemID, ))
    rows = cur.fetchall()
    if rows:
        print("We do have that item")
    else:
        print("Unfortunately, we do not have that item. It may be borrowed or currently unavailable")
        return

    userID = askIfUser()[0]
    
    cur.execute("SELECT DATE('now', '+14 days')")
    dueDate = cur.fetchone()[0]

    cur.execute("SELECT MAX(borrowingID) FROM Borrowing")
    newID = cur.fetchone()[0] + 1
    cur.execute("INSERT INTO Borrowing (borrowingID, itemID, userID, dueDate) VALUES (?, ?, ?, ?)", (newID, itemID, userID, dueDate))
    conn.commit()
    print("You have successfully borrowed an item from the library. The due date is: " + dueDate)
    return

def returnItem():
    cur = conn.cursor()
    print("Opened database successfully \n")
    userID = input("Enter your user ID: ")
    itemID = input("Enter the item's ID, if you do not have it use the find item function: ")

    cur.execute("SELECT * FROM Borrowing WHERE itemID = ? AND userID = ?", (itemID, userID))
    rows = cur.fetchall()

    if rows:
        borrowingID = rows[0][0]
        dueDate = rows[0][3]
        cur.execute("SELECT DATE('now')")
        curDate = cur.fetchone()[0]
        # curDate = '2024-12-12' for testing overdue items

        if curDate > dueDate:
            cur.execute("SELECT MAX(fineID) FROM Fines")
            newID = cur.fetchone()[0] + 1
            cur.execute("SELECT DATE('now', '+7 days')")
            fineDate = cur.fetchone()[0]
            
            cur.execute("SELECT * FROM Fines WHERE borrowingID = ?", (borrowingID, ))
            tuples = cur.fetchall()
            
            if tuples:
                fineAmount = tuples[0][2]
                print("Your item is overdue and you must pay $" + str(fineAmount) + " before returning")
                end_loop = 0
                while end_loop == 0:
                    payment = input("Insert $" + str(fineAmount) + " into the machine (Insert the exact number only, no symbols): ")
                    if payment == str(fineAmount):
                        cur.execute("DELETE FROM Fines WHERE borrowingID = ?", (borrowingID, ))
                        conn.commit()
                        print("Thank you, payment successful and fine is paid")
                        end_loop+=1
                    else:
                        print("Incorrect amount, try again")
                    
                cur.execute("DELETE FROM Borrowing WHERE itemID = ? AND userID = ?", (itemID, userID))
                conn.commit()
                print("Item has been returned")
                return

            print("Your item is overdue and a fine of $10 will be added to your account")
            cur.execute("INSERT INTO Fines (fineID, borrowingID, fineAmount, fineDate) VALUES (?,?,'10',?)", (newID, borrowingID, fineDate))
            conn.commit()
            cur.execute("SELECT * FROM Fines WHERE borrowingID = ?", (borrowingID, ))
            tuplesNew = cur.fetchall()
            fineAmount = tuplesNew[0][2]
            print("You must pay the fine first before returning")
            
            end_loop = 0
            while end_loop == 0:
                payment = input("Insert $" + str(fineAmount) + " into the machine (Insert numbers only, no symbols): ")
                if payment == str(fineAmount):
                    cur.execute("DELETE FROM Fines WHERE borrowingID = ?", (borrowingID, ))
                    conn.commit()
                    print("Thank you, payment successful and fine is paid")
                    end_loop+=1
                else:
                    print("Incorrect amount, try again")
                    
            cur.execute("DELETE FROM Borrowing WHERE itemID = ? AND userID = ?", (itemID, userID))
            conn.commit()
            print("Item has been returned")

        else:
            print("Thank you for returning the item")
            cur.execute("DELETE FROM Borrowing WHERE itemID = ? AND userID = ?", (itemID, userID))
            cur.execute("DELETE FROM Fines WHERE borrowingID = ?", (borrowingID, ))
            conn.commit()
    else:
        print("Incorrect information, try again")

def donateItem():
    cur = conn.cursor()
    print("Opened database successfully \n")
    
    cur.execute("SELECT MAX(itemID) FROM Items")
    
    newID = cur.fetchone()[0] + 1
    itemName = input("Enter the item's name: ")
    creatorName = input("Enter the creator's name: ")
    genre = input("Enter the genre of the item: ")
    itemFormat = input("Enter the format of the item: ")

    cur.execute("INSERT INTO Items (itemID, itemTitle, creatorName, genre, format) VALUES (?, ?, ?, ?, ?)",(newID, itemName, creatorName, genre, itemFormat))
    conn.commit()
    cur.execute("SELECT DATE('now')")
    current_date = cur.fetchone()[0]
    cur.execute("INSERT INTO FutureItems (itemID, arrivalDate) VALUES (?, DATE(?, '+7 days'))", (newID, current_date))
    conn.commit()
    print("You have been successfully donated to the library! There is a 7 day processing period before the item appears on shelves")
    return    
    

def findEvent():
    cur = conn.cursor()
    print("Opened database successfully \n")
    eventName = input("Enter the event's name: ")
    myQuery = "SELECT * FROM Events WHERE eventName=:eventName" 
    cur.execute(myQuery,{"eventName":eventName})
    rows = cur.fetchall()

    if rows:
        print("We do have the event: " + eventName)
        cur.execute("SELECT roomName FROM Rooms WHERE roomID = ?", (rows[0][5], ))
        roomName = cur.fetchone()
    else:
        print("Unfortunately, we do not have the event: " + eventName)

    for row in rows:
        print("ID: " + str(row[0]))
        print("Name: " + row[1])
        print("Description: " + row[2])
        print("Target Audience: " + row[3])
        print("Date: " + row[4])
        print("Room Name: " + roomName[0])
    return


def registerEvent():
    cur = conn.cursor()
    print("Opened database successfully \n")

    userID = askIfUser()
    
    eventName = input("Enter the event's name: ")
    myQuery = "SELECT * FROM Events WHERE eventName=:eventName" 
    cur.execute(myQuery,{"eventName":eventName})
    eventID = cur.fetchall()
    if eventID:
        cur.execute("INSERT INTO EventParticipants (eventID, userID) VALUES (?,?)", (eventID[0][0], userID[0]))
        conn.commit()
        print("You have successfully registered for the event")
    else:
        print("Incorrect information, try again")
    return

    
def volunteerForLibrary():
    cur = conn.cursor()
    print("Opened database successfully \n")
    cur.execute("SELECT MAX(personnelID) FROM Personnel")

    newID = cur.fetchone()[0] + 1
    name = input("Enter your name: ")
    email = input("Enter your email: ")
    phoneNumber = get_number_input("Enter your phone number, only enter numbers: ")

    cur.execute("INSERT INTO Personnel (personnelID, staffName, position, email, phoneNumber) VALUES (?, ?, 'Volunteer', ?, ?)",(newID, name, email, phoneNumber))
    conn.commit()
    print("You have been successfully added into the system")
    return

def askLibrarian():
    cur = conn.cursor()
    print("Opened database successfully \n")
    cur.execute("SELECT * FROM Personnel WHERE position = 'Librarian' OR position = 'Assistant Librarian'")
    rows = cur.fetchall()
    print("Our librarians are: \n")

    for row in rows:
        print("Name: " + row[1])
        print("Email: " + row[3])
        print("Phone Number: " + row[4])
        print("\n")

    print("You may contact any of them through phone or email with any questions you may have")
    print("Have a good day!")
    return
    

    
print("Hi, welcome to SFU Library. What do you need help with today?")
print("Option 1: Find an item in the library")
print("   Option 1.5: Show all available items in the library")
print("Option 2: Borrow an item from the library")
print("Option 3: Return a borrowed item")
print("Option 4: Donate an item to the library")
print("Option 5: Find an event in the library")
print("Option 6: Register for an event in the library")
print("Option 7: Volunteer for the library")
print("Option 8: Ask for help from a librarian")
print("Option 9: Exit Application")
print("\n")

end_loop = 0
selections = ["1","1.5","2","3","4","5","6","7","8","9"]

while end_loop == 0:
    option = input("Enter your choice ( 1 | 1.5 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 ): ")

    if option in selections:
        if option == "1":
            findItem()
            print("\n")

        elif option == "1.5":
            findAvailableItem()
            print("\n")
            
        elif option == "2":
            borrowItem()
            print("\n")
            
        elif option == "3":
            returnItem()
            print("\n")

        elif option == "4":
            donateItem()
            print("\n")
            
        elif option == "5":
            findEvent()
            print("\n")

        elif option == "6":
            registerEvent()
            print("\n")

        elif option == "7":
            volunteerForLibrary()
            print("\n")

        elif option == "8":
            askLibrarian()
            print("\n")
        
        elif option == "9":
            conn.close()
            end_loop+=1
            print("Closed database successfully")

    else: 
        print("Choose a number from 1 to 9") 
    

