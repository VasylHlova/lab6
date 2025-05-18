import pytest

def author_payload(first_name="John", last_name="Doe", biography="Test bio"):
    return {
        "first_name": first_name,
        "last_name": last_name,
        "biography": biography
    }

def category_payload(name="Fiction", description="Test category"):
    return {
        "name": name,
        "description": description
    }

def user_payload(first_name="User", last_name="Test", email="user@test.com", password="testpass123"):
    return {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "password": password
    }

def book_payload(title="BookTitle", isbn="ISBN-123", quantity=1, author_ids=None, category_ids=None):
    return {
        "title": title,
        "publication_year": 2020,
        "isbn": isbn,
        "quantity": quantity,
        "author_ids": author_ids or [],
        "category_ids": category_ids or []
    }

@pytest.mark.asyncio
async def test_create_book(client):
    author = (await client.post("/api/authors/", json=author_payload())).json()
    category = (await client.post("/api/categories/", json=category_payload())).json()
    response = await client.post("/api/books/", json=book_payload("BookA", "ISBN-A", 1, [author["id"]], [category["id"]]))
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "BookA"
    assert data["isbn"] == "ISBN-A"
    assert "id" in data

@pytest.mark.asyncio
async def test_create_book_duplicate_isbn(client):
    author = (await client.post("/api/authors/", json=author_payload("Dup", "Book"))).json()
    category = (await client.post("/api/categories/", json=category_payload("DupCat"))).json()
    await client.post("/api/books/", json=book_payload("BookB", "ISBN-B", 1, [author["id"]], [category["id"]]))
    response = await client.post("/api/books/", json=book_payload("BookC", "ISBN-B", 1, [author["id"]], [category["id"]]))
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_create_book_missing_fields(client):
    response = await client.post("/api/books/", json={"title": "NoISBN"})
    assert response.status_code in (400, 422)

@pytest.mark.asyncio
async def test_read_books(client):
    author = (await client.post("/api/authors/", json=author_payload("A", "A"))).json()
    category = (await client.post("/api/categories/", json=category_payload("CatA"))).json()
    await client.post("/api/books/", json=book_payload("BookD", "ISBN-D", 1, [author["id"]], [category["id"]]))
    await client.post("/api/books/", json=book_payload("BookE", "ISBN-E", 1, [author["id"]], [category["id"]]))
    response = await client.get("/api/books/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_read_books_empty(client):
    response = await client.get("/api/books/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_read_books_pagination(client):
    author = (await client.post("/api/authors/", json=author_payload("Pag", "Pag"))).json()
    category = (await client.post("/api/categories/", json=category_payload("PagCat"))).json()
    for i in range(5):
        await client.post("/api/books/", json=book_payload(f"Pag{i}", f"ISBN-Pag{i}", 1, [author["id"]], [category["id"]]))
    response = await client.get("/api/books/?skip=2&limit=2")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) <= 2

@pytest.mark.asyncio
async def test_read_book_by_id(client):
    author = (await client.post("/api/authors/", json=author_payload("Id", "Test"))).json()
    category = (await client.post("/api/categories/", json=category_payload("IdCat"))).json()
    resp = await client.post("/api/books/", json=book_payload("BookF", "ISBN-F", 1, [author["id"]], [category["id"]]))
    book_id = resp.json()["id"]
    response = await client.get(f"/api/books/{book_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == book_id

@pytest.mark.asyncio
async def test_read_book_not_found(client):
    response = await client.get("/api/books/99999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_read_book_by_id_invalid(client):
    response = await client.get("/api/books/invalid")
    assert response.status_code in (404, 422)

@pytest.mark.asyncio
async def test_update_book(client):
    author = (await client.post("/api/authors/", json=author_payload("Upd", "Book"))).json()
    category = (await client.post("/api/categories/", json=category_payload("UpdCat"))).json()
    resp = await client.post("/api/books/", json=book_payload("BookG", "ISBN-G", 1, [author["id"]], [category["id"]]))
    book_id = resp.json()["id"]
    response = await client.put(f"/api/books/{book_id}", json={"title": "BookG-Updated"})
    assert response.status_code == 200
    assert response.json()["title"] == "BookG-Updated"

@pytest.mark.asyncio
async def test_update_book_not_found(client):
    response = await client.put("/api/books/99999", json={"title": "Nope"})
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_book(client):
    author = (await client.post("/api/authors/", json=author_payload("Del", "Book"))).json()
    category = (await client.post("/api/categories/", json=category_payload("DelCat"))).json()
    resp = await client.post("/api/books/", json=book_payload("BookH", "ISBN-H", 1, [author["id"]], [category["id"]]))
    book_id = resp.json()["id"]
    response = await client.delete(f"/api/books/{book_id}")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_delete_book_not_found(client):
    response = await client.delete("/api/books/99999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_book_with_active_borrows(client):
    # Створити автора, категорію, книгу
    author_resp = await client.post("/api/authors/", json=author_payload("Borrow", "Book"))
    assert author_resp.status_code == 201, author_resp.text
    author = author_resp.json()
    category_resp = await client.post("/api/categories/", json=category_payload("BorrowCat"))
    assert category_resp.status_code == 201, category_resp.text
    category = category_resp.json()
    resp = await client.post("/api/books/", json=book_payload("BookI", "ISBN-I", 1, [author["id"]], [category["id"]]))
    assert resp.status_code == 201, resp.text
    book_id = resp.json()["id"]
    # Створити користувача
    user_resp = await client.post("/api/users/", json=user_payload("Borrower", "Test", "borrower@booki.com", "testpass123"))
    assert user_resp.status_code == 201, user_resp.text
    user = user_resp.json()
    user_id = user["id"]
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

@pytest.mark.asyncio
async def test_check_book_availability(client):
    author = (await client.post("/api/authors/", json=author_payload("Avail", "Book"))).json()
    category = (await client.post("/api/categories/", json=category_payload("AvailCat"))).json()
    resp = await client.post("/api/books/", json=book_payload("BookJ", "ISBN-J", 2, [author["id"]], [category["id"]]))
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
    author = (await client.post("/api/authors/", json=author_payload("Borrowed", "Book"))).json()
    category = (await client.post("/api/categories/", json=category_payload("BorrowedCat"))).json()
    resp = await client.post("/api/books/", json=book_payload("BookK", "ISBN-K", 1, [author["id"]], [category["id"]]))
    book_id = resp.json()["id"]
    user = (await client.post("/api/users/", json=user_payload("Borrower", "Test", "borrower@bookk.com", "testpass123"))).json()
    user_id = user["id"]
    borrowed_payload = {
        "user_id": user_id,
        "book_id": book_id
    }
    await client.post("/api/borrowed_books/", json=borrowed_payload)
    response = await client.get(f"/api/books/{book_id}/available")
    assert response.status_code == 200
    data = response.json()
    assert data["available_copies"] == 0
    assert data["is_available"] is False