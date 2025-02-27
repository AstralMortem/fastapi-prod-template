import datetime
import uuid
from contextlib import nullcontext

import pytest
from sqlalchemy.orm import Mapped
from sqlalchemy.testing.schema import mapped_column

from core.config import settings
from core.db.session import Model
from unittest.mock import patch
import inspect


def test_model_tablename():
    class TestModel(Model):
        pass

    assert TestModel.__tablename__ == "test_models"


@pytest.mark.parametrize(
    "name,type, exp",
    [
        ("id", int, nullcontext()),
        ("id", uuid.UUID, nullcontext()),
        ("model_id", str, nullcontext()),
        ("id", datetime.datetime, pytest.raises(ValueError)),
    ],
)
def test_model_default_pk(name, type, exp):
    with patch("core.db.session.settings") as mock_settings:
        table = Model.metadata.tables.get("test_models")
        if table is not None:
            Model.registry.metadata.remove(table)
        mock_settings.DEFAULT_PK_FIELD_NAME = name
        mock_settings.DEFAULT_PK_FIELD_TYPE = type

        with exp:

            class TestModel(Model):
                pass

            assert hasattr(TestModel, mock_settings.DEFAULT_PK_FIELD_NAME)
            test = inspect.get_annotations(TestModel)
            print(test)
            assert test[mock_settings.DEFAULT_PK_FIELD_NAME] == Mapped[type]


def test_model_without_pk_flag():
    class ModelWithoutPK(Model):
        __without_default_pk__ = True

        another_id: Mapped[int] = mapped_column(
            primary_key=True
        )  # To handle sqlalchemy error: Mapper could not assemble any primary key columns for mapped table

    assert hasattr(ModelWithoutPK, settings.DEFAULT_PK_FIELD_NAME) is False
