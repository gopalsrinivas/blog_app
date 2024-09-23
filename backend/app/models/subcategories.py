from sqlalchemy import Column, String, Boolean, DateTime, Integer, func, ForeignKey
from app.core.database import Base

class Subcategory(Base):
    __tablename__ = 'subcategories'

    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    subcat_id = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
    created_on = Column(DateTime, default=func.now(), nullable=False)
    updated_on = Column(DateTime, onupdate=func.now())

    def __repr__(self):
        return f"<Subcategory {self.name} (ID: {self.subcat_id}) created on {self.created_on}>"
