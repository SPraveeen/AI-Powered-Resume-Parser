from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime

class ResumeUpload(BaseModel):
    filename: str

class ParsedResume(BaseModel):
    id: int
    filename: str
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: Optional[List[str]] = None
    experience: Optional[List[Dict[str, Any]]] = None
    education: Optional[List[Dict[str, Any]]] = None
    experience_years: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class ResumeResponse(BaseModel):
    message: str
    resume_id: int
    parsed_data: Dict[str, Any]