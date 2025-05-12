import pytest

def author_payload(first_name="John", last_name="Doe", biography="Test bio"):
    return {
        "first_name": first_name,
        "last_name": last_name,
        "biography": biography
    }

# --- CREATE ---
@pytest.mark.asyncio
async def test_create_author(client):
    response = await client.post("/api/authors/", json=author_payload())
    assert response.status_code == 201

@pytest.mark.asyncio
async def test_create_author_missing_fields(client):
    response = await client.post("/api/authors/", json={"first_name": "NoLast"})
    assert response.status_code in (400, 422)

@pytest.mark.asyncio
async def test_create_author_duplicate(client):
    await client.post("/api/authors/", json=author_payload("Dup", "Author"))
    response = await client.post("/api/authors/", json=author_payload("Dup", "Author"))
    assert response.status_code == 201

# --- READ ALL ---
@pytest.mark.asyncio
async def test_read_authors(client):
    await client.post("/api/authors/", json=author_payload("A", "A"))
    await client.post("/api/authors/", json=author_payload("B", "B"))
    response = await client.get("/api/authors/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_read_authors_empty(client):
    response = await client.get("/api/authors/")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_read_authors_pagination(client):
    for i in range(5):
        await client.post("/api/authors/", json=author_payload(f"Pag{i}", f"Pag{i}"))
    response = await client.get("/api/authors/?skip=2&limit=2")
    assert response.status_code == 200
    assert len(response.json()) <= 2

# --- READ BY ID ---
@pytest.mark.asyncio
async def test_read_author_by_id(client):
    resp = await client.post("/api/authors/", json=author_payload("Id", "Test"))
    author_id = resp.json()["id"]
    response = await client.get(f"/api/authors/{author_id}")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_read_author_by_id_not_found(client):
    response = await client.get("/api/authors/99999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_read_author_by_id_invalid(client):
    response = await client.get("/api/authors/invalid")
    assert response.status_code in (404, 422)

# --- UPDATE ---
@pytest.mark.asyncio
async def test_update_author(client):
    resp = await client.post("/api/authors/", json=author_payload("Upd", "Test"))
    author_id = resp.json()["id"]
    response = await client.put(f"/api/authors/{author_id}", json={"first_name": "Updated"})
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_update_author_not_found(client):
    response = await client.put("/api/authors/99999", json={"first_name": "Nope"})
    assert response.status_code == 404



# --- DELETE ---
@pytest.mark.asyncio
async def test_delete_author(client):
    resp = await client.post("/api/authors/", json=author_payload("Del", "Test"))
    author_id = resp.json()["id"]
    response = await client.delete(f"/api/authors/{author_id}")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_delete_author_not_found(client):
    response = await client.delete("/api/authors/99999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_author_with_books(client):
    resp = await client.post("/api/authors/", json=author_payload("Book", "Author"))
    author_id = resp.json()["id"]
    book_payload = {
        "title": "Book by Author",
        "publication_year": 2020,
        "isbn": "ISBN-BOOK-AUTHOR",
        "quantity": 1,
        "author_ids": [author_id],
        "category_ids": []
    }
    await client.post("/api/books/", json=book_payload)
    response = await client.delete(f"/api/authors/{author_id}")
    assert response.status_code == 400