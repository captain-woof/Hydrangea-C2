import bcrypt
from database.database import HydrangeaDatabase

"""
These functions are meant for Team server administration
"""

# Get existing user by username
def getUserByUsername(db:HydrangeaDatabase, username: str):
    return db.getUserByUsername(username=username)

# Create a new user
def createUser(db:HydrangeaDatabase, username: str, password: str, role: str):
    # Validate role
    if role not in ["admin", "operator", "observer"]:
        return False
        
    # Hash user password
    passwordHash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    
    # Create user
    return db.createUser(username=username, passwordHash=passwordHash, role=role)

# Edit existing user
def editUser(db:HydrangeaDatabase, username: str, changeWhat: str, newValue: str):
    if changeWhat == "username":
        return db.changeUserUsername(username=username, usernameNew=newValue)
    elif changeWhat == "password":
        passwordHash = bcrypt.hashpw(newValue.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        return db.changeUserPassword(username=username, passwordHashNew=passwordHash)
    elif changeWhat == "role":
        return db.changeUserRole(username=username, roleNew=newValue)
    else:
        return False
    
# Delete existing user
def deleteUser(db:HydrangeaDatabase, username: str):
    return db.deleteUser(username=username)