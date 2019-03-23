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

from flask import Flask, jsonify, abort, make_response
from flask import request

app = Flask(__name__)

mockup_active = {
    "companies": [{
        "company_name": "178 - 202 LIMITED",
        "company_number": "00024028",
        "company_status": "active",
        "reg_address_care_of": "",
        "reg_address_po_box": "",
        "reg_address_address_line1": "32, VAUXHALL BRIDGE ROAD",
        "reg_address_address_line2": "",
        "reg_address_post_town": "LONDON",
        "reg_address_county": "",
        "reg_address_country": "",
        "reg_address_post_code": "SW1V 2SS",
        "company_category": "Private Limited Company",
        "country_of_origin": "United Kingdom",
        "dissolution_date": "0",
        "incorporation_date": "01/03/1887",
        "accounts_account_ref_day": "30",
        "accounts_account_ref_month": "6",
        "accounts_next_due_date": "31/03/2020'",
        "accounts_last_made_up_date": "30/06/2018",
        "accounts_account_category": "",
        "returns_next_due_date": "28/07/2016",
        "returns_last_made_up_date": "30/06/2015",
        "mortgages_num_mort_charges": "0",
        "mortgages_num_mort_outstanding": "0",
        "mortgages_num_mort_part_satisfied": "0",
        "mortgages_num_mort_satisfied": "0",
        "sic_code_sic_text_1": "74990 - Non-trading company",
        "sic_code_sic_text_2": "",
        "sic_code_sic_text_3": "",
        "sic_code_sic_text_4": "",
        "limited_partnerships_num_gen_partners": "0",
        "limited_partnerships_num_lim_partners": "0",
        "uri": "http://business.data.gov.uk/id/company/00024028",
        "previous_name_1_condate": "",
        "previous_name_1_company_name": "",
        "previous_name_2_condate": "",
        "previous_name_2_company_name": "",
        "previous_name_3_condate": "",
        "previous_name_3_company_name": "",
        "previous_name_4_condate": "",
        "previous_name_4_company_name": "",
        "previous_name_5_condate": "",
        "previous_name_5_company_name": "",
        "previous_name_6_condate": "",
        "previous_name_6_company_name": "",
        "previous_name_7_condate": "",
        "previous_name_7_company_name": "",
        "previous_name_8_condate": "",
        "previous_name_8_company_name": "",
        "previous_name_9_condate": "0",
        "previous_name_9_company_name": "0",
        "previous_name_10_condate": "0",
        "previous_name_10_company_name": "0",
        "conf_stmt_next_due_date": "14/07/2019",
        "conf_stmt_last_made_up_date": "30/06/2018",
        "reports": [{
                "url": "Prod224_0015_00024028_20140630.html",
                "year": "2014",
                "work_cap": "0.0",
                "cos": "0.0",
                "curr_ass": "0.0",
                "fix_ass": "0.0",
                "tot_ass": "0.0",
                "depr_amort": "0.0",
                "ppe": "0.0",
                "sga": "0.0",
                "long_term_d": "0.0",
                "curr_lia": "0.0",
                "inc_tax": "0.0",
                "cash": "0.0",
                "sales": "0.0",
                "pnl_before_tax": "0.0",
                "pnl_after_tax": "0.0",
                "gross_profit": "0.0"
            },
            {
                "url": "Prod224_0051_00024028_20170630.html",
                "year": "2017",
                "work_cap": "0.0",
                "cos": "0.0",
                "curr_ass": "0.0",
                "fix_ass": "0.0",
                "tot_ass": "0.0",
                "depr_amort": "0.0",
                "ppe": "0.0",
                "sga": "0.0",
                "long_term_d": "0.0",
                "curr_lia": "0.0",
                "inc_tax": "0.0",
                "cash": "0.0",
                "sales": "0.0",
                "pnl_before_tax": "0.0",
                "pnl_after_tax": "0.0",
                "gross_profit": "0.0"
            },
            {
                "url": "Prod224_0063_00024028_20180630.html",
                "year": "2018",
                "work_cap": "0.0",
                "cos": "0.0",
                "curr_ass": "0.0",
                "fix_ass": "0.0",
                "tot_ass": "0.0",
                "depr_amort": "0.0",
                "ppe": "0.0",
                "sga": "0.0",
                "long_term_d": "0.0",
                "curr_lia": "0.0",
                "inc_tax": "0.0",
                "cash": "0.0",
                "sales": "0.0",
                "pnl_before_tax": "0.0",
                "pnl_after_tax": "0.0",
                "gross_profit": "0.0"
            }
        ],
        "analysys": {
            "created_at": "2019-03-22 22:20:12",
            "credit_rating": "H",
            "credit_score": "0",
            "credit_limit": "ND",
            "purchase_score": "0",
            "purchase_rating": "H",
            "combined_credit_score": "",
            "combined_purchase_score": ""
        }
    }]
}

mockup_disolved = {
    "companies": [{
        "company_name": "BANFORD CONSULTING LIMITED",
        "company_number": "SC298153",
        "company_status": "dissolved",
        "reg_address_care_of": "",
        "reg_address_po_box": "",
        "reg_address_address_line1": "12 CARDEN PLACE",
        "reg_address_address_line2": "",
        "reg_address_post_town": "ABERDEEN",
        "reg_address_county": "ABERDEENSHIRE",
        "reg_address_country": "",
        "reg_address_post_code": "AB10 1UR",
        "company_category": "Private Limited Company",
        "country_of_origin": "United Kingdom",
        "dissolution_date": "0",
        "incorporation_date": "06/03/2006",
        "accounts_account_ref_day": "31",
        "accounts_account_ref_month": "3",
        "accounts_next_due_date": "31/12/2017",
        "accounts_last_made_up_date": "31/03/2016",
        "accounts_account_category": "TOTAL EXEMPTION SMALL",
        "returns_next_due_date": "203/04/2017",
        "returns_last_made_up_date": "06/03/2016",
        "mortgages_num_mort_charges": "1",
        "mortgages_num_mort_outstanding": "1",
        "mortgages_num_mort_part_satisfied": "0",
        "mortgages_num_mort_satisfied": "0",
        "sic_code_sic_text_1":
        "82990 - Other business support service activities n.e.c.",
        "sic_code_sic_text_2": "",
        "sic_code_sic_text_3": "",
        "sic_code_sic_text_4": "",
        "limited_partnerships_num_gen_partners": "0",
        "limited_partnerships_num_lim_partners": "0",
        "uri": "http://business.data.gov.uk/id/company/SC298153",
        "previous_name_1_condate": "12/10/2006",
        "previous_name_1_company_name": "SBA QUALITY LIMITED",
        "previous_name_2_condate": "",
        "previous_name_2_company_name": "",
        "previous_name_3_condate": "",
        "previous_name_3_company_name": "",
        "previous_name_4_condate": "",
        "previous_name_4_company_name": "",
        "previous_name_5_condate": "",
        "previous_name_5_company_name": "",
        "previous_name_6_condate": "",
        "previous_name_6_company_name": "",
        "previous_name_7_condate": "",
        "previous_name_7_company_name": "",
        "previous_name_8_condate": "",
        "previous_name_8_company_name": "",
        "previous_name_9_condate": "0",
        "previous_name_9_company_name": "0",
        "previous_name_10_condate": "0",
        "previous_name_10_company_name": "0",
        "conf_stmt_next_due_date": "20/03/2018",
        "conf_stmt_last_made_up_date": "06/03/2017"
    }]

}


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
