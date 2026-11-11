from dataclasses import dataclass
from sqlite3 import IntegrityError
from typing import Any
import time
from datetime import datetime

from sqlalchemy import select, func
from flask import Blueprint, Flask, jsonify, make_response, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Integer, Boolean, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from marshmallow import Schema, fields, validate
from werkzeug.exceptions import HTTPException


class Base(DeclarativeBase):
    pass


app = Flask(__name__)
db = SQLAlchemy(model_class=Base)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
db.init_app(app)


@dataclass
class Product(db.Model):
    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, default=0)
    archived: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "stock": self.stock,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ProductInSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    price = fields.Int(load_default=0, validate=validate.Range(min=0))
    stock = fields.Int(load_default=0, validate=validate.Range(min=0))
    description = fields.Str(load_default="")


class ProductOutSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    description = fields.Str(allow_none=True)
    price = fields.Int()
    stock = fields.Int()


class ProductPatchSchema(Schema):
    name = fields.Str()
    price_cents = fields.Int(validate=validate.Range(min=0))


class ReserveInSchema(Schema):
    qty = fields.Int(required=True, validate=validate.Range(min=1))


products_bp = Blueprint("products", __name__, url_prefix="/api/v1/products")
product_in_schema = ProductInSchema()
product_out_schema = ProductOutSchema()
products_out_schema = ProductOutSchema(many=True)
product_patch_schema = ProductPatchSchema()


@products_bp.get("")
def get_products():
    rows = db.session.execute(db.select(Product)).scalars().all()
    return jsonify(products_out_schema.dump(rows)), 200


@products_bp.post("")
def create_product():
    data = request.get_json(silent=True) or {}
    e = product_in_schema.validate(data)

    if e:
        return jsonify({ "errors": e }, 422)

    body: Any = product_in_schema.load(data)
    p = Product(**body)
    db.session.add(p)
    db.session.commit()
    return jsonify(product_out_schema.dump(p)), 201


@products_bp.get("/<int:id>")
def get_product(id: int):
    p = db.get_or_404(Product, id)
    return jsonify(products_out_schema.dump(p)), 200


@products_bp.patch("/<int:id>")
def patch_product(id: int):
    p = db.get_or_404(Product, id)
    data = request.get_json(silent=True) or {}
    errors = product_in_schema.validate(data)

    if errors:
        return jsonify({ "errors": errors }), 422

    body: Any = product_in_schema.load(data, partial=True)

    for k, v in body.items():
        setattr(p, k, v)

    db.session.commit()
    return jsonify(), 200


@products_bp.delete("/<int:id>")
def delete_product(id):
    p = db.get_or_404(Product, id)
    db.session.delete(p)
    db.session.commit()
    return "", 204


@app.get("/health")
def server_health():
    return "Ok", 200


@app.get("/ready")
def is_server_ready():
    try:
        db.session.execute(db.select(Product)).scalar_one()
        return jsonify({"status" : "Ready"}), 200
    except Exception as e:
        return jsonify({
            "status": "Not ready",
            "errors": [repr(e)]
        }), 503

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        db.session.commit()            

    app.run(host="127.0.0.1", port=5000, debug=True)
