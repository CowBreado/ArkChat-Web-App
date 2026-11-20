import bcrypt 

#Input password
inputt = "pogiEnzo"
#Password converted into bytes
password = inputt.encode('utf-8')


print("Inputted Password: ",inputt)
print("Password but converted to bytes: ",password)

#Encrypt password
password = bcrypt.hashpw(password, bcrypt.gensalt())
print("Encrypted password: ", password.decode())



def check_password(input_password):
    input_password = input_password.encode('utf-8')
    if bcrypt.checkpw(input_password, password):
        print("Matching password")
    else:
        print("Not matching password")
check_password("pogiEnzo")


        