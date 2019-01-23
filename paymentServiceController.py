from docutils.nodes import paragraph
from os import utime

import utilities
import paymentDBService
import requests
import json
import config as CONFIG
import os
from slugify import slugify
import datetime
import time

# TODO Bring razorpay URL into config file

utilities.logging.info("paymentServiceController")
NOTIFICATION_URL = CONFIG.notification_service
if "NOTIFICATION_URL" in os.environ:
    NOTIFICATION_URL = os.environ['NOTIFICATION_URL']

print("Connecting to Notification Service at : "+ NOTIFICATION_URL)


def processPayment(subscription_id, payment_token, userId):
    try:
        db_subscription_id = paymentDBService.getRazorpaySubscription(subscription_id)
        if None != db_subscription_id and None != subscription_id:
            key = CONFIG.RAZORPAY_KEY_ID
            secret = CONFIG.RAZORPAY_SECRET
            url = 'https://api.razorpay.com/v1/subscriptions/' + subscription_id
            r = requests.get(url, auth=(key, secret))
            print(r)
            utilities.logging.info(r)
            cleanJson = json.loads(r.text)
            print(cleanJson)
            if 'error' in cleanJson:
                utilities.logging.debug(cleanJson)
                raise Exception(utilities.xstr(cleanJson['error']))
            subscription_id = cleanJson['id']
            plan_id = cleanJson['plan_id']
            status = cleanJson['status']
            created_at = cleanJson['created_at']
            charge_at = cleanJson['charge_at']
            customer_id = cleanJson['customer_id']
            if None == customer_id:
                return {'message': "customer not found"}

            if None == charge_at:
                return {'message': "charge details not found"}
            sub_id = paymentDBService.updateRazorpaySubscription(subscription_id, plan_id, customer_id, status,
                                                          str(created_at),
                                                          str(charge_at))

            url = 'https://api.razorpay.com/v1/payments/' + payment_token
            r = requests.get(url, auth=(key, secret))
            print(r)
            utilities.logging.info(r)
            cleanJson = json.loads(r.text)
            print(cleanJson)
            if 'error' in cleanJson:
                utilities.logging.debug(cleanJson)
                return "erro occured"

            customer_id = cleanJson['customer_id']
            customer_email = cleanJson['email']
            customer_contact = cleanJson['contact']
            customer_card = cleanJson['card_id']

            # check if customer exists :
            db_customer_id = paymentDBService.getRazorpayCustomer(customer_id)
            if None == db_customer_id:
                db_customer_id = paymentDBService.createRazorpayCustomer(customer_id, customer_email, customer_card,
                                                                  customer_contact, userId)
                utilities.logging.info("customer created")
                utilities.logging.debug(db_customer_id)
            else:
                print("customer exists")
            order_id = cleanJson['order_id']
            order_amount = cleanJson['amount']
            order_invoice = cleanJson['invoice_id']
            order_status = cleanJson['status']
            payment_id = cleanJson['id']
            order_subscription = subscription_id

            paymentDBService.createRazorpayInvoice(order_id, customer_id, order_subscription, order_invoice, str(order_amount),
                                            order_status, payment_id)
            utilities.logging.debug(cleanJson)
            if sub_id:
                return {'id': subscription_id}

        else:
            raise Exception ("subscription not found " + subscription_id)
    except Exception as e:
        print(str(e))
        utilities.logging.info("failed to process Payment")
        utilities.logging.error(str(e), exc_info=True)
        errorMessage = str(e)
        errorMessage += "<br/>subscription_id " + utilities.xstr(subscription_id)
        errorMessage += "<br/>payment_token " + utilities.xstr(payment_token)

        # stripe_country, customer_email, subscription_id, subscription_item_id
        url = CONFIG.notification_service + CONFIG.errorEnd
        response = requests.post(url, json={"mail": errorMessage, "accessToken":CONFIG.accessToken})
        raise Exception("failed to processPayment for " + subscription_id + " payment Token "+ payment_token)

