# Mhero backend

[![Generic badge](https://img.shields.io/badge/coverage->=50-yellow.svg)](https://shields.io/)

This is a Django-based backend.

## Installation

```bash
# Clone the Project
git clone git@github.com:FND-Development/mhero-backend.git
```

## Setup **.env**

```
# write the corresponding settings in .env file

DJANGO_SECRET_KEY=<django-secret-key>
DEBUG=<debug>
ALLOWED_HOSTS=<allowed-hosts>
CORS_ALLOWED_ORIGINS=<cors-allowed-origins>

EMAIL_BACKEND=<email-backend>
EMAIL_HOST=<email-host>
EMAIL_PORT=<email-port>
EMAIL_HOST_USER=<email-host-user>
EMAIL_HOST_PASSWORD=<email-host-password>

POSTGRES_PASSWORD=<database-user-password>
POSTGRES_USER=<database-username>
POSTGRES_DB=<database-name>
POSTGRES_HOST=<database-host>
POSTGRES_PORT=<database-port>

ACCESS_TOKEN_LIFETIME=1600
FRONT_END_BASE_URL=<front-end-bas-url>

GOOGLE_CLIENT_ID=<google-client-id>
GOOGLE_CLIENT_SECRET=<google-client-secret>
AMAZON_CLIENT_ID=<amazon-client-id>
AMAZON_CLIENT_SECRET=<amazon-client-secret>
APPLE_CLIENT_ID=<apple-client-id>
APPLE_CLIENT_SECRET=<apple-client-secret>
SOCIAL_LOGIN_REDIRECT_URI=<social-login-redirect-uri>

STRIPE_SECRET_KEY=<stripe-secret-key>
```

## Dependencies

> To use the make commands, you will need to have Docker and Docker Compose installed on your machine.

### Install Docker:

* On Windows:
    * Download and install Docker Desktop from [here](https://www.docker.com/products/docker-desktop).
* On macOS:
    * Download and install Docker Desktop from [here](https://www.docker.com/products/docker-desktop).
* On Linux:
    * Follow the instructions for your distribution from [here](https://docs.docker.com/engine/install/).

### Install Docker Compose:

* On Windows and macOS:
    * Docker Compose is included with Docker Desktop.
* On Linux:
    * Follow the instructions from [here](https://docs.docker.com/compose/install/) to install Docker Compose.

## Run the server on local environment using `make` command

```bash
# run the web server and db
make run     

# run tests
make test 

# make migrations
make migrations
```
