from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.vendor import Vendor
from app.schemas.vendor import VendorCreate, VendorResponse
from typing import List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/vendors", tags=["Vendors"])

@router.post("/", response_model=VendorResponse)
def create_vendor(vendor: VendorCreate, db: Session = Depends(get_db)):
  
    existing_vendor = db.query(Vendor).filter(Vendor.name == vendor.name).first()
    if existing_vendor:
        raise HTTPException(
            status_code=409, 
            detail=f"Vendor with name '{vendor.name}' already exists"
        )
    
    new_vendor = Vendor(
        name=vendor.name,
        email=vendor.email
    )
    
    db.add(new_vendor)
    db.commit()
    db.refresh(new_vendor)
    
    logger.info(f"Created new vendor: {new_vendor.name} (ID: {new_vendor.id})")
    
    return new_vendor

@router.get("/", response_model=List[VendorResponse])
def get_vendors(db: Session = Depends(get_db)):
    vendors = db.query(Vendor).all()
    return vendors

@router.get("/{vendor_id}", response_model=VendorResponse)
def get_vendor(vendor_id: int, db: Session = Depends(get_db)):
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    
    return vendor
