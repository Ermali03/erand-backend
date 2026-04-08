from typing import Final, Iterable, Literal, get_args

RoleName = Literal["Admin", "Main Surgeon", "Doctor", "Nurse"]

VALID_ROLES: Final[set[str]] = set(get_args(RoleName))
PATIENT_WRITE_ROLES: Final[set[str]] = {"Admin", "Main Surgeon", "Doctor"}
RECORD_WRITE_ROLES: Final[set[str]] = {"Admin", "Main Surgeon", "Doctor"}
ROLE_PRIORITY: Final[dict[str, int]] = {
    "Admin": 0,
    "Main Surgeon": 1,
    "Doctor": 2,
    "Nurse": 3,
}
DEFAULT_ROLE: Final[str] = "Nurse"


def parse_roles(value: str | Iterable[str] | None) -> list[str]:
    if value is None:
        return [DEFAULT_ROLE]
    if isinstance(value, str):
        raw_roles = [item.strip() for item in value.split(",") if item.strip()]
    else:
        raw_roles = [item.strip() for item in value if item and item.strip()]

    unique_roles = list(dict.fromkeys(raw_roles))
    invalid_roles = [role for role in unique_roles if role not in VALID_ROLES]
    if invalid_roles:
        raise ValueError(f"Invalid roles: {', '.join(invalid_roles)}")
    if not unique_roles:
        return [DEFAULT_ROLE]
    return sorted(unique_roles, key=lambda role: ROLE_PRIORITY[role])


def serialize_roles(roles: Iterable[str]) -> str:
    return ",".join(parse_roles(list(roles)))


def primary_role(roles: str | Iterable[str] | None) -> str:
    return parse_roles(roles)[0]


def has_any_role(user_roles: str | Iterable[str] | None, allowed_roles: set[str]) -> bool:
    return any(role in allowed_roles for role in parse_roles(user_roles))
