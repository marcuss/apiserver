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

from flask import Flask
from flask import jsonify
from flask import abort
from flask import make_response
from flask import request


app = Flask(__name__)


@app.route('/apiserver/v1/uk/company_info', methods=['GET'])
def get_company_info():
    company_name = request.args.get('company_name')
    if company_name == '178 - 202 LIMITED':
        return jsonify(mockup_active)
    if company_name == 'BANFORD CONSULTING LIMITED':
        return jsonify(mockup_disolved)
    abort(404)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
