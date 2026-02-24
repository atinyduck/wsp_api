# models.py

from pydantic import BaseModel, Field
from datetime import date, time
from typing import List

# ========================================================
# --- Driver Models --- 

class DriverBase(BaseModel):
    """ Base model for a driver in Washington State Patrol system. """
    First_Name: str = Field(..., example="John")
    Last_Name: str = Field(..., example="Doe")
    Address: str = Field(..., example="123 Main St, Springfield, WA")
    Birth_Date: date = Field(..., example="1980-01-01") 
    License_Number: str = Field(..., example="WDL123456789")
    License_State: str = Field(..., min_length=2, max_length=2, example="WA")
    
class DriverCreate(DriverBase):
    """ Model for creating a new driver record. """
    pass

class DriverResponse(DriverBase):
    """ Model for returning driver information. """
    Driver_ID: int

    class Config:
        from_attributes = True
        
# --- End of Driver Models ---
# ========================================================
# --- Officer Models --- 

class OfficerBase(BaseModel):
    """ Base model for an officer in Washington State Patrol system. """
    Badge_Number: str = Field(..., min_length=5, example="12345")
    First_Name: str = Field(..., example="John")
    Last_Name: str = Field(..., example="Doe")
    
class OfficerCreate(OfficerBase):
    """ Model for creating a new officer record. """
    pass

class OfficerResponse(OfficerBase):
    """ Model for returning officer information. """
    Officer_ID: int

    class Config:
        from_attributes = True

# --- End of Officer Models ---
# ========================================================
# --- Vehicle Models --- 

class VehicleBase(BaseModel):
    """ Base model for a vehicle in Washing State Patrol system. """
    VIN: str = Field(..., min_length=17, max_length=17, example="1HGCM82633A123456")
    Make: str = Field(..., example="Honda")
    Model: str = Field(..., example="Accord")
    Color: str = Field(..., example="Blue")
    License_Plate: str = Field(..., example="ABC1234")
    License_State: str = Field(..., min_length=2, max_length=2, example="WA")

class VehicleCreate(VehicleBase):
    """ Model for creating a new vehicle record. """
    pass

class VehicleResponse(VehicleBase):
    """ Model for returning vehicle information. """
    class Config:
        from_attributes = True

# --- End of Vehicle Models ---
# ========================================================
# --- Correction Notice Models --- 

class CorrectionNoticeBase(BaseModel):
    """ Base model for a correction notice in Washing State Patrol system. """
    Violation_Date: date = Field(..., example="2024-01-01")
    Violation_Time: str = Field(..., example="14:30:00")
    Location: str = Field(..., example="I-5 Northbound")
    Driver_ID: int = Field(..., example=1)
    Officer_ID: int = Field(..., example=101)
    VIN: str = Field(..., example="1HGCM82633A123456")
    Violations: List[str] = Field(..., example=["SPEED0110", "DUI"])
    

class CorrectionNoticeCreate(CorrectionNoticeBase):
    """ Model for creating a new correction notice record. """
    pass

class CorrectionNoticeResponse(CorrectionNoticeBase):
    """ Model for returning correction notice information. """
    Notice_ID: int

    class Config:
        from_attributes = True
        
# --- End of Correction Notice Models ---
# ========================================================
# --- Violation Models --- 

class ViolationBase(BaseModel):
    """ Base model for a violation in Washing State Patrol system. """
    Violation_Code: str = Field(..., example="SPD0110")
    Violation_Description: str = Field(..., example="Vehicle Speeding by 1-10 mph over limit.")

class ViolationCreate(ViolationBase):
    """ Model for creating a new violation record. """
    pass 

class ViolationResponse(ViolationBase):
    """ Model for returning violation information. """
    class Config:
        from_attributes = True
        
# --- End of Violation Models ---
# ========================================================
# --- NoticeViolation Models --- 

class NoticeViolationBase(BaseModel):
    """ Base model for a notice violation in Washing State Patrol system. """
    Violation_Code: str = Field(..., example="SPD0110")
    
class NoticeViolationCreate(NoticeViolationBase):
    """ Model for creating a new notice violation record. """
    pass 

class NoticeViolationResponse(NoticeViolationBase):
    """ Model for returning notice violation information. """
    Notice_ID: int = Field(..., example=1)

    class Config:
        from_attributes = True

# --- End of NoticeViolation Models ---
# ========================================================
# --- Authentication Token Models ---

class Token(BaseModel):
    """ Model for returning authentication token information. """
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """ Model for returning token data information. """
    username: str | None = None

# --- End of Authentication Token Models ---
# ========================================================
# end of models.py