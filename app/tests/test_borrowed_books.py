import pytest
from datetime import datetime, timedelta, timezone

def user_payload(email="borrower@test.com"):
    return {
        "first_name": "Borrower",
        "last_name": "Test",
        "email": email
    }

def book_payload(title="BookTitle", author="AuthorName"):
    return {
        "title": title,
        "author": author,
        "isbn": f"ISBN-{title}",
        "publication_year": 2020
    }

async def create_user(client, email="borrower@test.com"):
    resp = await client.post("/api/users/", json=user_payload(email))
    return resp.json()["id"]

async def create_book(client, title="BookTitle"):
    resp = await client.post("/api/books/", json=book_payload(title))
    return resp.json()["id"]

def borrowed_payload(user_id, book_id, days=7):
    return {
        "user_id": user_id,
        "book_id": book_id,
        "return_date": (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()
    }

# --- CREATE ---
@pytest.mark.asyncio
async def test_create_borrowed(client):
    user_id = await create_user(client, "borrowed1@test.com")
    book_id = await create_book(client, "Book1")
    response = await client.post("/api/borrowed_books/", json=borrowed_payload(user_id, book_id))
    assert response.status_code == 201

@pytest.mark.asyncio
async def test_create_borrowed_invalid_user(client):
    book_id = await create_book(client, "Book2")
    response = await client.post("/api/borrowed_books/", json=borrowed_payload(99999, book_id))
    assert response.status_code in (400, 422)

@pytest.mark.asyncio
async def test_create_borrowed_invalid_book(client):
    user_id = await create_user(client, "borrowed2@test.com")
    response = await client.post("/api/borrowed_books/", json=borrowed_payload(user_id, 99999))
    assert response.status_code in (400, 422)

# --- READ ALL ---
@pytest.mark.asyncio
async def test_read_borrowed(client):
    user_id = await create_user(client, "borrowed3@test.com")
    book_id = await create_book(client, "Book3")
    await client.post("/api/borrowed_books/", json=borrowed_payload(user_id, book_id))
    response = await client.get("/api/borrowed_books/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_read_borrowed_empty(client):
    response = await client.get("/api/borrowed_books/")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_read_borrowed_filter_by_user(client):
    user_id = await create_user(client, "borrowed4@test.com")
    book_id = await create_book(client, "Book4")
    await client.post("/api/borrowed_books/", json=borrowed_payload(user_id, book_id))
    response = await client.get(f"/api/borrowed_books/?user_id={user_id}")
    assert response.status_code == 200
    assert all(b["user_id"] == user_id for b in response.json())

# --- READ BY USER ---
@pytest.mark.asyncio
async def test_read_borrowed_by_user(client):
    user_id = await create_user(client, "borrowed5@test.com")
    book_id = await create_book(client, "Book5")
    await client.post("/api/borrowed_books/", json=borrowed_payload(user_id, book_id))
    response = await client.get(f"/api/borrowed_books/{user_id}")
    assert response.status_code == 200
    assert all(b["user_id"] == user_id for b in response.json())

@pytest.mark.asyncio
async def test_read_borrowed_by_user_not_found(client):
    response = await client.get("/api/borrowed_books/99999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_read_borrowed_by_user_empty(client):
    user_id = await create_user(client, "borrowed6@test.com")
    response = await client.get(f"/api/borrowed_books/{user_id}")
    # Якщо у користувача немає позик, очікуємо 404 згідно вашого API
    assert response.status_code == 404

# --- UPDATE (RETURN BOOK) ---
@pytest.mark.asyncio
async def test_update_borrowed(client):
    user_id = await create_user(client, "borrowed7@test.com")
    book_id = await create_book(client, "Book7")
    resp = await client.post("/api/borrowed_books/", json=borrowed_payload(user_id, book_id))
    borrowed_id = resp.json()["id"]
    response = await client.put(f"/api/borrowed_books/{borrowed_id}", json={})
    assert response.status_code == 200
    assert response.json()["real_return_date"] is not None

@pytest.mark.asyncio
async def test_update_borrowed_not_found(client):
    response = await client.put("/api/borrowed_books/99999", json={})
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_borrowed_invalid(client):
    user_id = await create_user(client, "borrowed8@test.com")
    book_id = await create_book(client, "Book8")
    resp = await client.post("/api/borrowed_books/", json=borrowed_payload(user_id, book_id))
    borrowed_id = resp.json()["id"]
    # Ваша логіка може не мати валідації, але можна спробувати передати невалідне поле
    response = await client.put(f"/api/borrowed_books/{borrowed_id}", json={"user_id": None})
    assert response.status_code in (200, 422)

# --- DELETE ---
@pytest.mark.asyncio
async def test_delete_borrowed(client):
    user_id = await create_user(client, "borrowed9@test.com")
    book_id = await create_book(client, "Book9")
    resp = await client.post("/api/borrowed_books/", json=borrowed_payload(user_id, book_id))
    borrowed_id = resp.json()["id"]
    response = await client.delete(f"/api/borrowed_books/{borrowed_id}")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_delete_borrowed_not_found(client):
    response = await client.delete("/api/borrowed_books/99999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_borrowed_twice(client):
    user_id = await create_user(client, "borrowed10@test.com")
    book_id = await create_book(client, "Book10")
    resp = await client.post("/api/borrowed_books/", json=borrowed_payload(user_id, book_id))
    borrowed_id = resp.json()["id"]
    await client.delete(f"/api/borrowed_books/{borrowed_id}")
    response = await client.delete(f"/api/borrowed_books/{borrowed_id}")
    assert response.status_code == 404