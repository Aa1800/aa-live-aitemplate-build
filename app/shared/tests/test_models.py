import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.shared.models import TimestampMixin


class SampleModel(TimestampMixin, Base):
    __tablename__ = "sample_model"
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)


def test_timestamp_mixin_adds_created_at_column() -> None:
    cols = {c.key for c in sa.inspect(SampleModel).mapper.columns}
    assert "created_at" in cols


def test_timestamp_mixin_adds_updated_at_column() -> None:
    cols = {c.key for c in sa.inspect(SampleModel).mapper.columns}
    assert "updated_at" in cols


def test_timestamp_columns_are_datetime_type() -> None:
    mapper = sa.inspect(SampleModel).mapper
    assert isinstance(mapper.columns["created_at"].type, sa.DateTime)
    assert isinstance(mapper.columns["updated_at"].type, sa.DateTime)
