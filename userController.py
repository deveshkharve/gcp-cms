import utilities
import dataController
import hashlib
import os
import mailController


def addUser(username, email, password):
    try:
        encr = hashlib.sha256()
        passwordHash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        #check for user
        result = dataController.getCustomer(email, passwordHash)
        if result:
            return None
        result = dataController.addCustomer(username, email, passwordHash)
        if result:
            emailHash = hashlib.sha256(email.encode('utf-8')).hexdigest()
            mailController.sendWelcomeMailer(email, username, result, emailHash)
        return result
    except Exception as e:
        print (str(e))

    return None

def checkUser(email):
    result = dataController.checkCustomer(email)
    #
    # emailHash = hashlib.sha256(result['email'].encode('utf-8')).hexdigest()
    # result['emailHash'] = emailHash
    return result


def getUser(email, password):
    #check for user
    encr = hashlib.sha256()
    passwordHash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    result = dataController.getCustomer(email, passwordHash)
    return result



def addUserDirectory(email):

    dirHash = hashlib.sha256(email).hexdigest()
    length = 32
    if length < len(dirHash):
        dirHash = dirHash[:length]
    result = dataController.addUserDirectory(email, dirHash)
    return result


def getUserDirectory(email):
    #check for user
    result = dataController.getUserDirectory(email)
    return result


def forgotPassword(user):
    user_id = user['user_id']
    email = user['email']
    emailHash = hashlib.sha256(email.encode('utf-8')).hexdigest()
    mailController.sendForgotMailer(user_id, emailHash, email)
    return None


def resetPassword(user_id, emailHash, newPassword):
    user = user = dataController.getUserById(user_id)
    email = user['email']
    userEmailHash = hashlib.sha256(email.encode('utf-8')).hexdigest()
    if (userEmailHash == emailHash):
        print('valid user')
        newPasswordHash = hashlib.sha256(newPassword.encode('utf-8')).hexdigest()
        result = dataController.resetPassword(user_id, newPasswordHash)
        if result:
            return result
        else:
            return 0
    else:
        print('invalid user request')
        return None


def authenticateUser(user_id, emailHash):
    user = dataController.getUserById(user_id)
    if user:
        email = user['email']
        userEmailHash = hashlib.sha256(email.encode('utf-8')).hexdigest()
        if (userEmailHash == emailHash):
            print('valid user')
        data = dataController.setUserAuthentication(user_id)
        return data
    return None