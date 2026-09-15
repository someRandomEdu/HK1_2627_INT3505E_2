from flask import Flask, jsonify, request
from uuid import uuid4

app = Flask(__name__)
STUDENTS = []
BOOKS = [{ "t": "app" }, { "t": "wa" }, { "t": "" }, { "t": "not" }]
ORDERS = {}

@app.route("/orders/<id>", methods=["DELETE"])
def delete_order(id: str):
    order = ORDERS.get(id)

    if order is None:
        return { "error": "not found" }, 404

    if order["status"] in ("shipped", "delivered"):
        return { "error": "cannot delete" }, 409

    ORDERS.pop(id)
    return "", 204


@app.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id: int):
    return jsonify({ "id": book_id }), 200


@app.route("/books", methods=["GET"])
def list_book():
    # limit = int(request.args.get("limit", 20))
    # offset = int(request.args.get("offset", 0))
    q = request.args.get("q", "").strip().lower()
    items = [b for b in BOOKS if q in b["t"].lower()]
    return jsonify({ "items": items }), 200


@app.route("/students", methods=["POST"])
def create_student():
    body = request.get_json(silent=True) or {}
    name = body.get("name")

    if not name:
        return jsonify({ "error": "name là bắt buộc" }), 400

    student = {
        "id": str(uuid4()),
        "name": name,
        "gpa": body.get("gpa", 0.0)
    }

    STUDENTS.append(student)
    return jsonify(student), 201


@app.route("/health", methods=["GET"])
def health():
    return jsonify({ "status": "ok" }), 200


@app.route("/")
def index():
    return { "message": "Hello, API!" }


@app.route("/echo", methods=["POST"])
def echo():
    data = request.get_json(silent=True) or {}
    return jsonify({ "you_sent": data }), 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
