import pytest

def category_payload(name="TestCategory", description="Test description"):
    return {
        "name": name,
        "description": description
    }

# --- CREATE ---
@pytest.mark.asyncio
async def test_create_category(client):
    response = await client.post("/api/categories/", json=category_payload())
    assert response.status_code == 201

@pytest.mark.asyncio
async def test_create_category_duplicate_name(client):
    await client.post("/api/categories/", json=category_payload("UniqueName"))
    response = await client.post("/api/categories/", json=category_payload("UniqueName"))
    assert response.status_code in (400, 422)

@pytest.mark.asyncio
async def test_create_category_missing_fields(client):
    response = await client.post("/api/categories/", json={})
    assert response.status_code in (400, 422)

# --- READ ALL ---
@pytest.mark.asyncio
async def test_read_categories(client):
    await client.post("/api/categories/", json=category_payload("CatA"))
    await client.post("/api/categories/", json=category_payload("CatB"))
    response = await client.get("/api/categories/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_read_categories_empty(client):
    response = await client.get("/api/categories/")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_read_categories_pagination(client):
    for i in range(5):
        await client.post("/api/categories/", json=category_payload(f"Pag{i}"))
    response = await client.get("/api/categories/?skip=2&limit=2")
    assert response.status_code == 200
    assert len(response.json()) <= 2

# --- READ BY ID ---
@pytest.mark.asyncio
async def test_read_category_by_id(client):
    resp = await client.post("/api/categories/", json=category_payload("ById"))
    cat_id = resp.json()["id"]
    response = await client.get(f"/api/categories/{cat_id}")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_read_category_not_found(client):
    response = await client.get("/api/categories/99999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_read_category_by_id_invalid(client):
    response = await client.get("/api/categories/invalid")
    assert response.status_code in (404, 422)

# --- READ BY NAME ---
@pytest.mark.asyncio
async def test_read_category_by_name(client):
    await client.post("/api/categories/", json=category_payload("ByName"))
    response = await client.get("/api/categories/name/ByName")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_read_category_by_name_not_found(client):
    response = await client.get("/api/categories/name/NoSuchCategory")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_read_category_by_name_invalid(client):
    response = await client.get("/api/categories/name/")
    assert response.status_code in (404, 422)

# --- UPDATE ---
@pytest.mark.asyncio
async def test_update_category(client):
    resp = await client.post("/api/categories/", json=category_payload("ToUpdate"))
    cat_id = resp.json()["id"]
    response = await client.put(f"/api/categories/{cat_id}", json={"name": "UpdatedName"})
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_update_category_not_found(client):
    response = await client.put("/api/categories/99999", json={"name": "Nope"})
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_category_invalid(client):
    resp = await client.post("/api/categories/", json=category_payload("InvUpdate"))
    cat_id = resp.json()["id"]
    response = await client.put(f"/api/categories/{cat_id}", json={"name": ""})
    assert response.status_code in (400, 422)

# --- DELETE ---
@pytest.mark.asyncio
async def test_delete_category(client):
    resp = await client.post("/api/categories/", json=category_payload("ToDelete"))
    cat_id = resp.json()["id"]
    response = await client.delete(f"/api/categories/{cat_id}")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_delete_category_not_found(client):
    response = await client.delete("/api/categories/99999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_category_with_books(client):
    # Створити категорію
    resp = await client.post("/api/categories/", json=category_payload("WithBook"))
    cat_id = resp.json()["id"]
    # Створити книгу з цією категорією
    book_payload = {
        "title": "Book in Cat",
        "publication_year": 2020,
        "isbn": "ISBN-CAT-BOOK",
        "quantity": 1,
        "author_ids": [],
        "category_ids": [cat_id]
    }
    await client.post("/api/books/", json=book_payload)
    # Спроба видалити категорію з прив'язаною книгою
    response = await client.delete(f"/api/categories/{cat_id}")
    assert response.status_code == 400