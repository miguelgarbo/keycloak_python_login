**Python version: 3.12.0**

## For run the application

* Create a Virtual Enviroment

/ python -m venv .venv

* Activate the Enviroment

/ source .venv/bin/activate

* Install the requirements(libs) of the project
  
/ pip install -r requirements.txt

* Run app.py file

Documentation of using keycloak with docker :
https://www.keycloak.org/getting-started/getting-started-docker

Documentation of installing keycloak on your own machine
https://www.keycloak.org/guides

## For this application you may have installed or a docker image running a Keycloak Server

## .env file content

root='/home/'
ROOT_PATH_PREFIX='/home'

KEYCLOAK_SERVER_URL='http://localhost:8080/' if you running on a local server
KEYCLOAK_CLIENT_ID=name_of_keycloak_client_server_that_you_created
KEYCLOAK_REALM_NAME=name_of_a_realm_you_want_to_use
KEYCLOAK_CLIENT_SECRET_KEY=secret_key_here





