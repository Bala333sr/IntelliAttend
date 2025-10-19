#!/usr/bin/env python3
"""
Admin API for IntelliAttend V2 - Timetable Management
Separate implementation to avoid type checking issues
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import jwt
import bcrypt
import logging
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey, and_, or_
from sqlalchemy.orm import sessionmaker, Session
import json

# Create router
router = APIRouter(prefix="/api/admin", tags=["Admin"])

# Security
security = HTTPBearer()

# Logger
logger = logging.getLogger(__name__)

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class ResponseModel(BaseModel):
    success: bool
    status_code: int
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    error: Optional[str] = None

class AdminLoginRequest(BaseModel):
    """Admin login request"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)

class AdminCreateRequest(BaseModel):
    """Create new admin user"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = Field(None, max_length=100)
    role: Optional[str] = Field("admin", max_length=50)

class TimetableCreateRequest(BaseModel):
    """Create new timetable entry"""
    section_id: int
    day_of_week: str
    slot_number: Optional[int]
    slot_type: str
    start_time: str  # Format: HH:MM
    end_time: str    # Format: HH:MM
    subject_code: Optional[str] = Field(None, max_length=20)
    subject_name: Optional[str] = Field(None, max_length=100)
    faculty_name: Optional[str] = Field(None, max_length=100)
    room_number: Optional[str] = Field(None, max_length=20)
    
    @validator('slot_type')
    def validate_slot_type(cls, v):
        allowed_types = ['lecture', 'lab', 'break', 'lunch', 'free']
        if v not in allowed_types:
            raise ValueError(f'slot_type must be one of {allowed_types}')
        return v
    
    @validator('day_of_week')
    def validate_day_of_week(cls, v):
        allowed_days = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY']
        if v not in allowed_days:
            raise ValueError(f'day_of_week must be one of {allowed_days}')
        return v

class TimetableUpdateRequest(BaseModel):
    """Update timetable entry"""
    section_id: Optional[int] = None
    day_of_week: Optional[str] = None
    slot_number: Optional[int] = None
    slot_type: Optional[str] = None
    start_time: Optional[str] = None  # Format: HH:MM
    end_time: Optional[str] = None    # Format: HH:MM
    subject_code: Optional[str] = Field(None, max_length=20)
    subject_name: Optional[str] = Field(None, max_length=100)
    faculty_name: Optional[str] = Field(None, max_length=100)
    room_number: Optional[str] = Field(None, max_length=20)
    
    @validator('slot_type')
    def validate_slot_type(cls, v):
        if v is not None:
            allowed_types = ['lecture', 'lab', 'break', 'lunch', 'free']
            if v not in allowed_types:
                raise ValueError(f'slot_type must be one of {allowed_types}')
        return v
    
    @validator('day_of_week')
    def validate_day_of_week(cls, v):
        if v is not None:
            allowed_days = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY']
            if v not in allowed_days:
                raise ValueError(f'day_of_week must be one of {allowed_days}')
        return v

# ============================================================================
# DATABASE MODELS (Simplified)
# ============================================================================

class Admin:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class Timetable:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class Section:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class TimetableHistory:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

# ============================================================================
# CONFIGURATION
# ============================================================================

SECRET_KEY = "your-secret-key-change-in-production"
JWT_ALGORITHM = "HS256"

# ============================================================================
# AUTHENTICATION FUNCTIONS
# ============================================================================

def create_access_token(data: dict) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=JWT_ALGORITHM)

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def get_db():
    """Mock database session dependency"""
    # This would be replaced with actual database connection in a real implementation
    pass

def verify_admin_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify admin JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ============================================================================
# ADMIN AUTHENTICATION ENDPOINTS
# ============================================================================

@router.post("/login", response_model=ResponseModel)
async def admin_login(request: AdminLoginRequest):
    """Admin login endpoint - mock implementation"""
    try:
        # In a real implementation, this would query the database
        # For now, we'll return a mock response
        token = create_access_token({
            "type": "admin",
            "admin_id": 1,
            "username": request.username,
            "role": "super_admin"
        })
        
        return ResponseModel(
            success=True,
            status_code=200,
            message="Login successful",
            data={
                "access_token": token,
                "refresh_token": token,
                "admin": {
                    "admin_id": 1,
                    "username": request.username,
                    "email": "admin@intelliattend.com",
                    "full_name": "System Administrator",
                    "role": "super_admin",
                    "is_active": True
                }
            }
        )
    except Exception as e:
        logger.error(f"Admin login error: {str(e)}")
        return ResponseModel(
            success=False,
            status_code=500,
            error=str(e)
        )

# ============================================================================
# TIMETABLE MANAGEMENT ENDPOINTS
# ============================================================================

@router.get("/timetable")
async def get_all_timetable_entries(
    section_id: Optional[int] = None,
    day_of_week: Optional[str] = None,
    token_data: dict = Depends(verify_admin_token),
    db: Session = Depends(get_db)
):
    """Get all timetable entries with optional filtering"""
    try:
        query = db.query(Timetable)
        
        if section_id:
            query = query.filter(Timetable.section_id == section_id)
        
        if day_of_week:
            query = query.filter(Timetable.day_of_week == day_of_week.upper())
        
        timetable_entries = query.order_by(Timetable.day_of_week, Timetable.slot_number).all()
        
        entries = []
        for entry in timetable_entries:
            # Get section name
            section = db.query(Section).filter(Section.id == entry.section_id).first()
            
            entries.append({
                "id": int(entry.id),
                "section_id": int(entry.section_id),
                "section_name": section.section_name if section else None,
                "day_of_week": entry.day_of_week,
                "slot_number": int(entry.slot_number) if entry.slot_number else None,
                "slot_type": entry.slot_type,
                "start_time": str(entry.start_time) if entry.start_time else None,
                "end_time": str(entry.end_time) if entry.end_time else None,
                "subject_code": entry.subject_code,
                "subject_name": entry.subject_name,
                "faculty_name": entry.faculty_name,
                "room_number": entry.room_number
            })
        
        return ResponseModel(
            success=True,
            status_code=200,
            message=f"Retrieved {len(entries)} timetable entries",
            data={"entries": entries}
        )
    except Exception as e:
        logger.error(f"Error fetching timetable entries: {str(e)}")
        return ResponseModel(
            success=False,
            status_code=500,
            error=str(e)
        )

@router.post("/timetable")
async def create_timetable_entry(
    request: TimetableCreateRequest,
    reason: Optional[str] = None,
    token_data: dict = Depends(verify_admin_token),
    db: Session = Depends(get_db)
):
    """Create new timetable entry"""
    try:
        admin_id = token_data.get("admin_id")
        
        # Validate section exists
        section = db.query(Section).filter(Section.id == request.section_id).first()
        if not section:
            return ResponseModel(
                success=False,
                status_code=400,
                error="Section not found"
            )
        
        # Check for time conflicts
        start_time_obj = datetime.strptime(request.start_time, "%H:%M").time()
        end_time_obj = datetime.strptime(request.end_time, "%H:%M").time()
        
        conflict = db.query(Timetable).filter(
            Timetable.section_id == request.section_id,
            Timetable.day_of_week == request.day_of_week.upper(),
            Timetable.start_time < end_time_obj,
            Timetable.end_time > start_time_obj
        ).first()
        
        if conflict:
            return ResponseModel(
                success=False,
                status_code=400,
                error="Time conflict with existing timetable entry"
            )
        
        # Create new timetable entry
        new_entry = Timetable()
        setattr(new_entry, 'section_id', request.section_id)
        setattr(new_entry, 'day_of_week', request.day_of_week.upper())
        setattr(new_entry, 'slot_number', request.slot_number)
        setattr(new_entry, 'slot_type', request.slot_type.lower())
        setattr(new_entry, 'start_time', start_time_obj)
        setattr(new_entry, 'end_time', end_time_obj)
        setattr(new_entry, 'subject_code', request.subject_code)
        setattr(new_entry, 'subject_name', request.subject_name)
        setattr(new_entry, 'faculty_name', request.faculty_name)
        setattr(new_entry, 'room_number', request.room_number)
        
        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)
        
        # Log the change in history
        history_entry = TimetableHistory()
        setattr(history_entry, 'timetable_id', int(new_entry.id))
        setattr(history_entry, 'action', "CREATE")
        setattr(history_entry, 'old_data', None)
        setattr(history_entry, 'new_data', json.dumps({
            "section_id": int(new_entry.section_id),
            "day_of_week": new_entry.day_of_week,
            "slot_number": int(new_entry.slot_number) if new_entry.slot_number else None,
            "slot_type": new_entry.slot_type,
            "start_time": str(new_entry.start_time),
            "end_time": str(new_entry.end_time),
            "subject_code": new_entry.subject_code,
            "subject_name": new_entry.subject_name,
            "faculty_name": new_entry.faculty_name,
            "room_number": new_entry.room_number
        }))
        setattr(history_entry, 'changed_by', admin_id)
        setattr(history_entry, 'reason', reason)
        
        db.add(history_entry)
        db.commit()
        
        return ResponseModel(
            success=True,
            status_code=201,
            message="Timetable entry created successfully",
            data={"entry_id": int(new_entry.id)}
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating timetable entry: {str(e)}")
        return ResponseModel(
            success=False,
            status_code=500,
            error=str(e)
        )

@router.put("/timetable/{timetable_id}")
async def update_timetable_entry(
    timetable_id: int,
    request: TimetableUpdateRequest,
    reason: Optional[str] = None,
    token_data: dict = Depends(verify_admin_token),
    db: Session = Depends(get_db)
):
    """Update existing timetable entry"""
    try:
        admin_id = token_data.get("admin_id")
        
        # Get existing entry
        existing_entry = db.query(Timetable).filter(Timetable.id == timetable_id).first()
        
        if not existing_entry:
            return ResponseModel(
                success=False,
                status_code=404,
                error="Timetable entry not found"
            )
        
        # Store old data for history
        old_data = {
            "section_id": int(existing_entry.section_id),
            "day_of_week": existing_entry.day_of_week,
            "slot_number": int(existing_entry.slot_number) if existing_entry.slot_number else None,
            "slot_type": existing_entry.slot_type,
            "start_time": str(existing_entry.start_time),
            "end_time": str(existing_entry.end_time),
            "subject_code": existing_entry.subject_code,
            "subject_name": existing_entry.subject_name,
            "faculty_name": existing_entry.faculty_name,
            "room_number": existing_entry.room_number
        }
        
        # Check for time conflicts if time is being updated
        start_time = datetime.strptime(request.start_time, "%H:%M").time() if request.start_time else existing_entry.start_time
        end_time = datetime.strptime(request.end_time, "%H:%M").time() if request.end_time else existing_entry.end_time
        
        if request.start_time or request.end_time:
            conflict = db.query(Timetable).filter(
                Timetable.id != timetable_id,
                Timetable.section_id == (request.section_id if request.section_id else int(existing_entry.section_id)),
                Timetable.day_of_week == (request.day_of_week.upper() if request.day_of_week else existing_entry.day_of_week),
                Timetable.start_time < end_time,
                Timetable.end_time > start_time
            ).first()
            
            if conflict:
                return ResponseModel(
                    success=False,
                    status_code=400,
                    error="Time conflict with existing timetable entry"
                )
        
        # Update fields
        if request.section_id is not None:
            # Validate section exists
            section = db.query(Section).filter(Section.id == request.section_id).first()
            if not section:
                return ResponseModel(
                    success=False,
                    status_code=400,
                    error="Section not found"
                )
            setattr(existing_entry, 'section_id', request.section_id)
        
        if request.day_of_week is not None:
            setattr(existing_entry, 'day_of_week', request.day_of_week.upper())
        
        if request.slot_number is not None:
            setattr(existing_entry, 'slot_number', request.slot_number)
        
        if request.slot_type is not None:
            setattr(existing_entry, 'slot_type', request.slot_type.lower())
        
        if request.start_time is not None:
            setattr(existing_entry, 'start_time', start_time)
        
        if request.end_time is not None:
            setattr(existing_entry, 'end_time', end_time)
        
        if request.subject_code is not None:
            setattr(existing_entry, 'subject_code', request.subject_code)
        
        if request.subject_name is not None:
            setattr(existing_entry, 'subject_name', request.subject_name)
        
        if request.faculty_name is not None:
            setattr(existing_entry, 'faculty_name', request.faculty_name)
        
        if request.room_number is not None:
            setattr(existing_entry, 'room_number', request.room_number)
        
        db.commit()
        
        # Log the change in history
        new_data = {
            "section_id": int(existing_entry.section_id),
            "day_of_week": existing_entry.day_of_week,
            "slot_number": int(existing_entry.slot_number) if existing_entry.slot_number else None,
            "slot_type": existing_entry.slot_type,
            "start_time": str(existing_entry.start_time),
            "end_time": str(existing_entry.end_time),
            "subject_code": existing_entry.subject_code,
            "subject_name": existing_entry.subject_name,
            "faculty_name": existing_entry.faculty_name,
            "room_number": existing_entry.room_number
        }
        
        history_entry = TimetableHistory()
        setattr(history_entry, 'timetable_id', timetable_id)
        setattr(history_entry, 'action', "UPDATE")
        setattr(history_entry, 'old_data', json.dumps(old_data))
        setattr(history_entry, 'new_data', json.dumps(new_data))
        setattr(history_entry, 'changed_by', admin_id)
        setattr(history_entry, 'reason', reason)
        
        db.add(history_entry)
        db.commit()
        
        return ResponseModel(
            success=True,
            status_code=200,
            message="Timetable entry updated successfully",
            data={"entry_id": timetable_id}
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating timetable entry: {str(e)}")
        return ResponseModel(
            success=False,
            status_code=500,
            error=str(e)
        )

@router.delete("/timetable/{timetable_id}")
async def delete_timetable_entry(
    timetable_id: int,
    reason: Optional[str] = None,
    token_data: dict = Depends(verify_admin_token),
    db: Session = Depends(get_db)
):
    """Delete timetable entry"""
    try:
        admin_id = token_data.get("admin_id")
        
        # Get existing entry
        existing_entry = db.query(Timetable).filter(Timetable.id == timetable_id).first()
        
        if not existing_entry:
            return ResponseModel(
                success=False,
                status_code=404,
                error="Timetable entry not found"
            )
        
        # Store data for history
        old_data = {
            "section_id": int(existing_entry.section_id),
            "day_of_week": existing_entry.day_of_week,
            "slot_number": int(existing_entry.slot_number) if existing_entry.slot_number else None,
            "slot_type": existing_entry.slot_type,
            "start_time": str(existing_entry.start_time),
            "end_time": str(existing_entry.end_time),
            "subject_code": existing_entry.subject_code,
            "subject_name": existing_entry.subject_name,
            "faculty_name": existing_entry.faculty_name,
            "room_number": existing_entry.room_number
        }
        
        # Delete the entry
        db.delete(existing_entry)
        db.commit()
        
        # Log the change in history
        history_entry = TimetableHistory()
        setattr(history_entry, 'timetable_id', timetable_id)
        setattr(history_entry, 'action', "DELETE")
        setattr(history_entry, 'old_data', json.dumps(old_data))
        setattr(history_entry, 'new_data', None)
        setattr(history_entry, 'changed_by', admin_id)
        setattr(history_entry, 'reason', reason)
        
        db.add(history_entry)
        db.commit()
        
        return ResponseModel(
            success=True,
            status_code=200,
            message="Timetable entry deleted successfully"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting timetable entry: {str(e)}")
        return ResponseModel(
            success=False,
            status_code=500,
            error=str(e)
        )