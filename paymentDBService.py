# get data from database or filesystem as per request
# manage query and data connections

import config as CONFIG
import utilities
import psycopg2
import datetime
import time
import os

t = datetime.datetime(2012, 2, 23, 0, 0)
t.strftime('%m/%d/%Y')


hostname = os.getenv('PGDB_HOST', CONFIG.db['host'])
username = os.getenv('PGDB_USERNAME', CONFIG.db['username'])
password = os.getenv('PGDB_PASSWORD', CONFIG.db['password'])
database = os.getenv('PGDB_DATABASE', CONFIG.db['database'])

if CONFIG.enviornment.lower() == 'production':
    hostname = CONFIG.DB_PROD['host']
    username = CONFIG.DB_PROD['username']
    password = CONFIG.DB_PROD['password']
    database = CONFIG.DB_PROD['database']


print(password)

pg_connection = None
try:
    print("Connecting to the database at "+ hostname+ " for user : "+username)
    pg_connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
    print("Connected to the database at "+ hostname+ " for user : "+username)
except:
    print("Unable to connect to database, Guess I'll die.")
    raise Exception ("Unable to connect to database, Guess I'll die")

def getConnection():
    return pg_connection


def doQuery(query):
    # execute query
    pg_connection = getConnection()
    if None == pg_connection or pg_connection.closed != 0:
        try:
            pg_connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
        except:
            print("I am unable to connect to the database")
            raise Exception("unable to connect to database")
    try:
        utilities.logging.info("doQuery")
        utilities.logging.debug(query)
        resultSet = []
        cur = pg_connection.cursor()
        cur.execute(query)
        resultSet.append(cur.fetchall())
        utilities.logging.info("done query")
        return resultSet
    except Exception as e:
        utilities.logging.error(str(e), exc_info=True)
        pg_connection.rollback()
        raise Exception(e)

result = doQuery('select * from programs limit 1')
print (result)

def insertQuery(query):
    # execute query
    pg_connection = getConnection()
    if None == pg_connection or pg_connection.closed != 0 :
        try:
            pg_connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
        except:
            print("I am unable to connect to the database")
            raise Exception("unable to connect to database")

    try:
        utilities.logging.info("insert Query")
        utilities.logging.debug(query)
        resultSet = []
        cur = pg_connection.cursor()
        cur.execute(query)
        rowcount = cur.rowcount;
        utilities.logging.debug("Returned record count : " + str(rowcount))
        pg_connection.commit()
    except Exception as e:
        utilities.logging.error(str(e), exc_info=True)
        pg_connection.rollback()
        raise Exception(e)


def checkRazorpayPlan(planIdPGDB):
    result_set = None
    try:
        utilities.logging.info('checkRazorpayPlan ' + planIdPGDB)
        query = "select id from razorpay_plan where planId = '" + planIdPGDB + "'"
        plan_id = None
        result_set = doQuery(query)
        for row in result_set:
            for id in row:
                plan_id = id[0]
                utilities.logging.debug(id)
        return plan_id
    except Exception as e:
        utilities.logging.info("Unable to get razorpay plan " + planIdPGDB)
        utilities.logging.error(str(e), exc_info=True)
    return None


def createRazorpayPlan(plan_id, planIdPGDB, period, name, amount, currency, date):
    try:
        utilities.logging.info('createSubscriptionItem ' + plan_id)
        id = None
        query = "insert into razorpay_plan (id, planid, period, name, amount, currency, date,  createdAt) values('" + plan_id + "', '" + planIdPGDB + "', '" + period + "', '" + name + "', '" + str(
            amount) + "', '" + currency + "', " + str(date) + ", now()) ON CONFLICT(id) DO NOTHING"
        print(query)
        insertQuery(query)
        return plan_id
    except Exception as e:
        id = None
        utilities.logging.info("Unable to create Razorpay Plan " + plan_id)
        utilities.logging.error(str(e), exc_info=True)
        raise Exception("Unable to create Razorpay Plan " + plan_id)
    return id


def createRazorpaySubscription(subscription_id, plan_id, customer_id, status, created_at, charge_at):
    try:
        utilities.logging.info('createSubscriptionItem ' + plan_id)
        query = "insert into razorpay_subscription (id, plan_id, customer_id, status, createdAt) values('" + subscription_id + "', '" + plan_id + "', '" + customer_id + "', '" + status + "',  now()) ON CONFLICT(id) DO NOTHING"
        print(query)
        insertQuery(query)
        return subscription_id
    except Exception as e:
        utilities.logging.info("Unable to create razorpay subscription " + subscription_id)
        utilities.logging.erro(str(e), exc_info=True)
        raise Exception("Unable to create razorpay subscription " + subscription_id)


