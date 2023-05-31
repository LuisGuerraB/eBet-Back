# eBet-Back
TFG-BackEnd


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