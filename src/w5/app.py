from sqlalchemy import select, func
from flask import Flask, jsonify, make_response, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


app = Flask(__name__)
db = SQLAlchemy(model_class=Base)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
db.init_app(app)


class Book(db.Model):
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(db.String)
    author: Mapped[str] = mapped_column(db.String)

    def __init__(self, id: int | None, title: str, author: str):
        if id is not None:
            self.id = id

        self.title = title
        self.author = author

    def to_json(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author
        }


class Author(db.Model):
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    bio: Mapped[str] = mapped_column(db.String)

    def __init__(self, id: int | None, bio: str):
        if id is not None:
            self.id = id

        self.bio = bio

    def to_json(self):
        return {
            "id": self.id,
            "bio": self.bio
        }


class User(db.Model):
    id: Mapped[int] = mapped_column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(db.String)
    display_name: Mapped[str] = mapped_column(db.String)


@app.get("/")
def list_books():
    strategy = request.args.get("strategy", "offset")
    limit = max(min(int(request.args.get("limit", 0)), 0), 20)
    total = db.session.scalar(select(func.count(Book.id)))

    if strategy == "offset":
        offset = int(request.args.get("offset", 0))
        query = select(Book).offset(offset).order_by(Book.id).limit(limit)
        rows = db.session.scalars(query).all()
        books = [b.to_json() for b in rows]

        return {
            "data": books,

            "pagination": {
                "offset": offset,
                "total": total,
                "limit": limit,
                "count": len(books),
                "has_next": offset + limit < total if total is not None else False
            }
        }, 200
    elif strategy == "cursor":
        id = int(request.args.get("id", 0))
        query = select(Book).where(Book.id > id).order_by(Book.id.asc()).limit(limit)
        rows = db.session.scalars(query).all()
        books = [b.to_json() for b in rows]

        return {
            "data": books,

            "pagination": {
                "id": id,
                "total": total,
                "limit": limit,
                "count": len(books)
            }
        }, 200
    else:
        return {
            "status": 400,
            "title": 'Pagination strategy is not equal to either "offset" or "cursor"!'
        }, 400


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        db.session.add_all([
            Book(None, "Book", "Author"), 
            Book(None, "a", "b"), 
            Book(None, "abwa", "bar"), 
            Book(None, "theory", "practice"), 
            Book(None, "foo", "bar")
        ])

        db.session.commit()

    app.run(host="127.0.0.1", port=5000, debug=True)
