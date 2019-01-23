from flask import Flask, send_file, request, jsonify, url_for, render_template, json, make_response, flash, redirect, render_template, session, abort
from flask.json import jsonify
from flask_cors import CORS
import utilities
from APIException import APIException
import config as CONFIG
import rbac
import os, io
import cms
import binascii
import userController
import dataController

app = Flask(__name__)
app.secret_key = 'NOTASECRET'
CORS(app)

bad_request = {'message': 'Bad Request', 'status': '400'}

PORT = 8080

def checkUser(functionReq):
    if not (session.get('logged_in') and session.get('user')):
        return redirect('/login?redirect='+request.url)
    else:
        response = rbac.checkPermission(functionReq, session.get('user'))
        if response :
            return response

@app.route('/home')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        if request.args.get('redirect'):
            return redirect(request.args.get('redirect'))
        session['directory'] = ''
        user = {}
        user['id'] = session['id']
        user['username'] = session['user']
        info = json.dumps(user)
        userOb = {
            'email': session['email'],
            'name': session['user']
        }
        utilities.logger.debug(info)
        return render_template('home.html', value=info, user= userOb)


@app.route('/signin', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        if 'email' in request.form and 'password' in request.form:
            email = request.form['email']
            password = request.form['password']
            user = userController.getUser(email, password)

            if user:
                if 1 == user['verified']:
                    msg = "Please verify you account"
                    return render_template('login.html', state=msg)
                session['user'] = user['username']
                session['logged_in'] = True
                session['id'] = user['user_id']
                session['email'] = str(email)
                return redirect(url_for('home'))
            else:
                msg = 'invalid username or password'
                return render_template('login.html', state=msg)

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    elif request.method == 'POST':
        utilities.logger.debug(request.form)
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        # check password length
        if len(password) < 6:
            msg = 'Password must be 8 charcter long'
            return render_template('signup.html', state=msg)

        # check for g captcha
        if 'g-recaptcha-response' not in request.form:
            msg = ''
            return render_template('signup.html', state=msg)
        user = userController.checkUser(email)

        if user:
            msg = 'Email already exists'
            return render_template('signup.html', state=msg)

        user = userController.addUser(username, email, password)
        if user:
            session['user'] = request.form['username']
            session['logged_in'] = True
            session['id'] = user['user_id']
            session['email'] = str(email)
            # return redirect(url_for('home'))
            msg = "Please verify you account"
            return render_template('login.html', state=msg)
        else:
            msg = 'Unable to process request'
            return render_template('signup.html', state=msg)

@app.route("/logout")
def logout():
    session['logged_in'] = False
    session.pop('id', None)
    return redirect(url_for('userIndex'))


@app.route("/authenticate", methods=['POST'])
def authenticate():
    queryString = request.query_string
    if queryString:
        paramString = queryString.split("&")
        paramMap = {}
        for params in paramString:
            paramVal = params.split("=")
            paramMap[paramVal[0]] = paramVal[1]
        utilities.logger.debug(paramMap)
        if 'id' in paramMap and 'req' in paramMap:
            user_id = paramMap['id']
            emailHash = paramMap['req']
            res = userController.authenticateUser(user_id, emailHash)
            msg = "invalid request"
            if res:
                if res == 0:
                    msg = "Unable to process you request. Please try again later."
                else:
                    msg = "Password resest successful. Please login"
                    return render_template('login.html', state=msg)
            return render_template('forgotPassword.html', state=msg)


@app.route("/forgotpassword", methods=['GET', 'POST'])
def forgotPassword():
    if request.method == 'GET':
        # check query params
        queryString = request.query_string
        if queryString:
            paramString = queryString.split("&")
            paramMap = {}
            for params in paramString:
                paramVal =  params.split("=")
                paramMap[paramVal[0]] = paramVal[1]
            utilities.logger.debug(paramMap)
            if 'id' in paramMap and 'req' in paramMap:
                return render_template('forgotPassword.html', param=queryString)

        return render_template('forgotPassword.html')

    if request.method == 'POST':
        queryString = request.query_string
        if queryString:
            paramString = queryString.split("&")
            paramMap = {}
            # split
            for params in paramString:
                paramVal = params.split("=")
                paramMap[paramVal[0]] = paramVal[1]
            utilities.logger.debug(paramMap)
            if 'id' in paramMap and 'req' in paramMap:
                password = request.form['password']
                user_id = paramMap['id']
                emailHash = paramMap['req']
                res = userController.resetPassword(user_id, emailHash, password)
                msg = "invalid request"
                if res:
                    if res == 0:
                        msg = "Unable to process you request. Please try again later."
                    else:
                        msg = "Password resest successful. Please login"
                        return render_template('login.html', state=msg)
                return render_template('forgotPassword2.html', state=msg)
        utilities.logger.debug(request.form)
        email = request.form['email']
        user = userController.checkUser(email)
        if user:
            userController.forgotPassword(user)
        msg = "Please check  you mailbox"
        return render_template('forgotPassword.html', state = msg)

@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    # checkUser()
    if request.method == 'GET':
        return render_template('upload.html')
    if request.method == 'POST':
        fullPath = None
        if 'fullPath' in request.form:
            fullPath = request.form['fullPath']
        uploadFile = request.files['file']
        if session['logged_in']:
            id = str(session['id'])
            project = str(session['projectId'])
            reponse = cms.uploadtoGCP(id, project, uploadFile, fullPath)
            return 'file uploaded successfully'

@app.route('/download/<filename>', methods=['GET'])
def download(filename):
    utilities.logger.debug("chan")	
    if request.method == 'GET':
        if session.get('logged_in'):
            user_id = str(session['id'])
            projectId = str(session['projectId'])
    mainpath = "/" + user_id + "/" + projectId + "/"
    utilities.logger.debug(mainpath)	
    f = cms.download(mainpath)
    return send_file(f, attachment_filename= filename)

@app.route('/project/<projectname>', methods=['GET'])
def project(projectname):
    if not session.get('logged_in'):
        return render_template('login.html')

    if not int(projectname):
        return 'received', 200
    directoryInfo = cms.getProjectInfo(projectname, str(session['id']))
    session['projectId'] = str(projectname)
    user_id = str(session['id'])
    directory = ''
    if 'directory' in session:
        directory = session['directory']
    directoryInfo = cms.getDirectoryGCP(user_id, projectname, directory)
    if 'directoryId' in session:
        pass
    info = json.dumps(directoryInfo)
    meta = dataController.getProject(projectname, user_id)
    pkgDir = meta['package']
    is_submitted = meta['is_submitted']	
    is_completed = meta['is_completed']	
    utilities.logger.debug(pkgDir)
    utilities.logger.debug("is_completed" + is_completed)
    utilities.logger.debug("is_submitted" + is_submitted)	
    userOb = {
        'email': session['email'],
        'name': session['user']
    }
    if pkgDir != None and pkgDir != 'None' :
        pkgDir = pkgDir.replace('/', '~slash~')
        return render_template('project.html', value = info, object = meta, user= userOb, package=pkgDir, is_completed = is_completed)
    return render_template('project.html', value=info, object=meta, user=userOb, is_completed = is_completed)

@app.route('/api/user/project/<userId>', methods=['GET', 'POST'])
def userProjectAPI(userId):
    try:
        userid = str(userId)
        if request.method == 'GET':
            if session.get('logged_in'):
                # metaJson = jsonify(meta)
                projectInfo= dataController.getUserProjectInfo(userid)
                return jsonify(projectInfo)
        if request.method == 'POST':
            if not session.get('logged_in'):
                return jsonify({"status": 401, "data": "unauthorized"}, 401)
            projectName = 'MyProject'
            requestJSON = request.get_json()
            operationReq = requestJSON['data']
            utilities.logger.debug(operationReq)
            if 'operation' not in operationReq:
                # operatoin key missing, invalid request
                return jsonify({"status": 400, "data": "invalid request"}, 400)
            if 'add' == operationReq['operation']:
                name = str(operationReq['name'])
                description = str(operationReq['description'])
                package = str(operationReq['package'])
                if (userid == str(session['id'])):
                    dataController.addUserProjectInfo(userid, name, description,package)
                    projectInfo= dataController.getUserProjectInfo(userid)
                    utilities.logger.debug(projectInfo)
                    return jsonify(projectInfo)
            if 'delete' == operationReq['operation']:
                name = str(operationReq['name'])
                id = str(operationReq['id'])
                if (userid == str(session['id'])):
                    dataController.deleteUserProjectInfo(userid, name, id)
                    projectInfo= dataController.getUserProjectInfo(userid)
                    utilities.logger.debug(projectInfo)
                    return jsonify(projectInfo)
            if 'rename' == operationReq['operation']:
                name = str(operationReq['name'])
                id = str(operationReq['id'])
                if (userid == str(session['id'])):
                    dataController.renameUserProjectInfo(userid, name, id)
                    projectInfo= dataController.getUserProjectInfo(userid)
                    utilities.logger.debug(projectInfo)
                    return jsonify(projectInfo)
            if 'update' == operationReq['operation']:
                name = str(operationReq['name'])
                description = str(operationReq['description'])
                id = str(operationReq['id'])
                if (userid == str(session['id'])):
                    dataController.updateUserProjectInfo(userid, id, name, description)
                    projectInfo= dataController.getUserProjectInfo(userid)
                    utilities.logger.debug(projectInfo)
                    return jsonify(projectInfo)

    except Exception as e:
        return str(e)

@app.route('/api/project/<projectname>', methods=['GET'])
def projectAPI(projectname):
    if request.method == 'GET':
        if session.get('logged_in'):
            user_id = session['id']
            directoryInfo = dataController.getProject(projectname, user_id)
            return jsonify(directoryInfo)

@app.route('/api/directory/', methods=['GET', 'POST'])
@app.route('/api/directory/<directoryId>', methods=['GET', 'POST'])
def directoryAPI(directoryId=''):
    utilities.logger.debug(request)
    if request.method == 'GET':
        if session.get('logged_in'):
            projectname = str(session['projectId'])
            user_id = str(session['id'])
            directoryId = str(directoryId).replace('~slash~', '/')
            session['directory'] = directoryId
            directoryInfo = cms.getDirectoryGCP(user_id, projectname, directoryId, True)
            return jsonify(directoryInfo)


@app.route('/razorpaycheckout', methods=['GET'])
def rzr_checkout():
    return render_template('./razorpayCheckout.html')

@app.route('/razorpay/payment', methods=['GET'])
def rzr_payment():
    return render_template('./razorpayCheckout.html')


@app.route('/api/makeApi/<projectId>', methods=['POST'])
def getFiles(projectId):
    utilities.logger.debug('get files')
    if session.get('logged_in'):
        user_id = str(session['id'])
        req = request.get_json()
        pkgList = ''
        count = 0
        utilities.logger.debug(pkgList)
        utilities.logger.debug(req['data']['packageList'])
        for x in req['data']['packageList']:
            utilities.logger.debug (x)
            if count == 0:
                count += 1
                pkgList = str(x)
            else:
                pkgList += ',' + str(x)

        utilities.logger.debug(pkgList)
        directoryInfo = cms.updateProjectQueue(user_id, projectId, pkgList)
        # info = json.dumps(directoryInfo)
        # directoryInfo = cms.getDirectoryInfo(directoryId)
        # metaJson = jsonify(meta)
        return jsonify(directoryInfo)

@app.route('/', methods=['GET', 'POST', 'PATCH', 'PUT', 'DELETE'])
def userIndex():
    if request.method == 'GET':
        userOb = None
        if 'user' in session and 'email' in session and 'id' in session:
            userOb = {
                'email': session['email'],
                'name': session['user']
            }

        return render_template('index.html', user=userOb)

@app.errorhandler(APIException)
def handleAPIException(error):
    utilities.logging.error(str(error))
    response = str(error.toDict())
    response.status_code = error.statusCode
    return response


@app.errorhandler(404)
def handle404Error(error):
    utilities.logging.error(str(error))
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080, debug=True)