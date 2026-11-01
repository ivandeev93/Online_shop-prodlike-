from sqlalchemy import Boolean, Integer, ForeignKey, Text, DateTime
from sqlalchemy import CheckConstraint, func, text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.core.database import Base


class Review(Base):
    __tablename__ = "reviews"

    __table_args__ = (
        CheckConstraint(
            "grade >= 1 AND grade <= 5",
            name="ck_reviews_grade_range",
        ),
        UniqueConstraint(
            "user_id",
            "product_id",
            name="uq_reviews_user_product",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    comment_date: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                   nullable=False, server_default=func.now())
    grade: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True,
                                            server_default=text("true"), nullable=False)

    user: Mapped["User"] = relationship(back_populates="reviews")
    product: Mapped["Product"] = relationship(back_populates="reviews")
