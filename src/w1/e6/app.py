from flask import Flask, jsonify, request


app = Flask(__name__)
__next = 1


BOOKS = [{
    "id": 1,
    "title": "Clean Code",
    "author": "R. Martin",
    "year": 1900
}]


def find(bid: int):
    return next((b for b in BOOKS if b["id"] == bid), None)


@app.route("/books", methods=["GET"])
def list_books():
    n = int(request.args.get("limit", 100))
    books = BOOKS[:n].sort(key=lambda v: v["author"])
    return jsonify(books), 200


@app.route("/books/<int:bid>", methods=["GET"])
def get_book(bid: int):
    book = find(bid)

    if not book:
        return { "error": "not found" }, 404

    return jsonify(book), 200


@app.route("/books", methods=["POST"])
def create_book():
    body = request.get_json(silent=True) or {}
    t: str | None = body.get("title")
    a: str | None = body.get("author")
    y: int | None = body.get("year")

    if not t or not a:
        return { "error": "need title+author" }, 404

    if not isinstance(y, int) or y < 1900:
        return { "error": "year must be >= 1900" }, 404

    global __next
    book = { "id": __next, "title": t, "author": a, "year" : y }
    __next += 1
    BOOKS.append(book)
    return jsonify(book), 201, {"Location": f"/books/{book['id']}"}


@app.route("/books/<int:bid>", methods=["PUT", "DELETE"])
def modify_book(bid: int):
    book = find(bid)

    if not book:
        return { "error": "not found" }, 404


    if request.method == "PUT":
        book.update(request.get_json(silent=True) or {})
        return jsonify(book), 200

    BOOKS.remove(book)
    return "", 204


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
