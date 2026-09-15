from flask import Flask


app = Flask(__name__)
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


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
