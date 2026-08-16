from app.db import Base, engine
from app.models import Patient, MedicalRecord


def init_db():
    Base.metadata.create_all(
        bind=engine
    )


if __name__ == "__main__":
    init_db()
    print("DATABASE INITIALIZED")
