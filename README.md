# Apiserver

The API server is a Python application that runs a microframework for rest services called Flask.
The Database to query cached data is a MySQL instance, and the third party we will query for this first iteration for UK companies is https://api.companieshouse.gov.uk/company/{company_number}

## REST Service Definition.

Route: /apiserver/v1/uk/company_info
HTTP method: GET
Query parameter: company_name
Example curl:
curl -XGET http://127.0.0.1:5000/apiserver/v1/uk/company_info?company_name=test
127.0.0.1 = Deployment host
5000 = App running port

## REST Service Response.

See response format document.
https://docs.google.com/document/d/11wG_mnKECgI5veb5yQQC3wIYOLM0w4jHSJAbKOVejW4/edit


## Deployment.
The only prerequisite is an installed python3 so make sure you have Python3.x installed on your system.

`pip install virtualenv`

`python3 -m venv api_venv`

`source api_venv/bin/activate`

`pip install --user pipenv`

`export PATH=$PATH:~/.local/bin`

`pipenv install`

`python3 app.py` 

## How to run it from CLI/SSH
If it is not installed as a daemon/service on the server it is run from the CLI/SSH and no where else.

`source api_venv/bin/activate`

`python3 app.py` 

## How to run it as a service all the time

` nohup python3 app.py & `

## How to stop it from the service running

 kill -9 `netstat -napt| grep LISTEN |  grep 4998 |  awk {'print $7'} | cut -d'/' -f1' ` 
 
 The directory have a built in script to start and stop the service via shell

## Run it via shell script
Please chose the alternative you want

`./service.sh start`

`./service.sh stop `

`./service.sh status `
