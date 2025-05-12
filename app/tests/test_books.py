import pytest

def book_payload(title="BookTitle", isbn="ISBN-123", quantity=1):
    return {
        "title": title,
        "publication_year": 2020,
        "isbn": isbn,
        "quantity": quantity,
        "author_ids": [],
        "category_ids": []
    }

# --- CREATE ---
@pytest.mark.asyncio
async def test_create_book(client):
    response = await client.post("/api/books/", json=book_payload("BookA", "ISBN-A"))
    assert response.status_code == 201

@pytest.mark.asyncio
async def test_create_book_duplicate_isbn(client):
    await client.post("/api/books/", json=book_payload("BookB", "ISBN-B"))
    response = await client.post("/api/books/", json=book_payload("BookC", "ISBN-B"))
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_create_book_missing_fields(client):
    response = await client.post("/api/books/", json={"title": "NoISBN"})
    assert response.status_code in (400, 422)

# --- READ ALL ---
@pytest.mark.asyncio
async def test_read_books(client):
    await client.post("/api/books/", json=book_payload("BookD", "ISBN-D"))
    await client.post("/api/books/", json=book_payload("BookE", "ISBN-E"))
    response = await client.get("/api/books/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_read_books_empty(client):
    response = await client.get("/api/books/")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_read_books_pagination(client):
    for i in range(5):
        await client.post("/api/books/", json=book_payload(f"Pag{i}", f"ISBN-Pag{i}"))
    response = await client.get("/api/books/?skip=2&limit=2")
    assert response.status_code == 200
    assert len(response.json()) <= 2

# --- READ BY ID ---
@pytest.mark.asyncio
async def test_read_book_by_id(client):
    resp = await client.post("/api/books/", json=book_payload("BookF", "ISBN-F"))
    book_id = resp.json()["id"]
    response = await client.get(f"/api/books/{book_id}")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_read_book_not_found(client):
    response = await client.get("/api/books/99999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_read_book_by_id_invalid(client):
    response = await client.get("/api/books/invalid")
    assert response.status_code in (404, 422)

# --- UPDATE ---
@pytest.mark.asyncio
async def test_update_book(client):
    resp = await client.post("/api/books/", json=book_payload("BookG", "ISBN-G"))
    book_id = resp.json()["id"]
    response = await client.put(f"/api/books/{book_id}", json={"title": "BookG-Updated"})
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_update_book_not_found(client):
    response = await client.put("/api/books/99999", json={"title": "Nope"})
    assert response.status_code == 404

# --- DELETE ---
@pytest.mark.asyncio
async def test_delete_book(client):
    resp = await client.post("/api/books/", json=book_payload("BookH", "ISBN-H"))
    book_id = resp.json()["id"]
    response = await client.delete(f"/api/books/{book_id}")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_delete_book_not_found(client):
    response = await client.delete("/api/books/99999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_book_with_active_borrows(client):
    # Створити книгу
    resp = await client.post("/api/books/", json=book_payload("BookI", "ISBN-I"))
    assert resp.status_code == 201, resp.text
    book_id = resp.json()["id"]
    # Створити користувача
    user_payload = {
        "first_name": "Borrower",
        "last_name": "Test",
        "email": "borrower@booki.com"
    }
    user_resp = await client.post("/api/users/", json=user_payload)
    assert user_resp.status_code == 201, user_resp.text
    user_id = user_resp.json()["id"]
    # Позичити книгу
    borrowed_payload = {
        "user_id": user_id,
        "book_id": book_id
    }
    borrow_resp = await client.post("/api/borrowed_books/", json=borrowed_payload)
    assert borrow_resp.status_code == 201, borrow_resp.text
    # Спроба видалити книгу з активною позикою
    response = await client.delete(f"/api/books/{book_id}")
    assert response.status_code == 400

# --- CHECK AVAILABILITY ---
@pytest.mark.asyncio
async def test_check_book_availability(client):
    resp = await client.post("/api/books/", json=book_payload("BookJ", "ISBN-J", quantity=2))
    book_id = resp.json()["id"]
    response = await client.get(f"/api/books/{book_id}/available")
    assert response.status_code == 200
    data = response.json()
    assert data["book_id"] == book_id
    assert data["total_copies"] == 2
    assert data["available_copies"] == 2
    assert data["is_available"] is True

@pytest.mark.asyncio
async def test_check_book_availability_not_found(client):
    response = await client.get("/api/books/99999/available")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_check_book_availability_after_borrow(client):
    # Створити книгу
    resp = await client.post("/api/books/", json=book_payload("BookK", "ISBN-K", quantity=1))
    book_id = resp.json()["id"]
    # Створити користувача
    user_payload = {
        "first_name": "Borrower",
        "last_name": "Test",
        "email": "borrower@bookk.com"
    }
    user_resp = await client.post("/api/users/", json=user_payload)
    user_id = user_resp.json()["id"]
    # Позичити книгу
    borrowed_payload = {
        "user_id": user_id,
        "book_id": book_id
    }
    await client.post("/api/borrowed_books/", json=borrowed_payload)
    # Перевірити доступність
    response = await client.get(f"/api/books/{book_id}/available")
    assert response.status_code == 200
    data = response.json()
    assert data["available_copies"] == 0
    assert data["is_available"] is False