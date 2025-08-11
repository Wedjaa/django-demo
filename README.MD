# Creating the environment

`conda create -f environment.yaml`

## Activating

`conda activate django-roles`

# Setting up Okta

Edit `.env`:

```env
OIDC_RP_CLIENT_ID=
OIDC_RP_CLIENT_SECRET=
OIDC_OP_DOMAIN=
```

# Create the database

`python manage.py migrate`

## Updating migrations

`python manage.py makemigrations`

## Populate test data

`python manage.py create_sample_trades`

# Starting the server

`python manage.py runserver`


## Starting with SSL

`python manage.py runserver_plus --cert-file demo/cert.pem --key-file demo/key.pem`

