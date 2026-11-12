from fastapi import FastAPI
from base_models.country import Country
import database_api as db_api

app = FastAPI()

@app.post("/create_country")
def create_country(country_info: Country):
    db_api.country.create_country(country_info.country_name, country_info.country_code)
    return {"result": "successfully added country"}



