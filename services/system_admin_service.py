from fastapi import HTTPException

from database import memory


# =====================================================
# US 20: CREATE AND MANAGE USER ACCOUNTS
# =====================================================

def create_user(data):
    global_user_id = memory.next_user_id

    for user in memory.users.values():
        if user["username"].lower() == data.username.lower():
            raise HTTPException(409, "Username already exists")

        if user["email"].lower() == data.email.lower():
            raise HTTPException(409, "Email already exists")

    new_user = {
        "user_id": global_user_id,
        "display_name": data.display_name,
        "username": data.username,
        "email": str(data.email),
        "department": data.department,
        "contact": data.contact,
        "status": "active"
    }

    memory.users[global_user_id] = new_user
    memory.next_user_id += 1

    return new_user


def get_all_users():
    return list(memory.users.values())


def get_user(user_id):
    user = memory.users.get(user_id)

    if not user:
        raise HTTPException(404, "User not found")

    return user


def update_user(user_id, data):
    user = get_user(user_id)

    updates = data.model_dump(exclude_unset=True)

    for field, value in updates.items():
        user[field] = value

    return user


def deactivate_user(user_id):
    user = get_user(user_id)

    if user["status"] == "inactive":
        raise HTTPException(400, "User is already inactive")

    user["status"] = "inactive"

    return {
        "message": "User successfully deactivated",
        "user": user
    }


# =====================================================
# US 21: ASSIGN ROLES AND CONFIGURE PERMISSIONS
# =====================================================

def get_all_roles():
    return [
        {
            "role_id": role,
            "role_name": role,
            "permissions": permissions
        }
        for role, permissions in memory.role_permissions.items()
    ]


def get_role_permissions(role_id):
    permissions = memory.role_permissions.get(role_id)

    if permissions is None:
        raise HTTPException(404, "Role not found")

    return {
        "role_id": role_id,
        "permissions": permissions
    }


def assign_user_roles(user_id, roles):
    if user_id not in memory.users:
        raise HTTPException(404, "User not found")

    if memory.users[user_id]["status"] != "active":
        raise HTTPException(400, "Cannot assign roles to an inactive user")

    for role in roles:
        if role.value not in memory.role_permissions:
            raise HTTPException(400, f"Unknown role: {role.value}")

    memory.user_roles[user_id] = [role.value for role in roles]

    return {
        "user_id": user_id,
        "assigned_roles": memory.user_roles[user_id]
    }


def update_role_permissions(role_id, permissions):
    if role_id not in memory.role_permissions:
        raise HTTPException(404, "Role not found")

    # Only permissions defined by the application can be assigned.
    allowed_permissions = {
        permission
        for permission_list in memory.role_permissions.values()
        for permission in permission_list
    }

    invalid_permissions = set(permissions) - allowed_permissions

    if invalid_permissions:
        raise HTTPException(
            400,
            f"Unknown permissions: {sorted(invalid_permissions)}"
        )

    memory.role_permissions[role_id] = permissions

    return {
        "role_id": role_id,
        "permissions": permissions,
        "message": "Role permissions updated successfully"
    }


# =====================================================
# US 22: CONFIGURE ASSET CATEGORIES AND REFERENCE VALUES
# =====================================================

def get_asset_categories():
    return list(memory.asset_categories.values())


def create_asset_category(data):
    for category in memory.asset_categories.values():
        if category["code"].lower() == data.code.lower():
            raise HTTPException(409, "Category code already exists")

    category_id = memory.next_category_id

    new_category = {
        "category_id": category_id,
        "name": data.name,
        "code": data.code.upper(),
        "description": data.description,
        "is_active": True
    }

    memory.asset_categories[category_id] = new_category
    memory.next_category_id += 1

    return new_category


def update_asset_category(category_id, data):
    category = memory.asset_categories.get(category_id)

    if not category:
        raise HTTPException(404, "Asset category not found")

    updates = data.model_dump(exclude_unset=True)

    for field, value in updates.items():
        category[field] = value

    return category


def get_asset_statuses():
    return [
        {"value": status}
        for status in memory.asset_statuses
    ]