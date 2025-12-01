from app.models.user import User
from app.models.cat import Device, TipePerangkat
from app.database.db import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Create an in-memory SQLite database for testing
engine = create_engine('sqlite:///:memory:')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def test_relationship():
    try:
        # Create a user
        user = User(email="test@example.com", nama="Test User")
        session.add(user)
        session.commit()

        # Create a device linked to the user
        device = Device(
            nama_perangkat="Test Device",
            serial_number="12345",
            tipe=TipePerangkat.GPS,
            user_id=user.id
        )
        session.add(device)
        session.commit()

        # Verify relationship from User side
        assert len(user.devices) == 1
        assert user.devices[0].serial_number == "12345"

        # Verify relationship from Device side
        assert device.user.email == "test@example.com"

        print("Verification Successful: User-Device relationship is working correctly.")
    except Exception as e:
        print(f"Verification Failed: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    test_relationship()
