from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    cat_id = Column(String(50), nullable=False, unique=True)
    name = Column(String(255), nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
    created_on = Column(DateTime, default=func.now(), nullable=False)
    updated_on = Column(DateTime, onupdate=func.now())


    subcategories = relationship("Subcategory", back_populates="category")
    
    def __repr__(self):
        return f"<Category {self.name} (ID: {self.cat_id}) created on {self.created_on}>"