def getRazorpaySubscription(subscription_id):
    result_set = None
    try:
        utilities.logging.info(subscription_id)
        query = "select id from razorpay_subscription where id = '" + subscription_id + "'"
        print(query)
        result_set = doQuery(query)
        utilities.logging.debug(result_set)
        for row in result_set:
            for id in row:
                cust_id = id
                subscription_id = cust_id[0]
        utilities.logging.debug(subscription_id)
        return subscription_id
    except Exception as e:
        utilities.logging.info("unable to get RazorpaySubscription " + subscription_id)
        utilities.logging.error(str(e), exc_info=True)
        return None


def updateRazorpaySubscription(subscription_id, plan_id, customer_id, status, created_at, charge_at):
    try:
        utilities.logging.info('createSubscriptionItem ' + plan_id)
        query = "update razorpay_subscription set customer_id = '" + customer_id + "', status = '" + status + "', updatedat = now() where id = '" + subscription_id + "'"
        print(query)
        insertQuery(query)
        return subscription_id
    except Exception as e:
        utilities.logging.info("Unable to update Razorpay Subscription " + subscription_id + " status " + status)
        utilities.logging.error(str(e), exc_info=True)
        raise Exception("Unable to update Razorpay Subscription " + subscription_id + " status " + status)


def createRazorpayCustomer(customer_id, customer_email, customer_card, customer_contact, userId):
    try:
        utilities.logging.info('createSubscriptionItem ' + customer_id)
        query = "insert into razorpay_customer (id, user_id, customer_email, customer_card, customer_contact, createdAt) values('" + customer_id + "', '" + str(
            userId) + "', '" + customer_email + "', '" + customer_card + "', '" + customer_contact + "', now()) ON CONFLICT(id) DO NOTHING"
        print(query)
        insertQuery(query)
        return customer_id
    except Exception as e:
        utilities.logging.info("Unable to create Razorpay Customer " + customer_id)
        utilities.logging.error(str(e), exc_info=True)
        raise Exception("Unable to create Razorpay Customer " + customer_id)


def createRazorpayInvoice(order_id, customer_id, order_subscription, order_invoice, order_amount, status, payment_id):
    try:
        utilities.logging.info("create razorpay invoice " + str(order_id))
        query = "insert into razorpay_order (id, customer_id, order_subscription, order_invoice, order_amount, status, payment_id, createdAt) values('" + order_id + "', '" + customer_id + "', '" + order_subscription + "', '" + order_invoice + "', '" + str(
            order_amount) + "', '" + status + "', '" + payment_id + "', now()) ON CONFLICT(id) DO NOTHING"
        print(query)
        insertQuery(query)
        return order_id
    except Exception as e:
        utilities.logging.info("Unable to create Razorpay Invoice" + order_invoice)
        utilities.logging.error(str(e), exc_info=True)
        raise Exception("Unable to create Razorpay Invoice" + order_invoice)


def getRazorpayCustomer(customer_id):
    result_set = None
    try:
        utilities.logging.info("get Razorpay customer " + str(customer_id))
        query = "select id from razorpay_customer where id = '" + customer_id + "'"
        print(query)
        db_customer_id = None
        result_set = doQuery(query)
        utilities.logging.debug(result_set)
        for row in result_set:
            for id in row:
                cust_id = id
                db_customer_id = cust_id[0]
        utilities.logging.debug(customer_id)
        return db_customer_id
    except Exception as e:
        utilities.logging.info("unable to get RazorpayCustomer " + customer_id)
        utilities.logging.error(str(e), exc_info=True)
        return None


def updateRazorpaySubscriptionStatus(subscription_id, status):
    try:
        utilities.logging.info('updateRazorpaySubscriptionPending ' + subscription_id)
        query = "update razorpay_subscription set status = '" + status + "', updatedAt = now() where id = '" + subscription_id + "'"
        print(query)
        insertQuery(query)
        return subscription_id
    except Exception as e:
        utilities.logging.info("unable to update Razorpay SubscriptionStatus " + subscription_id + " status " + status)
        utilities.logging.error(str(e), exc_info=True)
        raise Exception("Unable to create invoice")


def updateRazorpayInvoice(order_id, order_status, order_subscription):
    try:
        utilities.logging.info('updateRazorpayInvoice ' + order_id)
        query = "update razorpay_order set order_subscription = '" + order_subscription + "', status = '" + order_status + "', updatedAt = now() where id = '" + order_id + "'"
        print(query)
        insertQuery(query)
        return order_id
    except Exception as e:
        utilities.logging.info(
            "unable to update Razorpay SubscriptionStatus " + order_subscription + " order_status " + order_status)
        raise Exception("Unable to create invoice")


