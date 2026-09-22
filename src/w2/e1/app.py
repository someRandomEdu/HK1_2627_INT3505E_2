from flask import Flask, make_response, request


app = Flask(__name__)
BOOKS = []
__next_id = 1


@app.route("/books")
def get_book():
    return {
        "data": BOOKS,
        "total": len(BOOKS)
    }, 200


@app.route("/books", methods=["POST"])
def create_book():
    global __next_id

    if not request.is_json:
        return "error: Expected JSON!", 415

    p = request.get_json(silent=True) or {}
    t = str(p.get("title", "")).strip()
    a = str(p.get("author", "")).strip()

    if not t or not a:
        return "error: title + author required!", 422

    book = { "id": __next_id, "title": t, "author": a }
    BOOKS.append(book)
    response = make_response(book, 201)
    response.headers["Location"] = f"/books/{__next_id}"
    __next_id += 1
    return response


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
