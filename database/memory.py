# ---------------- US 20: User Accounts ----------------

users = {
    1: {
        "user_id": 1,
        "display_name": "Win",
        "username": "win",
        "email": "win@example.com",
        "department": "IT",
        "contact": "07111111111",
        "status": "active"
    },
    2: {
        "user_id": 2,
        "display_name": "Franklin",
        "username": "franklin",
        "email": "franklin@example.com",
        "department": "IT",
        "contact": "07222222222",
        "status": "active"
    },
    3: {
        "user_id": 3,
        "display_name": "Rohit",
        "username": "rohit",
        "email": "rohit@example.com",
        "department": "Compliance",
        "contact": "07333333333",
        "status": "active"
    },
    4: {
        "user_id": 4,
        "display_name": "Tino",
        "username": "tino",
        "email": "tino@example.com",
        "department": "IT",
        "contact": "07444444444",
        "status": "active"
    }
}

next_user_id = 5


# ---------------- US 21: Roles and Permissions ----------------

user_roles = {
    1: ["Asset Manager"],
    2: ["Employee"],
    3: ["Auditor"],
    4: ["System Administrator"]
}

role_permissions = {
    "Asset Manager": [
        "asset:create",
        "asset:read",
        "asset:update",
        "asset:assign",
        "asset:return"
    ],
    "Employee": [
        "asset:view_assigned",
        "asset:acknowledge",
        "asset:return_information"
    ],
    "Auditor": [
        "audit:read",
        "audit:review",
        "audit:report"
    ],
    "System Administrator": [
        "user:manage",
        "role:manage",
        "permission:manage",
        "reference_data:manage"
    ]
}


# ---------------- US 22: Asset Categories ----------------

asset_categories = {
    1: {
        "category_id": 1,
        "name": "Laptop",
        "code": "LAP",
        "description": "Portable computing devices",
        "is_active": True
    },
    2: {
        "category_id": 2,
        "name": "Desktop",
        "code": "DES",
        "description": "Desktop computers",
        "is_active": True
    },
    3: {
        "category_id": 3,
        "name": "Monitor",
        "code": "MON",
        "description": "Computer display devices",
        "is_active": True
    },
    4: {
        "category_id": 4,
        "name": "Printer",
        "code": "PRI",
        "description": "Printing equipment",
        "is_active": True
    }
}

next_category_id = 5

asset_statuses = [
    "Available",
    "Assigned",
    "Under Maintenance",
    "Retired",
    "Disposed"
]