import uuid

from sqlalchemy.orm import Session

from services.identity.crypto import hash_password
from services.identity.models import (
    ConstituencyDB,
    CountryDB,
    DistrictDB,
    PermissionDB,
    RoleDB,
    RolePermissionDB,
    StateDB,
    UserDB,
)

# Static role permissions configuration for bootstrapping
BOOTSTRAP_ROLES = [
    {"name": "Citizen", "parent": None},
    {"name": "Field Engineer", "parent": "Citizen"},
    {"name": "Officer", "parent": "Field Engineer"},
    {"name": "MLA", "parent": "Officer"},
    {"name": "MP", "parent": "MLA"},
    {"name": "Platform Administrator", "parent": "MP"},
    {"name": "System Administrator", "parent": "Platform Administrator"},
]

BOOTSTRAP_PERMISSIONS = {
    "Citizen": [
        "issues:create",
        "issues:read",
        "spatial:read",
        "timeline:read",
    ],
    "Field Engineer": [],
    "Officer": [
        "issues:list_pending",
        "recommendations:read",
        "recommendations:write",
        "planning:read",
        "planning:write",
        "brief:read",
        "incidents:read",
        "incidents:write",
        "constituency:read",
    ],
    "MLA": [],
    "MP": [],
    "Platform Administrator": [],
    "System Administrator": [
        "audit:read",
        "audit:write",
        "system:admin",
    ],
}


def seed_database(db: Session) -> None:
    """Seeds the database with standard roles, permissions, geographic entities, and default admin."""
    # 1. Seed Roles and Permissions
    # Track created roles by name
    role_map = {}

    # Create permissions
    permission_map = {}
    all_perm_names = set()
    for perms in BOOTSTRAP_PERMISSIONS.values():
        for p in perms:
            all_perm_names.add(p)

    for p_name in all_perm_names:
        existing_p = db.query(PermissionDB).filter(PermissionDB.name == p_name).first()
        if not existing_p:
            perm = PermissionDB(
                id=str(uuid.uuid4()), name=p_name, description=f"Permission to {p_name}"
            )
            db.add(perm)
            permission_map[p_name] = perm
        else:
            permission_map[p_name] = existing_p

    db.commit()

    # Create Roles in hierarchical order
    for role_info in BOOTSTRAP_ROLES:
        role_name = role_info["name"]
        parent_name = role_info["parent"]

        parent_id = role_map[parent_name].id if parent_name else None

        existing_r = db.query(RoleDB).filter(RoleDB.name == role_name).first()
        if not existing_r:
            role = RoleDB(
                id=str(uuid.uuid4()),
                name=role_name,
                description=f"{role_name} Role",
                parent_role_id=parent_id,
            )
            db.add(role)
            db.commit()
            db.refresh(role)
            role_map[role_name] = role
        else:
            # Update parent relation if needed
            if parent_id and not existing_r.parent_role_id:
                existing_r.parent_role_id = parent_id
                db.commit()
            role_map[role_name] = existing_r

    # Create Role-Permission mappings
    for role_name, perms in BOOTSTRAP_PERMISSIONS.items():
        role = role_map[role_name]
        for p_name in perms:
            perm = permission_map[p_name]
            # Check if association already exists
            exists = (
                db.query(RolePermissionDB)
                .filter(
                    RolePermissionDB.role_id == role.id,
                    RolePermissionDB.permission_id == perm.id,
                )
                .first()
            )
            if not exists:
                association = RolePermissionDB(role_id=role.id, permission_id=perm.id)
                db.add(association)
    db.commit()

    # 2. Seed Geography (Country, State, District, Constituency)
    # Country
    country = db.query(CountryDB).filter(CountryDB.name == "India").first()
    if not country:
        country = CountryDB(id=str(uuid.uuid4()), name="India")
        db.add(country)
        db.commit()
        db.refresh(country)

    # State
    state = db.query(StateDB).filter(StateDB.name == "Uttar Pradesh").first()
    if not state:
        state = StateDB(
            id=str(uuid.uuid4()), name="Uttar Pradesh", country_id=country.id
        )
        db.add(state)
        db.commit()
        db.refresh(state)

    # District
    district = db.query(DistrictDB).filter(DistrictDB.name == "Auraiya").first()
    if not district:
        district = DistrictDB(id=str(uuid.uuid4()), name="Auraiya", state_id=state.id)
        db.add(district)
        db.commit()
        db.refresh(district)

    # Constituency
    constituency = (
        db.query(ConstituencyDB).filter(ConstituencyDB.name == "Dibiyapur").first()
    )
    if not constituency:
        constituency = ConstituencyDB(
            id=str(uuid.uuid4()),
            name="Dibiyapur",
            district_id=district.id,
            geojson_boundary=None,
            status="ACTIVE",
        )
        db.add(constituency)
        db.commit()
        db.refresh(constituency)

    # 3. Seed System Administrator
    admin = db.query(UserDB).filter(UserDB.email == "admin@helix.gov").first()
    if not admin:
        admin = UserDB(
            id="admin-id-123",
            email="admin@helix.gov",
            name="System Admin",
            hashed_password=hash_password("adminpass"),
            role="System Administrator",
            status="ACTIVE",
            is_verified=True,
            constituency_id=constituency.id,
        )
        db.add(admin)
        db.commit()
