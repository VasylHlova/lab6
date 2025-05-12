import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlmodel import SQLModel, create_engine, Session, inspect
from app.main import app
from app.db.database import get_session

DATABASE_TEST_URL = os.getenv("DATABASE_TEST_URL")

def create_test_db_and_tables():
    engine = create_engine(DATABASE_TEST_URL)
    try:
        # Перевірка підключення
        with engine.connect() as conn:
            print("Test database connection successful")

        # Логування моделей
        print("Registered models:", SQLModel.metadata.tables.keys())

        # Створення таблиць
        print("Creating test database tables...")
        SQLModel.metadata.drop_all(engine)
        SQLModel.metadata.create_all(engine)
        print("Test database tables created successfully")

        # Перевірка таблиць
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        print("Existing tables:", existing_tables)

        # Можна додати перевірку очікуваних таблиць
        expected_tables = ["book", "author", "book_author_link"]
        for table in expected_tables:
            if table not in existing_tables:
                print(f"Table '{table}' was not created")
            else:
                print(f"Table '{table}' exists")
    except Exception as e:
        print("Error creating test tables:", str(e))
        raise

@pytest.fixture(scope="session")
def engine():
    create_test_db_and_tables()
    engine = create_engine(DATABASE_TEST_URL)
    yield engine
    engine.dispose()

@pytest.fixture
def session(engine):
    with Session(engine) as session:
        yield session

@pytest_asyncio.fixture
async def client(session):
    app.dependency_overrides[get_session] = lambda: session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()