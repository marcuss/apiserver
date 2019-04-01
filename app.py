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
        sql_query = " SELECT * " \
                    " FROM company_data" \
                    " WHERE `Accounts.LastMadeUpDate` >= {} and company_data.CompanyNumber = '{}' "\
                    " LIMIT {}".format(a_year_ago.strftime('%Y/%m/%d'), company_number, config.DATA_FETCH_LIMIT)
        logger.debug("QUERY: " + sql_query)

        cursor.execute(sql_query)
        company_row = cursor.fetchall()

        response = list()
        live_status = get_company_live_status(company_number)
        logger.debug("Live Status: " + live_status)
        company_row['CompanyStatus'] = live_status

        if len(company_row) == 0:
            return null

        report_rows = list()
        try:
            cursor.execute(
                "SELECT * FROM company_ann_reports "
                "WHERE company_ann_reports.CompanyNumber = %s", (company_number,))
            report_rows = cursor.fetchall()
        except Exception as e:
            logger.debug(e)

        try:
            cursor.execute(
                "SELECT * FROM financial_analysis "
                "WHERE financial_analysis.CompanyNumber = %s", (company_number,))
            analysis_row = cursor.fetchone()
        except Exception as e:
            logger.debug(e)

        company = {'reports': report_rows, 'analysys': analysis_row}
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

        # company_name is already big enough to try a full name search.
        if(len(company_name) > config.LENGTH_FOR_FULL_NAME_SEARCH):
            logger.debug("Full name: " + company_name)
            found_companies = find_company_by_partial_name(cursor, company_name)
            logger.debug("Found {} companies.".format(len(found_companies)))
            if len(found_companies)>0:
                logger.debug("found by full name search.")
                for company_row in found_companies:
                    company = build_company_response(cursor, company_row)
                    companies.append(company)
                return jsonify(companies)

        # companies with more than a word in the name and the first 2 words have more than 10 characters
        splitted = company_name.split()
        if (len(splitted)>1 and  len(splitted[0])+ len(splitted[1]) > 9):
            first2words = splitted[0] + " " + splitted[1] + " "
            logger.debug("First two words: " + first2words)
            found_companies = find_company_by_partial_name(cursor, first2words)
            logger.debug("Found {} companies.".format(len(found_companies)))
            if len(found_companies)>0:
                logger.debug("found by first two word of the name.")
                for company_row in found_companies:
                    company = build_company_response(cursor, company_row)
                    companies.append(company)
                return jsonify(companies)

        # Search with the 10 first letters including spaces and symbols.
        if(len(company_name) >= 10):
            first10 = company_name[0:10]
            logger.debug("First 10 letters: " + first10)
            found_companies = find_company_by_partial_name(cursor, first10)
            logger.debug("Found {} companies.".format(len(found_companies)))
            if len(found_companies)>0:
                logger.debug("found by first 10 letters.")
                for company_row in found_companies:
                    company = build_company_response(cursor, company_row)
                    companies.append(company)
                return jsonify(companies)

        # Search with the 10 first letters including spaces and symbols.
        if(len(company_name) >= 5):
            first5 = company_name[0:5]
            logger.debug("First 10 letters: " + first5)
            companies = find_company_by_partial_name(cursor, first5)
            logger.debug("Found {} companies.".format(len(companies)))
            if len(companies)>0:
                logger.debug("found by first 5 letters.")
                for company_row in companies:
                    company = build_company_response(cursor, company_row)
                    companies.append(company)
                return jsonify(companies)

        # Everything goes.
        logger.debug("found by full name.")
        found_companies = find_company_by_partial_name(cursor, company_name)
        logger.debug("Found {} companies.".format(len(found_companies)))
        if len(found_companies)>0:
            logger.debug("found by full name search.")
            for company_row in companies:
                company = build_company_response(cursor, company_row)
                companies.append(company)
            return jsonify(companies)
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
    update_company_live_status(company_number, cursor, company_row)

    report_rows = find_reports_by_company_number(company_number, cursor)

    analysis_row = find_analysis_by_company_number(company_number, cursor, company_row)

    company = {'reports': report_rows, 'analysys': analysis_row}
    company.update(company_row)
    logger.debug("Company number: "+  company_number)
    return company


def update_company_live_status(company_number, cursor, company_row):
    last_updated = company_row['CompanyStatusUpdatedAt']
    a_day_ago = datetime.datetime.now() - datetime.timedelta(hours=24)

    if (last_updated < a_day_ago):
        live_status = get_company_live_status(company_number)
        logger.debug("Live Status: " + live_status)
        company_row['CompanyStatus'] = live_status

        sql_update_query = "UPDATE company_data set CompanyStatus = '{}' where CompanyNumber = '{}' LIMIT 1"\
            .format(live_status, company_number)
        logger.debug("QUERY: " + sql_update_query)
        cursor.execute(sql_update_query)

        sql_update_query = "UPDATE company_data set CompanyStatusUpdatedAt = '{}' where CompanyNumber = '{}' LIMIT 1" \
            .format(datetime.datetime.now(), company_number)
        logger.debug("QUERY: " + sql_update_query)
        cursor.execute(sql_update_query)


def extract_company_number(single_row):
    return single_row.get("CompanyNumber", None)


def find_analysis_by_company_number(company_number, cursor, n):
    cursor.execute(
        "SELECT * FROM financial_analysis "
        "WHERE financial_analysis.CompanyNumber = %s ", (company_number,))
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
                "LIKE '{}%' " \
                "ORDER BY IncorporationDate DESC " \
                "LIMIT {} " \
                .format(partial.strip(), config.DATA_FETCH_LIMIT)
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
