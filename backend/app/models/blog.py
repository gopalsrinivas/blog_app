from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, func, ForeignKey
from app.core.database import Base


class Blog(Base):
    __tablename__ = 'blog'

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    subcategory_id = Column(Integer, ForeignKey(
        'subcategories.id'), nullable=True)
    blog_id = Column(String(50), nullable=False, unique=True)
    title = Column(String(255), nullable=False, unique=True)
    content = Column(Text, nullable=False)
    image = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_on = Column(DateTime, default=func.now(), nullable=False)
    updated_on = Column(DateTime, onupdate=func.now())

    def __repr__(self):
        return f"<Blog {self.title} (ID: {self.blog_id}) created on {self.created_on}>"