def getRazorpayOrder(order_id):
    result_set = None
    try:
        utilities.logging.info("get razorpay order " + str(order_id))
        query = "select id, invoice_sent from razorpay_order where id = '" + order_id + "'"
        print(query)
        db_order_id = {}
        result_set = doQuery(query)
        utilities.logging.debug(result_set)
        for row in result_set:
            for id, invoice_sent in row:
                db_order_id['id'] = id
                if invoice_sent:
                    db_order_id['invoice_sent'] = invoice_sent
                elif None == invoice_sent:
                    db_order_id['invoice_sent'] = ''
                else:
                    db_order_id['invoice_sent'] = ''
        utilities.logging.debug(db_order_id)
        return db_order_id
    except Exception as e:
        utilities.logging.info("unable to get Razorpay Order " + order_id)
        utilities.logging.error(str(e), exc_info=True)
        return None


def getUserEmailId(user_id):
    result_set = None
    try:
        utilities.logging.info(user_id)
        query = "select email from users where id = " + str(user_id)
        print(query)
        db_email = None
        result_set = doQuery(query)
        utilities.logging.debug(result_set)
        for row in result_set:
            for email in row:
                email_id = email
                db_email = email_id[0]
        utilities.logging.debug(db_email)
        return db_email
    except Exception as e:
        utilities.logging.info("unable to get User Email " + str(user_id))
        utilities.logging.error(str(e), exc_info=True)
        raise Exception("Email not found for user " + str(user_id))

def getInvoiceForStripeSubscription(subscription_item_id):
    result_set = None
    try:
        utilities.logging.info('get last invoice subscription_item_id = ' + subscription_item_id)
        query = "select createdat, invoice_sent from invoice where subscription_item_id = '" + subscription_item_id + "' order by createdat desc limit 1"
        data = {}
        result_set = doQuery(query)
        for row in result_set:
            for createdat, invoice_sent in row:
                data['createdat'] = createdat
                data['invoice_sent'] = invoice_sent
        utilities.logging.debug(data)
        return data
    except Exception as e:
        utilities.logging.info('Unable to get last invoice subscription_item_id = ' + subscription_item_id)
        utilities.logging.error(str(e), exc_info=True)
    return None

def getLastInvoiceForStripeSubscription(subscription_item_id):
    result_set = None
    try:
        utilities.logging.info('get last invoice subscription_item_id = ' + subscription_item_id)
        query = "select createdat from invoice where subscription_item_id = '" + subscription_item_id + "' and payment_status = 'success' order by createdat limit 1"
        lastInvoice = None
        result_set = doQuery(query)
        for row in result_set:
            for createdat in row:
                lastInvoice = createdat[0]
        utilities.logging.debug(lastInvoice)
        return lastInvoice
    except Exception as e:
        utilities.logging.info('Unable to get last invoice subscription_item_id = ' + subscription_item_id)
        utilities.logging.error(str(e), exc_info=True)
    return None


def getUserIdForStripePayment(subscription_item_id):
    result_set = None
    try:
        utilities.logging.info('get last invoice subscription_item_id = ' + subscription_item_id)
        query = '''select payment_customer.email, subscription_items.plan_id from
                payment_customer join subscription on payment_customer.id = subscription.customer_id
                join subscription_items on subscription.id = subscription_items.subscription_id
                where subscription_items.id ='[si_id]' limit 1'''
        query = query.replace('[si_id]', subscription_item_id)
        data = {}
        result_set = doQuery(query)
        for row in result_set:
            for email, plan_id  in row:
                data['email'] = email
                data['planId'] = plan_id
        utilities.logging.debug(data)
        return data
    except Exception as e:
        utilities.logging.info('Unable to get last invoice subscription_item_id = ' + subscription_item_id)
        utilities.logging.error(str(e), exc_info=True)
    return None


def getStripePaymentDontaionId(subscription_item_id):
    result_set = None
    try:
        utilities.logging.info("get donation ID " + str(subscription_item_id))
        query = ''' select id from donations where "subscriptionId" = '[subscriptionItemId]' '''
        query = query.replace('[subscriptionItemId]', str(subscription_item_id))
        print(query)
        donationIdDB = None
        result_set = doQuery(query)
        utilities.logging.debug(result_set)
        for row in result_set:
            for id in row:
                donationId = id
                donationIdDB = donationId[0]
                utilities.logging.debug(str(id))
        return donationIdDB
    except Exception as e:
        utilities.logging.info("unable to get donation ID for " + subscription_item_id)
        utilities.logging.error(str(e), exc_info=True)
        return None


