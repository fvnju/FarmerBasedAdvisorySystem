from sqlalchemy.orm import Session  # Import Session type
from app.model import Module, Privilege, Role, User  # Import RBAC models

MODULES = {  # Module name -> (description, actions)
    "users": ("User accounts and roles", ["read", "create", "update", "delete", "assign_roles"]),
    "farms": ("Farm profiles, resources, soil and crop cycles", ["read", "create", "update", "delete"]),
    "advisories": ("Advisory requests, responses and feedback", ["read", "request", "give_feedback", "review"]),
    "knowledge": ("Crop guidance documents", ["read", "upload", "review"]),
    "weather": ("Forecasts and freshness policies", ["read", "manage_policies"]),
    "prices": ("Input price records", ["read", "create"]),
    "alerts": ("Weather action alerts", ["read", "manage"]),
    "audit": ("Audit log", ["read"]),
}

ROLES = {  # Role name -> (description, privilege codes). "*" means all privileges.
    "admin": ("System administrator", ["*"]),
    "farmer": (
        "Smallholder farmer",
        ["farms.read", "farms.create", "farms.update", "advisories.read", "advisories.request",
         "advisories.give_feedback", "weather.read", "prices.read", "prices.create", "alerts.read"],
    ),
    "extension_agent": (
        "Extension agent who helps assigned farmers",
        ["farms.read", "farms.create", "farms.update", "advisories.read", "advisories.request",
         "advisories.give_feedback", "knowledge.read", "weather.read", "prices.read", "prices.create",
         "alerts.read"],
    ),
    "agronomist": (
        "Agricultural specialist who reviews guidance and referred advice",
        ["farms.read", "advisories.read", "advisories.review", "knowledge.read", "knowledge.upload",
         "knowledge.review", "weather.read", "weather.manage_policies", "prices.read", "prices.create"],
    ),
}


def seed_rbac(db: Session) -> None:  # Create modules, privileges and roles. Safe to run again.
    privileges = {}  # Privilege code -> Privilege
    for module_name, (description, actions) in MODULES.items():
        module = db.query(Module).filter_by(name=module_name).first()
        if module is None:
            module = Module(name=module_name, description=description)
            db.add(module)
        for action in actions:
            code = f"{module_name}.{action}"
            privilege = db.query(Privilege).filter_by(code=code).first()
            if privilege is None:
                privilege = Privilege(code=code, module=module)
                db.add(privilege)
            privileges[code] = privilege

    for role_name, (description, codes) in ROLES.items():
        role = db.query(Role).filter_by(name=role_name).first()
        if role is None:
            role = Role(name=role_name)
            db.add(role)
        role.description = description
        role.is_system = True
        role.privileges = list(privileges.values()) if codes == ["*"] else [privileges[c] for c in codes]
        role.modules = list({p.module for p in role.privileges})  # Modules that the privileges are in


def seed_test_user(db: Session) -> None:  # Create a test admin user if it is missing
    if db.query(User).filter_by(username="johndoe").first() is None:
        test_user = User(
            username="johndoe", email="john@example.com", hashed_password="hashed_password"
        )
        test_user.roles.append(db.query(Role).filter_by(name="admin").one())
        db.add(test_user)
