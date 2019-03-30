# PROGRAM:   API Server
# AUTHOR:    Marcus Sanchez @marcuss
# LOGON ID:  Z??????
# DUE DATE:
#
# FUNCTION:  This program will receive requests asking for company
#           Information, including it's backrupcy status.
# INPUT:     REST call with information on which business to retrieve
#           It's details.
#
# OUTPUT:    REST response with the local database information plus
#           it's bankrupcy status that is retrieved from a third party.
#
# NOTES:     The Idea of this program is to be extensible so in the
#           future new Country/APIs can be query for company data.
import os
import logging.config
import config
from flask import Flask
from flask import jsonify
from flask import abort
from flask import make_response
from flask import request
from flaskext.mysql import MySQL
import datetime
import pymysql
import requests

app = Flask(__name__)
logging_conf_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'logging.conf'))
logging.config.fileConfig(logging_conf_path)
log = logging.getLogger(__name__)

@app.route('/apiserver/v1/uk/company_info', methods=['GET'])
def get_company_info():
    company_name = request.args.get('company_name')
    company_number = request.args.get('company_number')

    if not company_number:
        if not company_name:
            abort(400)

    if company_number:
        if company_name:
            abort(400)

    if  company_number:
        if not company_name:
            company =  get_company_by_number(company_number)
            if not company:
                abort(404)
            else:
                return company

    if  company_name:
        if not company_number:
            company = get_company_by_name(company_name)
            if not company:
                abort(404)
            else:
                return company
    abort(404)

def get_company_by_number(company_number):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        a_year_ago = datetime.datetime.now() - datetime.timedelta(days=365)
        sql_query = "SELECT * " \
                    "FROM company_data" \
                    " WHERE `Accounts.LastMadeUpDate` >= {} and company_data.CompanyNumber = '{}' " \
                    "LIMIT 15".format(a_year_ago.strftime('%Y/%m/%d'), company_number,)

        print(sql_query)

        cursor.execute(sql_query)
        company_row = cursor.fetchone()

        live_status = get_company_live_status(company_number)
        print("Live Status: " + live_status)
        company_row['CompanyStatus'] = live_status

        if len(company_row) == 0:
            return null

        cursor.execute(
            "SELECT * FROM company_ann_reports "
            "WHERE company_ann_reports.CompanyNumber = %s LIMIT 15", (company_number,))
        report_rows = cursor.fetchall()

        cursor.execute(
            "SELECT * FROM sync_payment_analysys "
            "WHERE sync_payment_analysys.CompanyNumber = %s LIMIT 15", (company_number,))
        analysys_row = cursor.fetchone()

        company = {'reports': report_rows, 'analysys': analysys_row}
        company.update(company_row)

        response = list()
        response.append(company)
        return jsonify(response)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()

def get_company_by_name(company_name):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:

        #First search for part of the name
        splitted = company_name.split()

        if (len(splitted)>1): # companies with more than a word in the name
            first2words = splitted[0] + " " + splitted[1] + " "

            single_row = find_by_partial_name(cursor, first2words)

            if single_row:
                print("found by partial name.")
                companies = list()
                response = build_company_response(companies, cursor, single_row)
                return jsonify(response)
            else: #if not found by partial name.
                first10 = company_name[0:10]
                single_row = find_by_partial_name(cursor, first10)

                if single_row: #
                    print("found by first 10 letters.")
                    companies = list()
                    response = build_company_response(companies, cursor, single_row)
                    return jsonify(response)

                else: #if not found by first 10 letters.
                    first5 = company_name[0:5]
                    single_row = find_by_partial_name(cursor, first5)

                    if single_row:
                        print("found by first 5 letters.")
                        companies = list()
                        response = build_company_response(companies, cursor, single_row)
                        return jsonify(response)

                    else: #if not found by first 5 letters.
                        return null
        else: # companies with only a word in the name.
            #full name search
            single_row = find_by_partial_name(cursor, company_name)

            if single_row:
                print("found by full name search.")
                companies = list()
                response = build_company_response(companies, cursor, single_row)
                return jsonify(response)
            else: #not found with full name search.
                return null

    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


def build_company_response(companies, cursor, company_row):

    company_number = extract_company_number(company_row)
    live_status = get_company_live_status(company_number)
    print("Live Status: " + live_status)
    company_row['CompanyStatus'] = live_status

    report_rows = find_reports_by_company_number(company_number, cursor)

    analysys_row = find_analysys_by_company_number(company_number, cursor, company_row)

    company = {'reports': report_rows, 'analysys': analysys_row}
    company.update(company_row)

    response = list()
    response.append(company)

    return response


def extract_company_number(single_row):
    return single_row.get("CompanyNumber", None)


def find_analysys_by_company_number(company_number, cursor, single_row):
    cursor.execute(
        "SELECT * FROM sync_payment_analysys "
        "WHERE sync_payment_analysys.CompanyNumber = %s ", (company_number,))
    single_row = cursor.fetchone()
    return single_row


def find_reports_by_company_number(company_number, cursor):
    cursor.execute(
        "SELECT * FROM company_ann_reports "
        "WHERE company_ann_reports.CompanyNumber = %s ", (company_number,))
    rows = cursor.fetchall()
    return rows


def find_by_partial_name(cursor, partial):
    cursor.execute(
        "SELECT * FROM company_data "
        "WHERE company_data.CompanyName LIKE %s ", (partial + '%',))
    single_row = cursor.fetchone()
    return single_row

def get_company_live_status(company_number):
    try:
        response =  requests.get(config.LIVE_STATUS_ENDPOINT+"/"+company_number,  auth=(config.CLIENT_SECRET, ''))
        response.raise_for_status()
        json_response = response.json()
        return json_response['company_status']
    except HTTPError as http_err:
        print('HTTP exception occurred: {http_err}')
        return null
    except Exception as err:
        print('Exception occurred: {err}')
        return null


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'Invalid Request'}), 400)

mysql = MySQL()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = config.MYSQL_DATABASE_USER
app.config['MYSQL_DATABASE_PASSWORD'] = config.MYSQL_DATABASE_PASSWORD
app.config['MYSQL_DATABASE_DB'] = config.MYSQL_DATABASE_DB
app.config['MYSQL_DATABASE_HOST'] = config.MYSQL_DATABASE_HOST
mysql.init_app(app)

if __name__ == '__main__':
    app.run(debug=config.FLASK_DEBUG, port=config.SERVER_PORT, use_reloader=False)
