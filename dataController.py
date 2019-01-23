from netrc import netrc

import utilities
import dbconnect

def getCustomer(userId, password):
    data = {}
    query = "SELECT username, email, user_id, verified  FROM users where email= '"+ str(userId) + "' and password = '" + password + "'"
    result = dbconnect.getData(query)
    if result:
        result_set = result.fetchall()
        for row in result_set:
            data['username'] = row[0]
            data['email'] = row[1]
            data['user_id'] = row[2]
            data['verified'] = row[3]
            return data
        return None
    else:
        return None

def updateCustomer(name, email, password):
    data = {}
    query = 'UPDATE users set username =' +name + ', email = ' + email + ', password = ' + password +', modifiedat = now()))'
    result = dbconnect.setData(query)
    return result


def addCustomer(name, email, password):
    data = {}
    query = "INSERT INTO users (username, email, password, createdat, modifiedat) values ( '" +name + "', '" + email + "', '" + password + "', now(), now())"
    result = dbconnect.setData(query)
    if result:
        data = {
            'user_id': result,
            'username': name,
            'email': email,
        }
        return data
    else:
        return None

def getUserProjectInfo(user_id):
    #chandra query = "SELECT user_id, name, description, library, path, id, createdat device FROM project where user_id="+ str(user_id)
    query = "SELECT user_id, name, description, library, path, id, createdat, is_submitted, is_completed device FROM project where user_id="+ str(user_id)	
    result = dbconnect.getData(query)
    if result:
        projects = []
        result_set = result.fetchall()
        for row in result_set:
            data = {}
            data['user_id'] = row[0]
            data['name'] = row[1]
            data['description'] = row[2]
            data['library'] = row[3]
            data['path'] = row[4]
            data['id'] = row[5]
            data['createdAt'] = row[6]
            data['is_submitted'] = str(row[7])
            data['is_completed'] = str(row[8])				
            projects.append(data)
        if len(projects) > 0:
            return projects
        else:
            return None
    else:
            return None


def getProject(projectId, user_id):
    data = {}
    #chandra query = 'SELECT id, name, description, createdat, package  FROM project where id='+ str(projectId) + ' and user_id = ' + str(user_id)
    query = 'SELECT id, name, description, createdat, package, is_submitted, is_completed  FROM project where id='+ str(projectId) + ' and user_id = ' + str(user_id)	
    result = dbconnect.getData(query)
    result_set = result.fetchall()
    for row in result_set:
        data['id'] = str(row[0])
        data['name'] = str(row[1])
        data['description'] = str(row[2])
        data['createdAt'] = str(row[3])
        data['package'] = str(row[4])
        data['is_submitted'] = str(row[5])
        data['is_completed'] = str(row[6])		
    if data:
        return data
    else:
        return None


def addProject(name, description):
    data = {}
    query = 'INSERT INTO project (name, description, createdat, modifiedat) values ( ' +name + ', ' + description + ', now(), now())'
    result = dbconnect.setData(query)
    result_set = result.fetchall()
    for row in result_set:
        data['os'] = row[0]
        data['device'] = row[1]
    if data:
        return data
    else:
        return None


def updateProject(name, description, rootDirectory):
    data = {}
    query = 'UPDATE projects set name = ' +name + ', description= ' + description + ', path = '+ rootDirectory +', modifiedat = now())'
    result = dbconnect.setData(query)
    result_set = result.fetchall()
    for row in result_set:
        data['os'] = row[0]
        data['device'] = row[1]
    if data:
        return data
    else:
        return None


def addUserDirectory(email, dirHash):
    return None


def addUserProjectInfo(userid, name, description, package):
    data = {}
    query = "INSERT INTO project (user_id, name, description, package, createdat, modifiedat) values ( " + userid +",'" + name + "', '" + description + "', '" + package + "', now(), now())"
    result = dbconnect.setData(query)
    if result :
        return data
    else:
        return None


def deleteUserProjectInfo(userid, name, id):
    data = {}
    query = "DELETE FROM project WHERE user_id=" + userid + " and  id = " + id + " and name = '" + name + "'"
    result = dbconnect.setData(query)
    if result:
        return data
    else:
        return None


def renameUserProjectInfo(userid, name, id):
    data = {}
    query = "UPDATE project SET name = '" + name + "', modifiedat = now() where user_id=" + userid + " and  id = " + id
    result = dbconnect.setData(query)
    if result:
        return data
    else:
        return None


def updateUserProjectInfo(userid, id, name, description):
    data = {}
    query = "UPDATE project SET name = '" + name + "', description = '"+ description +"', modifiedat = now() where user_id=" + userid + " and  id = " + id
    result = dbconnect.setData(query)
    if result:
        return data
    else:
        return None



def updateProjectQueue(user_id, Project_id, path, library):
    data = {}
    #query = "INSERT INTO queue (user_id, project_id, folder_path) values (" + user_id + " , "+ Project_id +" , '"+ path+ "')"
    query = "INSERT INTO queue (user_id, project_id, library, folder_path) values (" + user_id + " , "+ Project_id +" , '"+ library + "' , '"+ path+ "')"
    result = dbconnect.setData(query)
    if result:
        return result
    else:
        return None


def checkCustomer(email):
    query = "SELECT user_id, email FROM users where email='" + str(email)+"'"
    result = dbconnect.getData(query)
    if result:
        projects = []
        result_set = result.fetchall()
        for row in result_set:
            data = {}
            data['user_id'] = row[0]
            data['email'] = row[1]
            return data
    else:
        return None


def getUserById(user_id):
    query = "SELECT user_id, email FROM users where user_id=" + str(user_id)
    result = dbconnect.getData(query)
    if result:
        projects = []
        result_set = result.fetchall()
        for row in result_set:
            data = {}
            data['user_id'] = row[0]
            data['email'] = row[1]
            return data
    else:
        return None


def resetPassword(user_id, newPasswordHash):
    data = {}
    query = "UPDATE user SET password = '" + newPasswordHash+ "' where user_id=" + user_id
    result = dbconnect.setData(query)
    if result:
        return data
    else:
        return None


def setUserAuthentication(user_id):
    data = {}
    query = "UPDATE user SET verified = 1 where user_id=" + user_id
    result = dbconnect.setData(query)
    if result:
        return data
    else:
        return None
    return None


def updateProjectPackage(id, library):
    #query = "update project set library = '"+library+"' where id = " + str(id)
    query = "update project set library = '"+library+"', is_submitted = '" + '1' + "' where id = " + str(id)	
    dbconnect.setData(query)
    return None