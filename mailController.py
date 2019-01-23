import smtplib
import os
import config as CONFIG
import requests
import utilities
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import userController

def mailer(to, text, subject):
    sender = CONFIG.sender
    receivers = to
    msg = MIMEText(text,  'html')
    msg['Subject'] = subject
    mailUserName = os.getenv('SMTP_USER', CONFIG.mailUserName)
    mailPassword = os.getenv('SMTP_PASSWORD', CONFIG.mailPassword)
    try:
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(mailUserName, mailPassword)
        server.sendmail(sender, receivers, msg.as_string())
        utilities.logging.info("Successfully sent email")
    except Exception as e:
        utilities.logging.info(str(e))
        utilities.logging.info("Error: unable to send email")
        utilities.logging.error(str(e), exc_info=True)

def readFileToString(filepath):
    utilities.logging.info('readFileToString ' + filepath)
    data_to_read = None
    try:
        with open(filepath, "r") as myfile:
            data_to_read = myfile.read()
            utilities.logging.debug (data_to_read)
    except Exception as e:
        utilities.logging.error(str(e), exc_info=True)
        raise Exception(str(e))
    return data_to_read


def getTemplate(template_id):
    try:
        utilities.logging.info('get Template' + str(template_id))
        template_dir = CONFIG.TEMPLATE_DIR
        template_path = os.path.join(template_dir, template_id)
        return readFileToString(template_path)
    except Exception as e:
        utilities.logging.error(str(e), exc_info=True)
        raise Exception(str(e))

def loadTemplate(data, template):
    try:
        utilities.logging.info('loadTemplate')
        utilities.logging.debug(data)

        if (type(data) == type({'a' :'b'})) :
            for key in data:
                tag = '<%' + key + '%>'
                value = str(data[key])
                template = template.replace(tag, value)
        return template
    except Exception as e:
        utilities.logging.error(str(e),exc_info=True)
        raise Exception ("Failed to Load Template")


def sendForgotMailer(user_id, emailHash, email):

    tempalteStr = getTemplate(CONFIG.forgotMailTemplate)
    link = CONFIG.serverURL + '/forgotpassword' + '?id=' +str(user_id) + '&req=' + str(emailHash)
    data = {}
    data['link'] = link
    message = loadTemplate(data, tempalteStr)
    subject = CONFIG.forgotMailSubject
    mailer(email, message, subject)
    return None

def sendWelcomeMailer(email, name, user_id, emailHash):
    tempalteStr = getTemplate(CONFIG.welcomeMailTemplate)
    link = CONFIG.serverURL + '/authenticate' + '?id=' + str(user_id) + '&req=' + str(emailHash)
    data = {}
    data['name'] = name
    data['link'] = link
    message = loadTemplate(data, tempalteStr)
    subject = CONFIG.welcomeMailSubject
    mailer(email, message, subject)
    return None
