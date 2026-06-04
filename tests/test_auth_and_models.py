import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.database import Base, User, ChatSession, Message
from core.auth import hash_password, verify_password, make_session_cookie, _sign, _unsign


# --- In-memory DB fixture ---

@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


# --- Model tests ---

def test_create_user(db):
    user = User(username="alice", hashed_password=hash_password("secret"), is_admin=True)
    db.add(user)
    db.commit()
    assert db.query(User).count() == 1
    assert db.query(User).first().username == "alice"


def test_create_session_and_message(db):
    user = User(username="bob", hashed_password=hash_password("pw"), is_admin=False)
    db.add(user)
    db.flush()

    chat = ChatSession(user_id=user.id, title="Test chat")
    db.add(chat)
    db.flush()

    msg = Message(session_id=chat.id, role="user", content="Hello")
    db.add(msg)
    db.commit()

    assert db.query(ChatSession).count() == 1
    assert db.query(Message).first().content == "Hello"


def test_cascade_delete(db):
    user = User(username="carol", hashed_password=hash_password("pw"), is_admin=False)
    db.add(user)
    db.flush()
    chat = ChatSession(user_id=user.id)
    db.add(chat)
    db.flush()
    db.add(Message(session_id=chat.id, role="user", content="hi"))
    db.commit()

    db.delete(user)
    db.commit()
    assert db.query(ChatSession).count() == 0
    assert db.query(Message).count() == 0


# --- Auth tests ---

def test_password_hash_and_verify():
    h = hash_password("mypassword")
    assert verify_password("mypassword", h)
    assert not verify_password("wrong", h)


def test_cookie_sign_unsign():
    val = "42:1234567890"
    signed = _sign(val)
    assert _unsign(signed) == val


def test_cookie_tamper_detected():
    signed = _sign("42:1234567890")
    tampered = signed[:-4] + "xxxx"
    assert _unsign(tampered) is None


def test_make_session_cookie_contains_user_id():
    cookie = make_session_cookie(99)
    from core.auth import _unsign
    value = _unsign(cookie)
    assert value is not None
    uid, _ = value.split(":", 1)
    assert int(uid) == 99
