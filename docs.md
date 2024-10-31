# Get start
## Set your Azure enviroment 
To start using this project create a Language resource on Azure.
# Set the app's variables
Get the key and endpoint (from Azure) and put it all into the .env file, create this .env file in project root folder.
    - The variables need to be create with these names :
        key_variable = 'KEY'
        endpoint_vairable = 'ENDPOINT'
        flask_secret_key = 'SECRET_KEY'
        database_path = 'DB_PATH' (Your sqlite name database)


# Transfering data across the app
All data transfered across the app need to be in the DTO's format from DTO.py module.
