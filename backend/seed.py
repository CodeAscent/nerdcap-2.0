"""
Database Seeder
Populates the database with realistic AP land parcels, developers, and test users.
Run: python seed.py
"""
import sys
import os
import uuid
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, Base, engine
from app.models.models import LandParcel, Developer, User, UserRole
from app.auth import hash_password

# Ensure tables exist
Base.metadata.create_all(bind=engine)

db = SessionLocal()

print("🌱 Seeding database...")

# ---------------------------------------------------------------------------
# Test Users
# ---------------------------------------------------------------------------
test_users = [
    {"email": "admin@nredcap.gov.in", "password": "Admin@123", "full_name": "Admin User", "role": UserRole.admin, "department": "NREDCAP", "district": None},
    {"email": "officer@nredcap.gov.in", "password": "Officer@123", "full_name": "Sri K. Venkatesh", "role": UserRole.officer, "department": "NREDCAP District Office", "district": "Kurnool"},
    {"email": "developer@solar.com", "password": "Dev@123456", "full_name": "Sri Ravi Kumar", "role": UserRole.developer, "department": None, "district": None},
]

for u in test_users:
    existing = db.query(User).filter(User.email == u["email"]).first()
    if not existing:
        user = User(
            id=uuid.uuid4(),
            email=u["email"],
            hashed_password=hash_password(u["password"]),
            full_name=u["full_name"],
            role=u["role"],
            department=u.get("department"),
            district=u.get("district"),
            is_active=True,
        )
        db.add(user)
print(f"  ✅ Created {len(test_users)} test users")

# ---------------------------------------------------------------------------
# Developers
# ---------------------------------------------------------------------------
developers_data = [
    {"name": "Sri Ravi Kumar", "company": "SunPower India Pvt Ltd", "email": "ravi@sunpower.in", "trust_score": 78.5, "state_registration": "AP-2019-RE-0042"},
    {"name": "Smt. Priya Venkat", "company": "WindHarvest Technologies", "email": "priya@windharvest.in", "trust_score": 85.2, "state_registration": "AP-2020-RE-0117"},
    {"name": "M/s Greenfield Energy", "company": "Greenfield Energy Consortium", "email": "info@greenfield.in", "trust_score": 62.0, "state_registration": "AP-2018-RE-0089"},
    {"name": "Sri Rajesh Sharma", "company": "SolarMax Andhra", "email": "rajesh@solarmax.in", "trust_score": 71.3, "state_registration": "AP-2021-RE-0203"},
    {"name": "AP Renewables Pvt Ltd", "company": "AP Renewables Pvt Ltd", "email": "contact@aprenewables.in", "trust_score": 80.0, "state_registration": "AP-2017-RE-0021"},
]

developer_ids = []
for d in developers_data:
    existing = db.query(Developer).filter(Developer.email == d["email"]).first()
    if not existing:
        dev = Developer(
            id=uuid.uuid4(),
            name=d["name"],
            company=d["company"],
            email=d["email"],
            trust_score=d["trust_score"],
            state_registration=d["state_registration"],
            track_record_json={"completed_projects": 3, "total_mw": 250},
        )
        db.add(dev)
        developer_ids.append(dev.id)
    else:
        developer_ids.append(existing.id)
print(f"  ✅ Created {len(developers_data)} developers")

