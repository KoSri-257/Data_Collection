import logging
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from AES import encrypt, decrypt
from schema import Create, Response, SocialMediaModel
from models import PersonalInfo, HotelInfo, AgencyInfo, PlatformInfo, SocialMediaInfo
from typing import Dict, List
from config import LOG_LEVEL

logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)

def create_personalinfo(input: Create, db: Session) -> PersonalInfo:
    existing_email = db.query(PersonalInfo).filter(PersonalInfo.personal_email == input.personal_email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail=f"Personal email '{input.personal_email}' already exists.")

    existing_eid = db.query(PersonalInfo).filter(PersonalInfo.eid == input.eid).first()
    if existing_eid:
        raise HTTPException(status_code=400, detail=f"Employee ID '{input.eid}' already exists.")
    
    existing_phone = db.query(PersonalInfo).filter(PersonalInfo.personal_phone == input.personal_phone).first()
    if existing_phone:
        raise HTTPException(status_code=400, detail=f"Personal phone '{input.personal_phone}' already exists.")
    
    personal_info = PersonalInfo(
        first_name=input.first_name,
        last_name=input.last_name,
        title=input.title,
        personal_email=input.personal_email,
        eid=input.eid,
        country_code=input.country_code,
        personal_phone=input.personal_phone
        )
    try:
        db.add(personal_info)
        db.flush()
        logger.info(f"Created PersonalInfo with pid: {personal_info.pid}")
    except Exception as e:
        logger.error(f"Error while creating personal info: {str(e)}")
        raise
    return personal_info

def create_hotelinfo(input: Create, db: Session, personal_info: PersonalInfo) -> HotelInfo:
    hotel_info = HotelInfo(
        hotel_name=input.hotel_name,
        marsha_code=input.marsha_code,
        managed_franchise=input.managed_franchise,
        country=input.country,
        state=input.state,
        city=input.city,
        zip_code=input.zip_code,
        pid=personal_info.pid,
    )
    try:
        db.add(hotel_info)
        db.flush()  # To get the hid
        logger.info(f"Created HotelInfo with hid: {hotel_info.hid}")
    except Exception as e:
        logger.error(f"Error while creating personal info: {str(e)}")
        raise
    return hotel_info

def create_agencyinfo(input: Create, db: Session, hotel_info: HotelInfo) -> AgencyInfo:
    try:
        if input.not_applicable:
            return None
        agency_info = AgencyInfo(
            agency_name=input.agency_name,
            primary_contact=input.primary_contact,
            primary_email=input.primary_email,
            primary_phone=input.primary_phone,
            not_applicable=input.not_applicable,
            hid=hotel_info.hid
        )
        db.add(agency_info)
        db.flush() 
        logger.info(f"Created AgencyInfo with aid: {agency_info.aid}")
    except Exception as e:
        logger.error(f"Error while creating personal info: {str(e)}")
        raise
    else:
        return agency_info

def find_platform(platform_inputs: Dict[str, SocialMediaModel], db: Session) -> Dict[str, int]:
    try:
        platform_names = list(platform_inputs.keys())
        platform_info_list = db.query(PlatformInfo).filter(PlatformInfo.platform_name.in_(platform_names)).all()
        if len(platform_info_list) != len(platform_names):
            missing_platforms = set(platform_names) - {platform_info.platform_name for platform_info in platform_info_list}
            logger.error(f"Missing platforms: {', '.join(missing_platforms)}")
            raise HTTPException(status_code=400, detail=f"None of the platforms {', '.join(missing_platforms)} were found in PlatformInfo.")
        platforms_obj = {plat_info.platform_name: plat_info.plid for plat_info in platform_info_list}
        logger.info(f"Found platform IDs: {platforms_obj}")
    except NoResultFound as e:
        logger.error(f"No results found: {e}")
        raise HTTPException(status_code=404, detail="No results found")
    except Exception as e:
        raise
    return platforms_obj

def create_socialmediainfo(input: Create, db: Session, hotel_info: HotelInfo) -> dict: 
    for platform_name, social_media_model in input.platform_inputs.items():
        # existing_pageURL = db.query(SocialMediaInfo).filter(decrypt(SocialMediaInfo.pageURL) == social_media_model.pageURL).first()
        # if existing_pageURL:
        #     raise HTTPException(status_code=400, detail=f"Page URL '{social_media_model.pageURL}' already exists.")

        # existing_pageID = db.query(SocialMediaInfo).filter(decrypt(SocialMediaInfo.pageID) == social_media_model.pageID).first()
        # if existing_pageID:
        #     raise HTTPException(status_code=400, detail=f"Page ID '{social_media_model.pageID}' already exists.")

        platform_ids = find_platform(input.platform_inputs, db) 
        social_media_objects = [] 
        platform_to_info_map = {}

        if platform_name not in platform_ids:
            raise HTTPException(status_code=400, detail=f"Platform {platform_name} not found in PlatformInfo.")
        
        social_media_info = SocialMediaInfo(
            sma_name=social_media_model.sma_name,
            sma_person=social_media_model.sma_person,
            sma_email=social_media_model.sma_email,
            sma_phone=social_media_model.sma_phone,
            pageURL=encrypt(social_media_model.pageURL),
            pageID=encrypt(social_media_model.pageID),
            mi_fbm=social_media_model.mi_fbm,
            added_dcube=social_media_model.added_dcube,
            hid=hotel_info.hid,
            plid=platform_ids[platform_name]
        )
        social_media_objects.append(social_media_info)
        platform_to_info_map[platform_name] = social_media_info

    try:
        db.add_all(social_media_objects)
        db.flush()
        logger.info(f"Created SocialMediaInfo with sid: {social_media_info.sid}")
    except Exception as e:
        raise
    return platform_to_info_map

