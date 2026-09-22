from flask import Flask, jsonify, make_response, request


app = Flask(__name__)
BOOKS = []


@app.get("/books/<int:bid>")
def fetch(bid: int):
    for b in BOOKS:
        if b["id"] == bid:
            response = make_response(b, 200)
            response.headers["Cache-Control"] = "max-age=60"
            return response

    return "error: not found", 404


@app.put("/books/<int:bid>")
def put(bid: int):
    for b in BOOKS:
        if b["id"] == bid:
            p = request.get_json(silent=True) or {}
            t: str | None = p.get("title")
            a: str | None = p.get("author")

            if not t or not a:
                return "error: need title + author", 422

            b["title"] = t
            b["author"] = a
            response = make_response(b, 200)
            response.headers["Cache-Control"] = "max-age=60"
            return response

    return "error: not found", 404


@app.patch("/books/<int:bid>")
def patch(bid: int):
    for b in BOOKS:
        if b["id"] == bid:
            p = request.get_json(silent=True) or {}
            price = int(p.get("price", 0))

            if price < 0:
                return jsonify(error="price must be positive"), 422

            title: str | None = p.get("title", None)
            b["price"] = price

            if title is not None:
                b["title"] = title

            return b, 200
    
    return jsonify(error="not found"), 404


@app.delete("/books/<int:bid>")
def delete(bid: int):
    for b in BOOKS:
        if b["id"] == bid:
            BOOKS.remove(b)
            return "", 204

    return jsonify(error="not found"), 404


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
