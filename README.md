# eBet-Back
TFG-BackEnd

# Running the app

First, take both db-local-template and template.env and create two new files with 
the same name, but without the "template".

Next substitute dummy data with the corresponding passwords and username

Lastly, run the deploy command:
```
docker-compose -f db.docker-compose.yml --env-file db-local.env up -d
```


# Exporting DB models
First install sqlacodegen
```
pip install --upgrade sqlacodegen
```
Then run this command filling with the user and the password
```
sqlacodegen --outfile=models.sql --noinflect  postgresql://<user>:<password>@localhost/eBet
```
Lastly upgrade sqlalchemy, due to a downgrade made by the installation of sqlacodegen
```
pip install --upgrade sqlalchemy
```

# Running Tests
```
python -m pytest --disable-warnings tests
```