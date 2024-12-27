from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class PersonalInfo(Base):
    __tablename__ = "personal_info"
    pid = Column(Integer, primary_key=True, index=True, autoincrement=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    title = Column(String, nullable=False)
    personal_email = Column(String, nullable=False, unique=True)
    eid = Column(String, nullable=False, unique=True)
    country_code = Column(String, nullable=False)
    personal_phone = Column(String, nullable=False, unique=True)
    # One-to-one relationship with HotelInfo
    hotel_info = relationship("HotelInfo", back_populates="personal_info", uselist=False, cascade="all, delete-orphan")

class HotelInfo(Base):
    __tablename__ = "hotel_info"
    hid = Column(Integer, primary_key=True, index=True, autoincrement=True)
    hotel_name = Column(String, nullable=False)
    marsha_code = Column(String, nullable=False)
    managed_franchise = Column(String, nullable=False)
    country = Column(String, nullable=False)
    state = Column(String, nullable=False)
    city = Column(String, nullable=False)
    zip_code = Column(Integer, nullable=False)
    pid = Column(Integer, ForeignKey("personal_info.pid"), nullable=False, unique=True)
    # One-to-one relationship with PersonalInfo & AgencyInfo
    personal_info = relationship("PersonalInfo", back_populates="hotel_info", uselist=False)
    agency_info = relationship("AgencyInfo", back_populates="hotel_info", uselist=False, cascade="all, delete-orphan")
    # One-to-many relationship with SocialMediaInfo
    social_media_info = relationship("SocialMediaInfo", back_populates="hotel_info", cascade="all, delete-orphan")

class AgencyInfo(Base):
    __tablename__ = "agency_info"
    aid = Column(Integer, primary_key=True, autoincrement=True)
    agency_name = Column(String, nullable=False)
    primary_contact = Column(String, nullable=False)
    primary_email = Column(String, nullable=False)
    primary_phone = Column(String, nullable=False)
    not_applicable = Column(Boolean, default=False, nullable=True)
    hid = Column(Integer, ForeignKey("hotel_info.hid"), nullable=False, unique=True)
    # One-to-one relationship with HotelInfo
    hotel_info = relationship("HotelInfo", back_populates="agency_info")

class PlatformInfo(Base): 
    __tablename__ = "platform_info"
    plid = Column(Integer, primary_key=True, autoincrement=True)
    platform_name = Column(String, unique=True, nullable=False)
    # One-to-many relationship with SocialMediaInfo
    social_media_info = relationship("SocialMediaInfo", back_populates="platform_info", cascade="all, delete-orphan")

class SocialMediaInfo(Base):
    __tablename__ = "social_media_info"
    sid = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sma_name = Column(String, nullable=False)
    sma_person = Column(String, nullable=False)
    sma_email = Column(String, nullable=False)
    sma_phone = Column(String, nullable=False)
    pageURL = Column(String, nullable=False, unique=True)
    pageID = Column(String, nullable=False, unique=True)
    mi_fbm = Column(Boolean, nullable=False, default=False)
    added_dcube = Column(Boolean, nullable=False, default=False)
    hid = Column(Integer, ForeignKey("hotel_info.hid"), nullable=False)
    plid = Column(Integer, ForeignKey("platform_info.plid"), nullable=False)
    # Many-to-one relationship with HotelInfo & PlatformInfo
    hotel_info = relationship("HotelInfo", back_populates="social_media_info")
    platform_info = relationship("PlatformInfo", back_populates="social_media_info")
