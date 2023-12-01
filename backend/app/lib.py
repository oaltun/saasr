import json
from typing import Optional
from sqlalchemy.orm import Session
from app.core.error import error_detail
from fastapi import Response, status,  Depends, APIRouter, HTTPException
from sqlalchemy.ext.declarative import DeclarativeMeta


def db_create(db: Session, model, schema):
    new_item = model(**schema.dict())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


def db_get(db: Session, model, id, model_name: Optional[str] = None):

    item = db.query(model).filter(model.id == id).first()
    if item == None:
        name = model_name or "Item"
        print("(d6ef9986)")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_detail("DB_ITEM_DOES_NOT_EXIST"),
        )
    return item


def db_get_item_or_error(id, model, model_name, db: Session):

    return db_get(db, model, id, model_name)


class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # an SQLAlchemy class
            fields = {}
            for field in [
                x
                for x in dir(obj)
                if not x.startswith("_") and x != "metadata" and x != "registry"
            ]:
                data = obj.__getattribute__(field)
                try:
                    json.dumps(
                        data
                    )  # this will fail on non-encodable values, like other classes
                    fields[field] = data
                except TypeError:
                    fields[field] = str(data)

            # a json-encodable dict
            return fields

        return json.JSONEncoder.default(self, obj)


def json_orm(obj):
    json.dumps(obj, cls=AlchemyEncoder, check_circular=False)


def print_orm(obj):
    print(json_orm(obj))
