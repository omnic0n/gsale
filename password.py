import bcrypt
import getpass

pswd = getpass.getpass('Password:')

# Adding the salt to password
salt = bcrypt.gensalt()
# Hashing the password
hashed = bcrypt.hashpw(pswd.encode('utf8'), salt)

# printing the hashed
print("Hashed")
print(hashed)