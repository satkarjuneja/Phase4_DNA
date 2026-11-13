from datetime import date

from pydantic import BaseModel


class Athlete(BaseModel):
    athlete_id: str
    member_id: int
    email_address: str
    phone_number: str
    date_of_birth: date
    gender: str
    country_name: str
    company_name: str | None = None
    street: str | None = None
    city: str | None = None
    postal_code: str | None = None


class AthleteRegistration(BaseModel):
    first_name: str
    last_name: str
    athlete_id: str
    email_address: str
    phone_number: str
    date_of_birth: date
    gender: str
    country_name: str
    company_name: str | None = None
    street: str | None = None
    city: str | None = None
    postal_code: str | None = None


class AthleteProfileUpdate(BaseModel):
    first_name: str
    last_name: str
    email_address: str
    phone_number: str
    company_name: str | None = None
    street: str | None = None
    city: str | None = None
    postal_code: str | None = None
