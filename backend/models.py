from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    # 'legislation' | 'ruling' | 'bill'
    type = Column(String, nullable=False, index=True)
    title = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    case_number = Column(String, nullable=True)
    court = Column(String, nullable=True)
    judge = Column(String, nullable=True)
    # comma-separated: עבודה,מקרקעין
    law_area = Column(String, nullable=True)
    # 'high' | 'medium' | 'low'
    urgency = Column(String, default="low")
    source_url = Column(String, nullable=True)
    pub_date = Column(String, nullable=True)
    bookmarked = Column(Boolean, default=False)
    raw_content = Column(Text, nullable=True)
    # 'knesset' | 'elyon1' | 'supreme' | 'manual'
    scraped_from = Column(String, default="manual")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
