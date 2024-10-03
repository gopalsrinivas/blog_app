from sqlalchemy import Column, String, Boolean, DateTime, Integer, func, ForeignKey
from app.core.database import Base
from sqlalchemy.orm import relationship

class Subcategory(Base):
    __tablename__ = 'subcategories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    subcat_id = Column(String(50), nullable=False, unique=True)
    name = Column(String(255), nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
    created_on = Column(DateTime, default=func.now(), nullable=False)
    updated_on = Column(DateTime, onupdate=func.now())
    
    # Relationship with Blog
    category = relationship("Category", back_populates="subcategories")
    blogs = relationship("Blog", back_populates="subcategory")

    def __repr__(self):
        return f"<Subcategory {self.name} (ID: {self.subcat_id}) created on {self.created_on}>"
