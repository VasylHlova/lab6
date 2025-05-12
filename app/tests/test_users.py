import pytest

def user_payload(email="test@example.com"):
    return {
        "first_name": "Test",
        "last_name": "User",
        "email": email
    }

# --- CREATE ---
@pytest.mark.asyncio
async def test_create_user(client):
    response = await client.post("/api/users/", json=user_payload())
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["is_active"] is True

@pytest.mark.asyncio
async def test_create_user_duplicate_email(client):
    await client.post("/api/users/", json=user_payload("dup@mail.com"))
    response = await client.post("/api/users/", json=user_payload("dup@mail.com"))
    assert response.status_code in (400, 422)

@pytest.mark.asyncio
async def test_create_user_missing_fields(client):
    response = await client.post("/api/users/", json={"first_name": "NoLast"})
    assert response.status_code in (400, 422)

# --- READ ALL ---
@pytest.mark.asyncio
async def test_read_users(client):
    await client.post("/api/users/", json=user_payload("a@a.com"))
    await client.post("/api/users/", json=user_payload("b@b.com"))
    response = await client.get("/api/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_read_users_empty(client):
    response = await client.get("/api/users/")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_read_users_pagination(client):
    for i in range(5):
        await client.post("/api/users/", json=user_payload(f"pag{i}@mail.com"))
    response = await client.get("/api/users/?skip=2&limit=2")
    assert response.status_code == 200
    assert len(response.json()) <= 2

# --- READ BY ID ---
@pytest.mark.asyncio
async def test_read_user_by_id(client):
    resp = await client.post("/api/users/", json=user_payload("id@id.com"))
    user_id = resp.json()["id"]
    response = await client.get(f"/api/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["email"] == "id@id.com"

@pytest.mark.asyncio
async def test_read_user_not_found(client):
    response = await client.get("/api/users/99999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_read_user_by_id_invalid(client):
    response = await client.get("/api/users/invalid")
    assert response.status_code in (404, 422)

# --- READ BY EMAIL ---
@pytest.mark.asyncio
async def test_read_user_by_email(client):
    await client.post("/api/users/", json=user_payload("mail@mail.com"))
    response = await client.get("/api/users/email/mail@mail.com")
    assert response.status_code == 200
    assert response.json()["email"] == "mail@mail.com"

@pytest.mark.asyncio
async def test_read_user_by_email_not_found(client):
    response = await client.get("/api/users/email/notfound@mail.com")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_read_user_by_email_invalid(client):
    response = await client.get("/api/users/email/")
    assert response.status_code in (404, 422)

# --- READ ACTIVE ---
@pytest.mark.asyncio
async def test_read_active_users(client):
    await client.post("/api/users/", json=user_payload("active1@mail.com"))
    await client.post("/api/users/", json=user_payload("active2@mail.com"))
    response = await client.get("/api/users/active")
    assert response.status_code == 200
    assert all(u["is_active"] for u in response.json())

@pytest.mark.asyncio
async def test_read_active_users_empty(client):
    response = await client.get("/api/users/active")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_read_active_users_pagination(client):
    for i in range(5):
        await client.post("/api/users/", json=user_payload(f"activepag{i}@mail.com"))
    response = await client.get("/api/users/active?skip=2&limit=2")
    assert response.status_code == 200
    assert len(response.json()) <= 2

# --- UPDATE ---
@pytest.mark.asyncio
async def test_update_user(client):
    resp = await client.post("/api/users/", json=user_payload("upd@upd.com"))
    user_id = resp.json()["id"]
    response = await client.put(f"/api/users/{user_id}", json={"first_name": "Updated"})
    assert response.status_code == 200
    assert response.json()["first_name"] == "Updated"

@pytest.mark.asyncio
async def test_update_user_not_found(client):
    response = await client.put("/api/users/99999", json={"first_name": "Nope"})
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_user_invalid(client):
    resp = await client.post("/api/users/", json=user_payload("inv@inv.com"))
    user_id = resp.json()["id"]
    response = await client.put(f"/api/users/{user_id}", json={"email": ""})
    assert response.status_code in (400, 422)

# --- DELETE ---
@pytest.mark.asyncio
async def test_delete_user(client):
    resp = await client.post("/api/users/", json=user_payload("del@del.com"))
    user_id = resp.json()["id"]
    response = await client.delete(f"/api/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["id"] == user_id

@pytest.mark.asyncio
async def test_delete_user_not_found(client):
    response = await client.delete("/api/users/99999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_user_with_borrowed_books(client):
    # Створити користувача
    resp = await client.post("/api/users/", json=user_payload("borrowed@del.com"))
    user_id = resp.json()["id"]
    # Створити книгу
    book_payload = {
        "title": "Book for User",
        "publication_year": 2020,
        "isbn": "ISBN-USER-BOOK",
        "quantity": 1,
        "author_ids": [],
        "category_ids": []
    }
    book_resp = await client.post("/api/books/", json=book_payload)
    book_id = book_resp.json()["id"]
    # Позичити книгу
    borrowed_payload = {
        "user_id": user_id,
        "book_id": book_id,
        "return_date": "2099-12-31T00:00:00Z"
    }
    await client.post("/api/borrowed_books/", json=borrowed_payload)
    # Спроба видалити користувача з активною позикою
    response = await client.delete(f"/api/users/{user_id}")
    assert response.status_code == 400
    assert "borrowed books" in response.json()["detail"]