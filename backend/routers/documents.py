from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, List
from database import get_db
import models
import schemas

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.get("", response_model=List[schemas.DocumentOut])
def list_documents(
    type: Optional[str] = Query(None),
    urgency: Optional[str] = Query(None),
    bookmarked: Optional[bool] = Query(None),
    q: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    query = db.query(models.Document)

    if type and type != "all":
        query = query.filter(models.Document.type == type)
    if urgency and urgency != "all":
        query = query.filter(models.Document.urgency == urgency)
    if bookmarked is not None:
        query = query.filter(models.Document.bookmarked == bookmarked)
    if q:
        search = f"%{q}%"
        query = query.filter(
            or_(
                models.Document.title.ilike(search),
                models.Document.summary.ilike(search),
                models.Document.case_number.ilike(search),
            )
        )

    return query.order_by(models.Document.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/stats", response_model=schemas.StatsOut)
def get_stats(db: Session = Depends(get_db)):
    total = db.query(models.Document).count()
    urgent = db.query(models.Document).filter(models.Document.urgency == "high").count()
    bookmarked = db.query(models.Document).filter(models.Document.bookmarked == True).count()
    rulings = db.query(models.Document).filter(models.Document.type == "ruling").count()
    bills = db.query(models.Document).filter(models.Document.type == "bill").count()
    legislation = db.query(models.Document).filter(models.Document.type == "legislation").count()
    return schemas.StatsOut(
        urgent=urgent,
        bookmarked=bookmarked,
        rulings=rulings,
        bills=bills,
        legislation=legislation,
        total=total,
    )


@router.get("/{doc_id}", response_model=schemas.DocumentOut)
def get_document(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.post("", response_model=schemas.DocumentOut, status_code=201)
def create_document(payload: schemas.DocumentCreate, db: Session = Depends(get_db)):
    doc = models.Document(**payload.model_dump())
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.patch("/{doc_id}/bookmark", response_model=schemas.DocumentOut)
def toggle_bookmark(doc_id: int, payload: schemas.BookmarkToggle, db: Session = Depends(get_db)):
    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    doc.bookmarked = payload.bookmarked
    db.commit()
    db.refresh(doc)
    return doc


@router.patch("/{doc_id}/urgency", response_model=schemas.DocumentOut)
def update_urgency(doc_id: int, payload: schemas.UrgencyUpdate, db: Session = Depends(get_db)):
    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if payload.urgency not in ("high", "medium", "low"):
        raise HTTPException(status_code=400, detail="urgency must be high/medium/low")
    doc.urgency = payload.urgency
    db.commit()
    db.refresh(doc)
    return doc


@router.delete("/{doc_id}", status_code=204)
def delete_document(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(doc)
    db.commit()
