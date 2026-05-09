"""Crée un parent de test si absent. Usage : uv run python -m app.scripts.seed_dev"""

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.parent import Parent

TEST_LOGIN = "admin"
TEST_PASSWORD = "admin"


def main() -> None:
    db = SessionLocal()
    try:
        existing = db.query(Parent).filter(Parent.login == TEST_LOGIN).first()
        if existing:
            print(f"Parent '{TEST_LOGIN}' déjà présent (id={existing.id})")
            return
        parent = Parent(
            login=TEST_LOGIN,
            password_hash=hash_password(password=TEST_PASSWORD),
        )
        db.add(instance=parent)
        db.commit()
        print(f"Parent '{TEST_LOGIN}' créé (id={parent.id})")
    finally:
        db.close()


if __name__ == "__main__":
    main()
