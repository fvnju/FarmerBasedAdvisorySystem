"""Seed data: modules, privileges, system roles, and the first admin user. Safe to run again."""

import secrets  # Import secrets to make a random password

from sqlalchemy.orm import Session  # Import Session type

from app.core.config import settings  # Import settings to read the seed password
from app.core.security import hash_password  # Import the password hash function
from app.model import Module, Privilege, Role, User  # Import RBAC models

SEED_ADMIN_USERNAME = "johndoe"  # Name of the first admin

MODULES = {  # Module name -> (description, actions). The services check "<module>.<action>".
    "users": ("User accounts", ["read", "create", "update", "delete", "assign_roles"]),
    "rbac": ("Roles, modules, and privileges", ["read", "manage"]),
    "sessions": ("Login sessions and one-time tokens", ["read", "revoke"]),
    "consents": ("Consent records", ["read", "create"]),
    "assignments": ("Links between extension agents and farmers", ["read", "manage"]),
    "reference": ("Regions and crops", ["read", "manage"]),
    "farms": ("Farm profiles, resources, soil and crop cycles", ["read", "create", "update", "delete"]),
    "advisories": (
        "Advisory requests, responses, explanations, citations, feedback and observations",
        ["read", "request", "respond", "give_feedback", "review", "delete"],
    ),
    "knowledge": ("Crop guidance documents and passages", ["read", "upload", "review", "manage"]),
    "weather": ("Forecasts and freshness policies", ["read", "manage_forecasts", "manage_policies"]),
    "prices": ("Input price records", ["read", "create", "manage"]),
    "alerts": ("Weather action alerts", ["read", "manage"]),
    "audit": ("Audit log", ["read"]),
    "data": ("Data scope", ["all_farmers"]),  # See and change the data of all farmers
    "system": ("System operations", ["delete_all"]),
}

FARMER = [
    "farms.read", "farms.create", "farms.update", "farms.delete",
    "advisories.read", "advisories.request", "advisories.give_feedback",
    "knowledge.read", "weather.read", "prices.read", "prices.create", "alerts.read",
    "consents.read", "consents.create", "assignments.read", "reference.read",
    "sessions.read", "sessions.revoke",
]

ROLES = {  # Role name -> (description, privilege codes). "*" means all privileges.
    "admin": ("System administrator", ["*"]),
    "farmer": ("Smallholder farmer. Sees only their own data.", FARMER),
    "extension_agent": (
        "Extension agent. Sees their own data and the data of assigned farmers, and can register farmers.",
        FARMER + ["users.read", "users.create"],
    ),
    "agronomist": (
        "Agricultural specialist who reviews guidance and referred advice. Sees the data of all farmers.",
        [
            "data.all_farmers", "users.read", "farms.read",
            "advisories.read", "advisories.respond", "advisories.review",
            "knowledge.read", "knowledge.upload", "knowledge.review", "knowledge.manage",
            "weather.read", "weather.manage_forecasts", "weather.manage_policies",
            "prices.read", "prices.create", "prices.manage",
            "reference.read", "reference.manage", "alerts.read", "alerts.manage",
            "consents.read", "assignments.read", "sessions.read", "sessions.revoke",
        ],
    ),
}


def seed_rbac(db: Session) -> None:  # Create modules, privileges and roles. Safe to run again.
    privileges = {}  # Privilege code -> Privilege
    for module_name, (description, actions) in MODULES.items():
        module = db.query(Module).filter_by(name=module_name).first()
        if module is None:
            module = Module(name=module_name)
            db.add(module)
        module.description = description
        for action in actions:
            code = f"{module_name}.{action}"
            privilege = db.query(Privilege).filter_by(code=code).first()
            if privilege is None:
                privilege = Privilege(code=code, module=module)
                db.add(privilege)
            privileges[code] = privilege
    db.flush()

    for role_name, (description, codes) in ROLES.items():
        role = db.query(Role).filter_by(name=role_name).first()
        if role is None:
            role = Role(name=role_name)
            db.add(role)
        role.description = description
        role.is_system = True
        if codes == ["*"]:
            role.privileges = db.query(Privilege).all()  # Also privileges that an admin added
        else:
            role.privileges = [privileges[code] for code in codes]
        role.modules = list({p.module for p in role.privileges})  # Modules that the privileges are in


def seed_test_user(db: Session) -> str | None:  # Create the first admin. Return the password if it was made.
    if db.query(User).filter_by(username=SEED_ADMIN_USERNAME).first() is not None:
        return None
    password = settings.seed_admin_password  # Set SEED_ADMIN_PASSWORD in .env to choose the password
    generated = None
    if not password:
        password = generated = secrets.token_urlsafe(12)  # No fixed password in the code
        print(f"🔑 [SEED] Password for {SEED_ADMIN_USERNAME}: {password}  (set SEED_ADMIN_PASSWORD to choose one)")
    test_user = User(
        username=SEED_ADMIN_USERNAME, email="john@example.com", hashed_password=hash_password(password)
    )
    test_user.roles.append(db.query(Role).filter_by(name="admin").one())
    db.add(test_user)
    return generated
