from fastapi import FastAPI
from base_models.country import Country
from database_api import country

app = FastAPI()

@app.post("/country")
def add_country(country_info: Country):
    country.add_country(country_info.country_name, country_info.country_code)
    return {"result": "successfully added country"}

@app.delete("/country/{country_name}")
def delete_country(country_name):
    country.delete_country(country_info.country_name)
    return {"result": "successfully deleted country"}
