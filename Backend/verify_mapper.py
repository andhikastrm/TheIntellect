from sqlalchemy.orm import configure_mappers
from app.models.user import User
from app.models.cat import Device

try:
    configure_mappers()
    print("Mapper configuration successful. Relationships are valid.")
except Exception as e:
    print(f"Mapper configuration failed: {e}")
