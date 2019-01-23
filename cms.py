import os, io
import gzip
import config as CONFIG
from werkzeug.utils import secure_filename
import utilities
import dataController
# import dbconnect
from google.cloud import storage,client,_helpers


CLOUD_STORAGE_BUCKET = CONFIG.bucket_name

def upload_file(id, uploadFile, fullPath):
        print ('copy to', fullPath)
        dirPath = os.path.join(CONFIG.uploadDir, id)
        fileDir = os.path.dirname(fullPath)
        dirPath = os.path.join(dirPath, fileDir)

        if not os.path.exists(dirPath):
            os.makedirs(dirPath)

        filePath = os.path.join(dirPath, secure_filename(uploadFile.filename))
        uploadFile.save(filePath)
        # s = uploadFile.read()
        # uploadFile.close()
        #
        # outF = gzip.GzipFile(filePath, 'wb')
        # outF.write(s)
        # outF.close()
        # f.save(filePath)
        return 'file uploaded successfully'


# [START upload]
def uploadtoGCP(id, projectId, uploaded_file, fullPath):
    """Process the uploaded file and upload it to Google Cloud Storage."""
    if not uploaded_file:
        return 'No file uploaded.', 400
    # Create a Cloud Storage client.
    gcs = storage.Client('client.ClientWithProject')

    # Get the bucket that the file will be uploaded to.
    bucket = gcs.get_bucket(CLOUD_STORAGE_BUCKET)

    # Create a new blob and upload the file's content.
    dirPath = os.path.join(CONFIG.uploadDir, id)
    dirPath = os.path.join(dirPath, projectId)
    fileDir = os.path.dirname(fullPath)
    dirPath = os.path.join(dirPath, fileDir)

    filePath = os.path.join(dirPath, secure_filename(str(uploaded_file.filename)))
    print (filePath)
    blob = bucket.blob(str(filePath))

    blob.upload_from_string(
        uploaded_file.read(),
        content_type=uploaded_file.content_type
    )

    # The public URL can be used to directly access the uploaded file via HTTP.
    return blob.public_url

def getFileFromGCP(fileName):
    gcs = storage.Client('client.ClientWithProject')
    # Get the bucket that the file will be uploaded to.
    bucket = gcs.get_bucket(CLOUD_STORAGE_BUCKET)
    blob = bucket.get_blob(fileName)
    return blob.download_as_string()

def download(filename):
    try:
        filePath = os.path.join(CONFIG.downloadDir, filename)
        # inF = gzip.GzipFile(filePath, 'rb')
        # s = inF.read()
        s = getFileFromGCP(filePath)
        # tempFilePath = os.path.join(CONFIG.uploadDir, secure_filename(filename))
        f = io.BytesIO(s)
        return f
    except Exception as e:
        utilities.logger.error(str(e), exc_info= True)
        return None


def getDirectoryInfo(directoryId):

    state = {
        "project": {"name": "testProject", "createdAt": "2018-02-03", "description": "my new project", 'is_submitted' : 'true', 'is_completed' : 'true'},
        "files": [{"name": 'new file', "type": 2, "id": 11}, {"name": 'file1', "type": 2, "id": 12},
                  {"name": 'file2', "type": 2, "id": 13}],
        "selectedDir": {"name": 'testProject', "type": 1, "id": 0,'is_submitted' : 'true', 'is_completed' : 'true'},
        "parentDir": {"id": 1, "name": "project"},
    }

    if(0 == directoryId):
        state = {
            "project": {"name": "testProject", "createdAt": "2018-02-03", "description": "my new project", 'is_submitted' : 'true', 'is_completed' : 'true'},
            "files": [{"name": 'folder', "type": 2, "id": 11}, {"name": 'file1', "type": 2, "id": 12}, {"name": 'file2', "type": 2, "id": 13}],
            "selectedDir": {"name": 'folder', "type": 1, "id": 0, 'is_submitted' : 'true', 'is_completed' : 'true'},
            "parentDir": {"id": 1, "name": "testProject"},
        }
    return {}

