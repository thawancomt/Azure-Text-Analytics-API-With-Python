# Get start
## Set your Azure enviroment 
To start using this project create a Language resource on Azure.
# Set the app's variables
Get the key and endpoint and put it all into the .env file, create this .env file in project root folder.
    - The variables need to be create with these names :
        key_variable = 'KEY'
        endpoint_vairable = 'ENDPOINT'
        flask_secret_key = 'SECRET_KEY'


# Transfering data across the app
All the response need to be passed to it respective DTO object across all parts of the code.

Example: Linked entities need to be passed as a LinkedEntitiesDTO object to all operations tha will handle this data.
