from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from helix_platform.persistence import get_db
from helix_platform.security import hash_password
from services.identity.models import UserDB


def test_citizen_self_registration_and_login(client: TestClient) -> None:
    # 1. Register a new citizen
    payload = {
        "email": "citizen@example.com",
        "name": "Citizen John",
        "password": "securepassword123",
        "phone": "+123456789",
        "bio": "A proud citizen.",
    }
    response = client.post("/identity/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "citizen@example.com"
    assert data["name"] == "Citizen John"
    assert data["role"] == "Citizen"
    assert data["status"] == "ACTIVE"
    assert "id" in data

    # 2. Login as the citizen
    login_payload = {"email": "citizen@example.com", "password": "securepassword123"}
    login_response = client.post("/identity/login", json=login_payload)
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert "access_token" in login_data
    assert login_data["user"]["email"] == "citizen@example.com"

    # 3. Try to register same email again, should fail
    fail_response = client.post("/identity/register", json=payload)
    assert fail_response.status_code == 400


def test_user_profile_endpoints(client: TestClient) -> None:
    # 1. Register and login
    payload = {
        "email": "profile_user@example.com",
        "name": "Jane Doe",
        "password": "mypassword",
    }
    reg_resp = client.post("/identity/register", json=payload)
    user_id = reg_resp.json()["id"]

    login_resp = client.post(
        "/identity/login",
        json={"email": "profile_user@example.com", "password": "mypassword"},
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get profile
    profile_resp = client.get("/identity/profile", headers=headers)
    assert profile_resp.status_code == 200
    assert profile_resp.json()["name"] == "Jane Doe"

    # 3. Put profile
    update_payload = {
        "name": "Jane Updated",
        "phone": "+987654321",
        "bio": "Updated bio text.",
    }
    update_resp = client.put("/identity/profile", json=update_payload, headers=headers)
    assert update_resp.status_code == 200
    assert update_resp.json()["name"] == "Jane Updated"
    assert update_resp.json()["phone"] == "+987654321"
    assert update_resp.json()["bio"] == "Updated bio text."

    # 4. Get profile with X-User-ID header to verify testing path
    profile_header_resp = client.get(
        "/identity/profile", headers={"X-User-ID": user_id}
    )
    assert profile_header_resp.status_code == 200
    assert profile_header_resp.json()["name"] == "Jane Updated"


def test_invitation_and_approval_workflow(client: TestClient) -> None:
    # Set up Admin directly in DB to initiate invitations
    # We will use get_db to get a session
    db_gen = get_db()
    db: Session = next(db_gen)

    admin_user = UserDB(
        id="admin-id-123",
        email="admin@helix.gov",
        name="System Admin",
        hashed_password=hash_password("adminpass"),
        role="ADMINISTRATOR",
        status="ACTIVE",
    )
    # Check if admin already exists from a previous test run
    existing_admin = db.query(UserDB).filter(UserDB.email == "admin@helix.gov").first()
    if not existing_admin:
        db.add(admin_user)
        db.commit()
    else:
        admin_user = existing_admin

    # Get admin token
    admin_login = client.post(
        "/identity/login", json={"email": "admin@helix.gov", "password": "adminpass"}
    )
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Admin invites MLA
    invite_payload = {"email": "mla_candidate@helix.gov", "role": "MLA"}
    invite_resp = client.post(
        "/identity/invitations", json=invite_payload, headers=admin_headers
    )
    assert invite_resp.status_code == 201
    invite_data = invite_resp.json()
    token = invite_data["token"]
    assert invite_data["role"] == "MLA"
    assert invite_data["status"] == "PENDING"

    # 2. MLA candidate accepts invitation
    accept_payload = {
        "token": token,
        "password": "mlapassword",
        "name": "MLA Candidate",
        "phone": "+111222333",
    }
    accept_resp = client.post("/identity/invitations/accept", json=accept_payload)
    assert accept_resp.status_code == 200
    mla_user_data = accept_resp.json()
    mla_user_id = mla_user_data["id"]
    assert mla_user_data["role"] == "MLA"
    assert mla_user_data["status"] == "PENDING_APPROVAL"

    # 3. MLA tries to login but should fail because status is not ACTIVE
    mla_login_fail = client.post(
        "/identity/login",
        json={"email": "mla_candidate@helix.gov", "password": "mlapassword"},
    )
    assert mla_login_fail.status_code == 403

    # 4. MLA tries to invite Officer before being approved, should fail
    mla_headers_unapproved = {"X-User-ID": mla_user_id}
    unauthorized_invite = client.post(
        "/identity/invitations",
        json={"email": "officer@helix.gov", "role": "OFFICER"},
        headers=mla_headers_unapproved,
    )
    assert unauthorized_invite.status_code == 403
    # Let's check get_current_user in routes.py:
    # "if x_user_id: user = db.query(UserDB).filter(UserDB.id == x_user_id).first(); return user"
    # Ah! X-User-ID bypasses status check? No, let's keep status check for X-User-ID too or check get_current_user:
    # "if user.status != "ACTIVE": raise HTTPException(status_code=403, ...)"
    # Wait, in routes.py we wrote:
    # "if x_user_id: user = db.query(UserDB).filter(UserDB.id == x_user_id).first() if user: return user"
    # Oh! In our routes.py, if x_user_id is passed, it returns the user IMMEDIATELY without checking if they are ACTIVE!
    # But wait, that's actually fine for testing if we want to bypass ACTIVE checks. But let's check: if we want to test status checks, we should use Bearer token, which validates the status.
    # Wait! Let's check: if we want MLA login to fail because of status, that's exactly what `test_identity.py` checks.
    # Let's verify how we want to handle unapproved MLA trying to do something. If we use Bearer token for MLA:
    # To get Bearer token for MLA, MLA must first login. But login fails with 403 because they are not ACTIVE! So they cannot get a Bearer token.
    # What if they try to use X-User-ID? X-User-ID in get_current_user returns the user directly.
    # Let's check if we want get_current_user to check ACTIVE status for X-User-ID as well.
    # Yes, it's safer if get_current_user always checks user.status == "ACTIVE" regardless of header (unless we specifically want to bypass it in testing, but we can bypass it by setting the status in DB directly).
    # Let's adjust get_current_user in routes.py to check for ACTIVE status for both! Wait, in routes.py we wrote:
    # `if x_user_id: user = db.query(UserDB).filter(UserDB.id == x_user_id).first() if user: return user`
    # Let's change routes.py to verify status for X-User-ID too, OR we can just let it return the user and only enforce ACTIVE status for Bearer token. Actually, enforcing status for both is cleaner and more secure:
    # `if x_user_id: user = ...; if user: if user.status != "ACTIVE": raise HTTPException(status_code=403); return user`
    # Let's make sure our routes.py does check status for X-User-ID too, except maybe during profile retrieval/update? No, even if they are inactive they shouldn't be allowed to use the system. Wait, if they are PENDING_APPROVAL, they shouldn't be allowed to do anything.

    # 5. System Admin approves the MLA
    approve_resp = client.post(
        f"/identity/users/{mla_user_id}/approve", headers=admin_headers
    )
    assert approve_resp.status_code == 200
    assert approve_resp.json()["status"] == "ACTIVE"

    # 6. MLA logins successfully now
    mla_login_success = client.post(
        "/identity/login",
        json={"email": "mla_candidate@helix.gov", "password": "mlapassword"},
    )
    assert mla_login_success.status_code == 200
    mla_token = mla_login_success.json()["access_token"]
    mla_headers = {"Authorization": f"Bearer {mla_token}"}

    # 7. MLA invites Officer
    officer_invite_payload = {
        "email": "officer_candidate@helix.gov",
        "role": "OFFICER",
        "department_id": "dept-123",
    }
    off_invite_resp = client.post(
        "/identity/invitations", json=officer_invite_payload, headers=mla_headers
    )
    assert off_invite_resp.status_code == 201
    off_invite_data = off_invite_resp.json()
    off_token = off_invite_data["token"]
    assert off_invite_data["role"] == "Officer"

    # 8. Officer accepts invitation
    off_accept_resp = client.post(
        "/identity/invitations/accept",
        json={
            "token": off_token,
            "password": "officerpassword",
            "name": "Officer Smith",
        },
    )
    assert off_accept_resp.status_code == 200
    off_user_id = off_accept_resp.json()["id"]
    assert off_accept_resp.json()["status"] == "PENDING_APPROVAL"

    # 9. MLA approves Officer
    off_approve_resp = client.post(
        f"/identity/users/{off_user_id}/approve", headers=mla_headers
    )
    assert off_approve_resp.status_code == 200
    assert off_approve_resp.json()["status"] == "ACTIVE"
    assert off_approve_resp.json()["department_id"] == "dept-123"

    # 10. List users
    users_resp = client.get("/identity/users", headers=admin_headers)
    assert users_resp.status_code == 200
    users_list = users_resp.json()
    assert len(users_list) >= 3  # Admin, MLA, Officer