def getDirectoryGCP(user_id, projectId, directory, fullPath = False):
    """Process the uploaded file and upload it to Google Cloud Storage."""
    user_id = str(user_id)
    projectId =str(projectId)
    directory = str(directory)
    # Create a Cloud Storage client.
    gcs = storage.Client('client.ClientWithProject')

    # Get the bucket that the file will be uploaded to.
    bucket = gcs.get_bucket(CLOUD_STORAGE_BUCKET)

    path = os.path.join(CONFIG.uploadDir, user_id)
    path = os.path.join(path, projectId)
    pId = path
    if directory:
        path = path + directory

    # if fullPath:
    #     path = directory

    selectDir = {'id': path.replace(pId, '').replace('//', '/'), 'name': str(directory)}
    parentDir = {'id': str(os.path.dirname(path)).replace(pId, '').replace('//', '/'), 'name': str(os.path.dirname(directory))}
    state = {}
    state['selectedDir'] = selectDir
    state['parentDir'] = parentDir
    state['files'] = []
    if not path:
        return state
    path_to_dir = path
    if not str(path)[(len(str(path))-1)] == '/':
        path_to_dir = path +"/"
    blobs = bucket.list_blobs(prefix=path_to_dir)
    files = []
    subDirectoryList = []
    for blob in blobs:
        dir = str(os.path.dirname(blob.name))
        if path in os.path.dirname(blob.name):
            file = {'name': '', 'id': 0, 'path': '', 'createdAt': '', 'type': 2}
            if dir == path:
                type = str(blob.content_type)
                name = str(blob.name).replace(path_to_dir, '')
                file['name'] = name
                file['id'] = os.path.dirname(blob.name).replace(pId,'')
                file['type'] = 2
                files.append((file))
            else:
                while str(os.path.dirname(dir)) != path and path in os.path.dirname(blob.name):
                    dir = str(os.path.dirname(dir))
                if str(dir) not in subDirectoryList:
                    subDirectoryList.append(str(dir))
                    file['name'] = os.path.basename(dir)
                    file['id'] = str(dir).replace(pId,'')
                    file['type'] = 1
                    files.append((file))

    # blob = bucket.blob(directory)
    state['files'] = files

    # The public URL can be used to directly access the uploaded file via HTTP.
    return state

def getProjectInfo(projectname, user_id):
    # projectInfo = getProjectInfo()
    state = {
        "meta": {'name': 'test', 'id': '1', 'isEmpty': 'true', 'is_submitted' : 'true', 'is_completed' : 'true'},
        "project": {"name": "testProject", "createdAt": "2018-02-03", "description": "my new project", 'is_submitted' : 'true', 'is_completed' : 'true'},
        "files": [{"name": 'folder', "type": 1, "id": 11}, {"name": 'file1', "type": 2, "id": 12},
                  {"name": 'file2', "type": 2, "id": 13}],
        "selectedDir": {"name": 'testProject', "type": 1, "id": 0 , 'is_submitted' : 'true', 'is_completed' : 'true'},
        "parentDir": {"id": 1, "name": ""},
    }

    return {}

def getPath(user_id, projectId):
    user_id = str(user_id)
    projectId = str(projectId)
    dirPath = os.path.join(CONFIG.uploadDir, user_id)
    dirPath = os.path.join(dirPath, projectId)
    dirPath = dirPath + "/"
    print (dirPath)
    return dirPath

def updateProjectQueue(user_id, projectId, packages):
    import googleapiclient.discovery
    utilities.logger.info('update project queue')
    path = getPath(user_id, projectId)
    dataController.updateProjectPackage(projectId, packages);
    data = dataController.updateProjectQueue(user_id, projectId, path, packages)
    if data:
        #run shell script
        try:
            print ('running command')
            utilities.logger.info('running command')
            #os.system('sh ' + './createInstance.sh')
            #os.system("gcloud compute instances start develop-v0")
            compute = googleapiclient.discovery.build('compute', 'v1')
            r = compute.instances().start(project='optimistic-yeti-192610', zone='asia-east1-a', instance='develop-v0').execute()
        except Exception as e:
            utilities.logger.error(str(e), exc_info=True)
            print (e)

    return data