# ---------------------------------------------------------------------------
# Land Parcels (realistic AP coordinates)
# Kurnool, Anantapur, Kadapa districts
# ---------------------------------------------------------------------------
parcels_data = [
    # Kurnool
    {"name": "Nandyal Barren Land Block A", "district": "Kurnool", "mandal": "Nandyal", "area_ha": 320.5,
     "coords": [[78.47, 15.48], [78.52, 15.48], [78.52, 15.45], [78.47, 15.45], [78.47, 15.48]],
     "ownership": "government", "land_use": "barren", "elevation": 345.0, "slope": 2.1},
    {"name": "Allagadda Wind Corridor Plot", "district": "Kurnool", "mandal": "Allagadda", "area_ha": 480.0,
     "coords": [[78.91, 15.13], [78.96, 15.13], [78.96, 15.09], [78.91, 15.09], [78.91, 15.13]],
     "ownership": "pattadar", "land_use": "waste land", "elevation": 420.0, "slope": 3.5},
    {"name": "Kurnool District Solar Zone 1", "district": "Kurnool", "mandal": "Kurnool", "area_ha": 210.0,
     "coords": [[78.03, 15.82], [78.08, 15.82], [78.08, 15.79], [78.03, 15.79], [78.03, 15.82]],
     "ownership": "government", "land_use": "barren", "elevation": 280.0, "slope": 1.2},
    # Anantapur
    {"name": "Dharmavaram Agricultural Transition Zone", "district": "Anantapur", "mandal": "Dharmavaram", "area_ha": 550.0,
     "coords": [[77.72, 14.42], [77.77, 14.42], [77.77, 14.38], [77.72, 14.38], [77.72, 14.42]],
     "ownership": "pattadar", "land_use": "agricultural", "elevation": 375.0, "slope": 1.8},
    {"name": "Hindupur Wind Farm Extension", "district": "Anantapur", "mandal": "Hindupur", "area_ha": 680.0,
     "coords": [[77.48, 13.83], [77.54, 13.83], [77.54, 13.79], [77.48, 13.79], [77.48, 13.83]],
     "ownership": "government", "land_use": "waste land", "elevation": 680.0, "slope": 4.2},
    {"name": "Anantapur Solar Park Block B", "district": "Anantapur", "mandal": "Anantapur", "area_ha": 390.0,
     "coords": [[77.59, 14.69], [77.64, 14.69], [77.64, 14.65], [77.59, 14.65], [77.59, 14.69]],
     "ownership": "government", "land_use": "barren", "elevation": 345.0, "slope": 0.9},
    # Kadapa
    {"name": "Mydukur Barren Plateau", "district": "Kadapa", "mandal": "Mydukur", "area_ha": 295.0,
     "coords": [[79.01, 14.72], [79.06, 14.72], [79.06, 14.68], [79.01, 14.68], [79.01, 14.72]],
     "ownership": "government", "land_use": "barren", "elevation": 310.0, "slope": 2.8},
    {"name": "Proddatur Solar Zone South", "district": "Kadapa", "mandal": "Proddatur", "area_ha": 185.0,
     "coords": [[78.55, 14.75], [78.60, 14.75], [78.60, 14.72], [78.55, 14.72], [78.55, 14.75]],
     "ownership": "pattadar", "land_use": "waste land", "elevation": 295.0, "slope": 1.5},
    {"name": "Rajampet Wind Potential Site", "district": "Kadapa", "mandal": "Rajampet", "area_ha": 420.0,
     "coords": [[79.16, 14.20], [79.21, 14.20], [79.21, 14.16], [79.16, 14.16], [79.16, 14.20]],
     "ownership": "government", "land_use": "barren", "elevation": 410.0, "slope": 3.8},
    {"name": "Kadapa District Mixed Zone", "district": "Kadapa", "mandal": "Kadapa", "area_ha": 500.0,
     "coords": [[78.82, 14.47], [78.87, 14.47], [78.87, 14.43], [78.82, 14.43], [78.82, 14.47]],
     "ownership": "government", "land_use": "waste land", "elevation": 325.0, "slope": 2.0},
]

for p in parcels_data:
    coords = p["coords"]
    wkt = f"SRID=4326;POLYGON(({', '.join(f'{c[0]} {c[1]}' for c in coords)}))"
    existing = db.query(LandParcel).filter(LandParcel.name == p["name"]).first()
    if not existing:
        parcel = LandParcel(
            id=uuid.uuid4(),
            name=p["name"],
            district=p["district"],
            mandal=p["mandal"],
            area_ha=p["area_ha"],
            geometry=wkt,
            ownership_type=p["ownership"],
            land_use_type=p["land_use"],
            elevation_m=p.get("elevation"),
            slope_degrees=p.get("slope"),
        )
        db.add(parcel)
print(f"  ✅ Created {len(parcels_data)} land parcels across Kurnool, Anantapur, Kadapa")

db.commit()
db.close()

print("\n✅ Seeding complete!")
print("\n📋 Test Credentials:")
print("  Admin   : admin@nredcap.gov.in / Admin@123")
print("  Officer : officer@nredcap.gov.in / Officer@123")
print("  Developer: developer@solar.com / Dev@123456")
