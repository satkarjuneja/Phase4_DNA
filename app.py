from fastapi import FastAPI
from base_models.country import Country
from database_api import country

app = FastAPI()

@app.post("/add_country")
def add_country(country_info: Country):
    country.add_country(country_info.country_name, country_info.country_code)
    return {"result": "successfully added country"}

@app.post("/delete_country")
def delete_country(country_info:Country):
    country.delete_country(country_info.country_name, country_info.country_code)
    return {"result": "successfully deleted country"}
