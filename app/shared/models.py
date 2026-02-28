from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from app.shared.utils import utcnow


class TimestampMixin:
    @declared_attr
    def created_at(cls) -> Mapped[datetime]:  # noqa: N805
        return mapped_column(sa.DateTime, default=utcnow, nullable=False)

    @declared_attr
    def updated_at(cls) -> Mapped[datetime]:  # noqa: N805
        return mapped_column(
            sa.DateTime, default=utcnow, onupdate=utcnow, nullable=False
        )
