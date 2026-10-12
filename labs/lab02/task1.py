import hashlib
import os
import hmac
import re
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass


class User:
    def __init__(
        self, username: str, email: str, role: str = "user", active: bool = True
    ):
        self.username = username
        self.email = email
        self.role = role
        self.active = active
        self.__password_hash = b""
        self.__password_salt = b""
        self._ITERATIONS = 100_000

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str):
        pattern = r"^[a-zA-Z][a-zA-Z0-9_]{2,63}@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, value):
            raise ValueError(f"Некоректний формат email: {value}")
        self._email = value

    def set_password(self, password: str):
        self.__password_salt = os.urandom(16)
        self.__password_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), self.__password_salt, self._ITERATIONS
        )

    def check_password(self, password: str) -> bool:
        if not self.__password_salt or not self.__password_hash:
            return False
        test_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), self.__password_salt, self._ITERATIONS
        )
        return hmac.compare_digest(self.__password_hash, test_hash)

    def deactivate(self):
        self.active = False

    def __str__(self):
        status = "Active" if self.active else "Inactive"
        return f"User(username='{self.username}', email='{self.email}', role='{self.role}', status='{status}')"


class Admin(User):
    def __init__(
        self, username: str, email: str, active: bool = True, permissions: set = None
    ):
        super().__init__(username, email, role="admin", active=active)
        self.permissions = permissions if permissions is not None else set()

    def grant_permission(self, permission: str):
        self.permissions.add(permission)

    def revoke_permission(self, permission: str):
        self.permissions.discard(permission)

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions

    def __str__(self):
        base_str = super().__str__()
        return f"{base_str} [Permissions: {', '.join(self.permissions) if self.permissions else 'None'}]"


class Session:
    def __init__(self, ip: str):
        self.ip = ip
        now = datetime.now(timezone.utc)
        self.login_time = now
        self.last_activity = now

    def touch(self):
        self.last_activity = datetime.now(timezone.utc)

    def is_active(self, timeout_sec: int) -> bool:
        if timeout_sec <= 0:
            raise ValueError("Timeout повинен бути позитивним числом.")
        now = datetime.now(timezone.utc)
        return (now - self.last_activity) <= timedelta(seconds=timeout_sec)


@dataclass
class LogEntry:
    timestamp: datetime
    username: str
    action: str

    def __str__(self):
        return f"[{self.timestamp.isoformat()}] {self.username} -> {self.action}"


class AuditLog:
    def __init__(self):
        self.logs = []

    def add_log(self, username: str, action: str):
        entry = LogEntry(
            timestamp=datetime.now(timezone.utc), username=username, action=action
        )
        self.logs.append(entry)

    def show_all(self):
        for log in self.logs:
            print(log)


class UserAccount:
    SESSION_TIMEOUT_SEC = 900

    def __init__(self, user: User, audit_log: AuditLog = None):
        self.user = user
        self.session = None
        self.audit_log = audit_log if audit_log is not None else AuditLog()

    def login(self, username: str, password: str, ip: str) -> bool:
        if not self.user.active or self.user.username != username:
            self.audit_log.add_log(
                username, "login_failure (user inactive or wrong username)"
            )
            return False

        if self.user.check_password(password):
            self.session = Session(ip)
            self.audit_log.add_log(username, "login_success")
            return True
        else:
            self.audit_log.add_log(username, "login_failure (wrong password)")
            return False

    def is_authenticated(self) -> bool:
        if self.session and self.session.is_active(self.SESSION_TIMEOUT_SEC):
            self.session.touch()
            return True
        return False

    def logout(self):
        if self.session:
            self.session = None
            self.audit_log.add_log(self.user.username, "logout")

    def __getitem__(self, key):
        allowed_keys = ["user", "session", "audit_log"]
        if key not in allowed_keys:
            raise KeyError(f"Доступ до атрибуту {key} заборонено або він не існує.")
        return getattr(self, key)

    def __setitem__(self, key, value):
        if key == "user" and isinstance(value, User):
            self.user = value
        elif key == "session" and (isinstance(value, Session) or value is None):
            self.session = value
        elif key == "audit_log" and isinstance(value, AuditLog):
            self.audit_log = value
        elif key in ["user", "session", "audit_log"]:
            raise TypeError(f"Неправильний тип значення для {key}.")
        else:
            raise KeyError(f"Модифікація атрибуту {key} заборонена.")
