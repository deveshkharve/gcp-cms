from flask import jsonify

class APIException(Exception):
    statusCode = 400

    def __init__(self, exception, developerMessage, clientMessage, moreInfo, statusCode=None, payload=None):
        Exception.__init__(self)
        self.clientMessage = clientMessage
        self.developerMessage = developerMessage
        self.exception = exception
        self.moreInfo = moreInfo
        if statusCode is not None:
            self.statusCode = statusCode
        self.payload = payload

    def toDict(self):
        rv = dict(self.payload or ())
        rv['clientMessage'] = self.clientMessage
        rv['developerMessage'] = self.developerMessage
        rv['exception'] = self.exception
        rv['moreInfo'] = self.moreInfo
        return rv