def build_personal_info(personal_info: PersonalInfo) -> dict:
    try:
        return {
            "first_name": personal_info.first_name,
            "last_name": personal_info.last_name,
            "title": personal_info.title,
            "personal_email": personal_info.personal_email,
            "eid": personal_info.eid,
            "country_code": personal_info.country_code,
            "personal_phone": personal_info.personal_phone
        }
    except Exception as e:
        raise 

def build_hotel_info(hotel_info: HotelInfo) -> dict:
    try:
        return {
            "hotel_name": hotel_info.hotel_name,
            "marsha_code": hotel_info.marsha_code,
            "managed_franchise": hotel_info.managed_franchise,
            "country": hotel_info.country,
            "state": hotel_info.state,
            "city": hotel_info.city,
            "zip_code": hotel_info.zip_code
        }
    except Exception as e:
        raise

def build_agency_info(agency_info: AgencyInfo) -> dict:
    try:
        return {
            "agency_name": agency_info.agency_name if agency_info else None,
            "primary_contact": agency_info.primary_contact if agency_info else None,
            "primary_email": agency_info.primary_email if agency_info else None,
            "primary_phone": agency_info.primary_phone if agency_info else None,
            "not_applicable": agency_info.not_applicable if agency_info else None
        }
    except Exception as e:
        raise

def build_social_media_info_list(social_media_info_list: List[SocialMediaInfo], decrypted_info: Dict[int, dict], db: Session) -> dict:
    result = {}
    for sm_info in social_media_info_list:
        platform_info = db.query(PlatformInfo).filter(PlatformInfo.plid == sm_info.plid).first() 
        if not platform_info:
            raise ValueError(f"No PlatformInfo found for plid: {sm_info.plid}")
        logger.info(f"Platfrom ID: {platform_info.platform_name} and Decrypted data: {decrypted_info.get(sm_info.plid)}")
        decrypted_data = decrypted_info.get(sm_info.plid)
    try:
            result[platform_info.platform_name] = {
                "sma_name": sm_info.sma_name,
                "sma_person": sm_info.sma_person,
                "sma_email": sm_info.sma_email,
                "sma_phone": sm_info.sma_phone,
                "pageURL": decrypted_data.get('pageURL'),
                "pageID": decrypted_data.get('pageID'),
                "mi_fbm": sm_info.mi_fbm,
                "added_dcube": sm_info.added_dcube
            }
    except Exception as e:
        raise 
    return result

def post_info(input: Response, db: Session) -> dict:
    try:
        personal_info = create_personalinfo(input, db)
        hotel_info = create_hotelinfo(input, db, personal_info)
        agency_info = create_agencyinfo(input, db, hotel_info)
        social_media_info = create_socialmediainfo(input, db, hotel_info)
        
        response_data =  {
            "pid": personal_info.pid,
            "hid": hotel_info.hid,
            "aid": agency_info.aid if agency_info else None,
            "sid": [info.sid for info in social_media_info.values()]
        }
    except Exception as e:
        raise
    logger.info(f"Successfully posted info: {response_data}")
    return response_data

def get_info(eid: str, db: Session) -> dict:
    personal_info = db.query(PersonalInfo).filter(PersonalInfo.eid == eid).first()
    if not personal_info:
        logger.error(f"PersonalInfo not found for eid {eid}")
        raise HTTPException(status_code=404, detail="PersonalInfo not found.")

    hotel_info = db.query(HotelInfo).filter(HotelInfo.pid == personal_info.pid).first()
    if not hotel_info:
        logger.error(f"HotelInfo not found for hid {personal_info.pid}")
        raise HTTPException(status_code=404, detail="HotelInfo not found.")

    agency_info = db.query(AgencyInfo).filter(AgencyInfo.hid == hotel_info.hid).first()

    social_media_info = db.query(SocialMediaInfo).filter(SocialMediaInfo.hid == hotel_info.hid).all()
    if not social_media_info:
        logger.error(f"SocialMediaInfo not found for hid {hotel_info.hid}")
        raise HTTPException(status_code=404, detail="SocialMediaInfo not found.")
    try:
        decrypted_info = {
            smi.plid: {
                'pageURL': decrypt(smi.pageURL),
                'pageID': decrypt(smi.pageID)
            }
            for smi in social_media_info
        }
        logger.info(f"Decrypted Info Map: {decrypted_info}")

        response_data = {
            "Personal Info": build_personal_info(personal_info),
            "Hotel Info": build_hotel_info(hotel_info),
            "Agency Info": build_agency_info(agency_info), #  if agency_info else None
            "Social Media Info": build_social_media_info_list(social_media_info, decrypted_info, db),
        }   
    except Exception as e:
        raise
    logger.info(f"Info retrieved successfully for sid {eid}")
    return response_data