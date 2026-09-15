from typing import Any

from flask import Flask, jsonify, request
from uuid import uuid4


app = Flask(__name__)
BOOKS = []


def find_by_id(id: Any):
    for b in BOOKS:
        if b["id"] == id:
            return b

    return None


@app.route("/books/<book_id>", methods=["GET"])
def get_book(book_id: str):
    book = find_by_id(book_id)

    if book is None:
        return jsonify({ "error": "not found" }), 404

    return jsonify({ "id": book_id }), 200


@app.route("/items/<int:item_id>")
def get_item(item_id: int):
    return jsonify({ "id": item_id }), 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