def getRazorpayDontaionId(order_subscription):
    result_set = None
    try:
        utilities.logging.info("get donation ID " + str(order_subscription))
        query = ''' select id from donations where "subscriptionId" = '[subscriptionItemId]' '''
        query = query.replace('[subscriptionItemId]', str(order_subscription))
        print(query)
        donationIdDB = None
        result_set = doQuery(query)
        utilities.logging.debug(result_set)
        for row in result_set:
            for id in row:
                donationId = id
                donationIdDB = donationId[0]
                utilities.logging.debug(str(id))
        return donationIdDB
    except Exception as e:
        utilities.logging.info("unable to get donation ID for " + order_subscription)
        utilities.logging.error(str(e), exc_info=True)
        return None

    return None


def getLastInvoiceForRzorpaySubscription(order_subscription):
    result_set = None
    try:
        utilities.logging.info('get last invoice subscription_item_id = ' + order_subscription)
        query = '''
                    select createdat
                    from razorpay_order
                    where order_subscription = '[subscriptionId]'
                    and status = 'captured'
                    order by createdat limit 1'''

        query = query.replace('[subscriptionId]',  order_subscription)
        lastInvoice = None
        result_set = doQuery(query)
        for row in result_set:
            for updatedAt in row:
                lastInvoice = updatedAt[0]
        utilities.logging.debug(lastInvoice)
        return lastInvoice
    except Exception as e:
        utilities.logging.info('Unable to get last invoice subscription_item_id = ' + order_subscription)
        utilities.logging.error(str(e), exc_info=True)
        raise Exception("Razorpay Subscription not found for " + str(order_subscription))


def checkIfRazorpaySubscriptionActive(subscription_item_id):
    try:
        utilities.logging.info('checkIfSubscriptionItemActive ' + subscription_item_id)
        query = "select updatedAt from subscription_items where state = 'active' and id = '" + subscription_item_id + "'"
        print(query)
        item_state = None
        result_set = doQuery(query)
        for row in result_set:
            for updatedAt in row:
                item_state = updatedAt[0]
        utilities.logging.debug(item_state)
        return item_state
    except Exception as e:
        utilities.logging.error(str(e), exc_info=True)
    return None


def getUserIdForRazorpayPayment(order_subscription):
    result_set = None
    try:
        utilities.logging.info('get last invoice subscription_item_id = ' + order_subscription)
        query = '''
                select razorpay_customer.customer_email , razorpay_plan.planid  from razorpay_customer
                join razorpay_subscription  on
                razorpay_subscription.customer_id = razorpay_customer.id
                join razorpay_plan  on razorpay_plan.id = razorpay_subscription.plan_id
                where
                razorpay_subscription.id = '[si_id]' limit 1
                '''

        query = query.replace('[si_id]', order_subscription)
        data = {}
        result_set = doQuery(query)
        for row in result_set:
            for email, plan_id in row:
                data['email'] = email
                data['planId'] = plan_id
        utilities.logging.debug(data)
        return data
    except Exception as e:
        utilities.logging.info('Unable to get userId subscription_id = ' + order_subscription)
        utilities.logging.error(str(e), exc_info=True)
    return None


def setStripeInvoiceSentFlag(invoice_id, param):
    try:
        utilities.logging.info('updateStripeInvoiceSent ' + utilities.xstr(param))
        query = "update invoice set invoice_sent = '" + utilities.xstr(param) + "', updatedAt = now() where id = '" + invoice_id + "'"
        print(query)
        insertQuery(query)
        return invoice_id
    except Exception as e:
        utilities.logging.info(
            "unable to update Stripe SubscriptionStatus " + invoice_id + " order_status " + utilities.xstr(param))
        # raise Exception("Unable to create invoice")


def setRazorpayInvoiceSentFlag(invoice_id, param):
    try:
        utilities.logging.info('updateRazorpayInvoiceSent ' + utilities.xstr(param))
        query = "update razorpay_order set invoice_sent = " + utilities.xstr(param) + ", updatedAt = now() where id = '" + invoice_id + "'"
        print(query)
        insertQuery(query)
        return invoice_id
    except Exception as e:
        utilities.logging.info(
            "unable to update Razorpay SubscriptionStatus " + invoice_id + " order_status " + utilities.xstr(param))
        # raise Exception("Unable to create invoice")