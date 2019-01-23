from flask import make_response


userMap = {
    "admin" : 1
}

permissionMap = {
    1 : ['lead', 'cha']

}

def checkPermission(functionReq, user):
    # get user role
    roleId = userMap[user]

    # get permissionLis
    permissionList = permissionMap[roleId]
    if functionReq in permissionList:
        # permission granted
        print ('permission granted')
    else:
        return make_response("Permission not available",400)