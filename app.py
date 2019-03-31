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
logger = logging.getLogger(__name__)

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
                    "LIMIT {}".format(a_year_ago.strftime('%Y/%m/%d'), company_number, config.DATA_FETCH_LIMIT)
        logger.debug("QUERY: " + sql_query)

        cursor.execute(sql_query)
        company_row = cursor.fetchall()

        response = list()
        live_status = get_company_live_status(company_number)
        print("Live Status: " + live_status)
        company_row['CompanyStatus'] = live_status

        if len(company_row) == 0:
            return null

        cursor.execute(
            "SELECT * FROM company_ann_reports "
            "WHERE company_ann_reports.CompanyNumber = %s", (company_number,))
        report_rows = cursor.fetchall()

        cursor.execute(
            "SELECT * FROM sync_payment_analysys "
            "WHERE sync_payment_analysys.CompanyNumber = %s", (company_number,))
        analisys_row = cursor.fetchone()

        company = {'reports': report_rows, 'analysys': analisys_row}
        company.update(company_row)

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
        companies = list()
        #First search for part of the name
        splitted = company_name.split()

        if (len(splitted)>1): # companies with more than a word in the name
            first2words = splitted[0] + " " + splitted[1] + " "
            logger.debug("First two words: " + first2words)
            found_companies = find_company_by_partial_name(cursor, first2words)
            logger.debug("Found {} companies.".format(len(found_companies)))
            if len(companies)>0:
                logger.debug("found by partial name.")
                for company_row in found_companies:
                    company = build_company_response(cursor, company_row)
                    companies.append(company)
                return jsonify(companies)
            else:
                first10 = company_name[0:10]
                found_companies = find_company_by_partial_name(cursor, first10)
                logger.debug("Found {} companies.".format(len(found_companies)))
                if len(found_companies)>0:
                    logger.debug("found by first 10 letters.")
                    for company_row in found_companies:
                        company = build_company_response(cursor, company_row)
                        companies.append(company)
                    return jsonify(companies)

                else:
                    first5 = company_name[0:5]
                    companies = find_company_by_partial_name(cursor, first5)
                    logger.debug("Found {} companies.".format(len(companies)))
                    if len(companies)>0:
                        logger.debug("found by first 5 letters.")
                        for company_row in companies:
                            company = build_company_response(cursor, company_row)
                            companies.append(company)
                        return jsonify(companies)

                    else:
                        return null
        else: # companies with only a word in the name.
            logger.debug("found by full name.")
            companies = find_company_by_partial_name(cursor, company_name)
            logger.debug("Found {} companies.".format(len(companies)))
            if len(companies)>0:
                logger.debug("found by full name search.")
                response = build_company_response(cursor, company_row)
                return jsonify(response)
            else:
                return null

    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


def build_company_response(cursor, company_row):
    logger.debug("Build company response")
    company_number = extract_company_number(company_row)
    logger.debug("Company number: " + company_number)
    live_status = get_company_live_status(company_number)
    logger.debug("Live Status: " + live_status)
    company_row['CompanyStatus'] = live_status

    report_rows = find_reports_by_company_number(company_number, cursor)

    analisys_row = find_analysys_by_company_number(company_number, cursor, company_row)

    company = {'reports': report_rows, 'analysys': analisys_row}
    company.update(company_row)
    logger.debug("Company number: "+  company_number)
    return company


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


def find_company_by_partial_name(cursor, partial):
    sql_query = "SELECT * FROM company_data " \
                "WHERE company_data.CompanyName " \
                "LIKE '{}%' LIMIT {}".format(partial.strip(), config.DATA_FETCH_LIMIT)
    logger.debug("QUERY: " + sql_query)
    cursor.execute(sql_query)
    multiple_rows = cursor.fetchall()
    return multiple_rows

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
