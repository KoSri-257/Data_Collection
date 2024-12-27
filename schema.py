from pydantic import BaseModel, model_validator
from typing import Optional, Dict, List
from fastapi import HTTPException
import re

class Base(BaseModel):
    first_name: str
    last_name: str
    title: str
    personal_email: str
    eid: str
    country_code: str
    personal_phone: str 
    hotel_name: str
    marsha_code: str
    managed_franchise: str
    country: str
    state: str
    city: str
    zip_code: int
    agency_name: Optional[str] = None
    primary_contact: Optional[str] = None
    primary_email: Optional[str] = None
    primary_phone: Optional[str] = None
    not_applicable: Optional[bool] = None

    @model_validator(mode='before')
    def validate_personalFields(cls, values: dict):
        required_fields = ["first_name", "last_name", "title", "personal_email", "eid", "country_code", "personal_phone"]
        missing_fields = [field for field in required_fields if not values.get(field)]
        try:
            if missing_fields:
                raise HTTPException(status_code=422, detail=f"Missing '{', '.join(missing_fields)}' from 'PersonalInfo'")
        except Exception as e:
             raise
        return values
    
    @model_validator(mode='before')
    def validate_hotelFields(cls, values: dict):
        required_fields = ["hotel_name", "marsha_code", "managed_franchise", "country", "state", "city", "zip_code"]
        missing_fields = [field for field in required_fields if not values.get(field)]
        try:
            if missing_fields:
                raise HTTPException(status_code=422, detail=f"Missing '{', '.join(missing_fields)}' from 'HotelInfo'")
        except Exception as e:
             raise
        return values

    @model_validator(mode='before')
    def validate_agencyFields(cls, values: dict):
        not_applicable = values.get('not_applicable')
        try:
            if not not_applicable:
                missing_fields = [field for field in ['agency_name', 'primary_contact', 'primary_email', 'primary_phone'] if not values.get(field)]
                if missing_fields:
                    raise HTTPException(status_code=422, detail=f"Missing '{', '.join(missing_fields)}' from 'AgencyInfo'")
        except Exception as e:
            raise 
        return values
    
    @model_validator(mode='before')
    def validate_email_phone(cls, values: dict):
        try:
            personal_email = values.get('personal_email')
            if personal_email:
                    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', personal_email):
                        raise HTTPException(status_code=422, detail=f"Invalid email structure for {personal_email}. It should follow structure: user@example.com")
            personal_phone = values.get('personal_phone')
            if personal_phone:
                    if not re.match(r'^\d{10}$', personal_phone):
                        raise HTTPException(status_code=422, detail=f"Invalid phone number for {personal_phone}. It must be exactly 10 digits.")
            primary_email = values.get('primary_email')
            if primary_email:
                    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',  primary_email):
                        raise HTTPException(status_code=422, detail=f"Invalid email structure for {primary_email}. It should follow structure: user@example.com")
            primary_phone = values.get('primary_phone')
            if primary_phone:
                    if not re.match(r'^\d{10}$', primary_phone):
                        raise HTTPException(status_code=422, detail=f"Invalid phone number for {primary_phone}. It must be exactly 10 digits.")
        except Exception as e:
            raise
        return values

class SocialMediaModel(BaseModel):
    sma_name: str
    sma_person: str
    sma_email: str
    sma_phone: str
    pageURL: str
    pageID: str
    mi_fbm: bool
    added_dcube: Optional[bool]

    @model_validator(mode='before')
    def validate_socialmediaFields(cls, values: dict):
        required_fields = ["sma_name", "sma_person", "sma_email", "sma_phone", "pageURL", "pageID"]
        missing_fields = [field for field in required_fields if not values.get(field)]
        try:
            if missing_fields:
                raise HTTPException(status_code=422, detail=f"Missing '{', '.join(missing_fields)}' from 'SocialMediaInfo'")
            sma_email = values.get('sma_email')
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', sma_email):
                raise HTTPException(status_code=422, detail=f"Invalid email structure for {sma_email}. It should follow structure: user@example.com")
            sma_phone = values.get('sma_phone')
            if not re.match(r'^\d{10}$', sma_phone):
                raise HTTPException(status_code=422, detail=f"Invalid phone number for {sma_phone}. It must be exactly 10 digits.")
            pageURL = values.get('pageURL')
            if not re.match(r'^https://www\..*\.com(/.*)?', pageURL):
                raise HTTPException(status_code=422, detail=f"Invalid URL for {pageURL}.")
            mi_fbm = values.get('mi_fbm')
            added_dcube = values.get('added_dcube')
            if mi_fbm:
                values['added_dcube'] = True
            elif mi_fbm is False and added_dcube is None:
                raise HTTPException(status_code=422, detail="added_dcube must be specified if MI FBM is No.")
            elif mi_fbm is None:
                raise HTTPException(status_code=422, detail="mi_fbm is a required field.")
        except Exception as e:
            raise
        return values

class Create(Base):
    platform_inputs: Dict[str, SocialMediaModel]

    @model_validator(mode="before")
    def validate_platforms(cls, values: dict):
        try:
            platform_inputs = values.get('platform_inputs', {})
            if not platform_inputs:
                raise HTTPException(status_code=422, detail="At least one platform input is required.")
        except Exception as e:
            raise 
        return values

class Response(Base):
    pid: int  
    hid: int
    aid: Optional[int] = None
    sid: List[int]

    class Config:
        from_attributes = True
