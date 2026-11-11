"""LAB 1 — add your five tests here. Do not delete the smoke tests.

A. GET /books, empty database -> HTTP 200 and []
B. GET /books/9999 -> HTTP 404, JSON code == NOT_FOUND
C. POST /books with only author -> HTTP 400, errors contains title
D. POST valid book, DELETE it, GET same id -> HTTP 404
BONUS. Validate a Book response using JSON Schema; add an unknown
       field to a *copy* of the response and assert ValidationError.

Useful imports:
    from jsonschema import validate, ValidationError
    import pytest
    from tools import get_book_schema

Do not depend on test execution order. Fixtures: client, app, sample_book.
"""

def test_get_books(client):
    response = client.get("/books")
    assert response.status == 200
    assert response.get_json() == []


def test_get_book(client):
    response = client.get("/books/9999")
    assert response.status == 404
    assert response.get_json()["code"] == "NOT_FOUND"


def test_post_book_invalid(client):
    response = client.post("/books", json={ "title": "crashMe" })
    assert response.status == 400


def test_post_book_valid(client):
    response = client.post("/books", json={ "title": "test", "author": "coder", "year": 2026, "isbn": "0000000000000" })
    assert response.status == 201
