import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from gateway.database import Base, get_db
from gateway.main import app
from gateway.middleware.auth import set_session_factory

# Single test engine shared across all tests
TEST_DB = "sqlite:///./test_shared.db"
engine = create_engine(TEST_DB, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Apply overrides once globally
app.dependency_overrides[get_db] = override_get_db
set_session_factory(TestingSessionLocal)  # auth middleware uses this for API key lookup

@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def get_test_session():
    return TestingSessionLocal()
