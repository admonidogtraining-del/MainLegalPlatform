from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DocumentCreate(BaseModel):
    type: str
    title: str
    summary: Optional[str] = None
    case_number: Optional[str] = None
    court: Optional[str] = None
    judge: Optional[str] = None
    law_area: Optional[str] = None
    urgency: Optional[str] = "low"
    source_url: Optional[str] = None
    pub_date: Optional[str] = None
    raw_content: Optional[str] = None
    scraped_from: Optional[str] = "manual"


class DocumentOut(BaseModel):
    id: int
    type: str
    title: str
    summary: Optional[str]
    case_number: Optional[str]
    court: Optional[str]
    judge: Optional[str]
    law_area: Optional[str]
    urgency: str
    source_url: Optional[str]
    pub_date: Optional[str]
    bookmarked: bool
    raw_content: Optional[str]
    scraped_from: Optional[str]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class StatsOut(BaseModel):
    urgent: int
    bookmarked: int
    rulings: int
    bills: int
    legislation: int
    total: int


class BookmarkToggle(BaseModel):
    bookmarked: bool


class UrgencyUpdate(BaseModel):
    urgency: str


class ScrapeStatus(BaseModel):
    last_run: Optional[str]
    last_count: int
    is_running: bool
