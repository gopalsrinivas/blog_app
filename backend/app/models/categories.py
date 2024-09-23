from sqlalchemy import Column, String, Boolean, DateTime, Integer, func
from app.core.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    cat_id = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
    created_on = Column(DateTime, default=func.now(), nullable=False)
    updated_on = Column(DateTime, onupdate=func.now())

    def __repr__(self):
        return f"<Category {self.name} created on {self.created_on}>"
