"""
API Key Pool model for managing GLM and Bytez API keys.
Supports distributing keys across multiple users with configurable limits.
"""

from datetime import datetime, UTC
from typing import Optional, List
from pydantic import Field
from beanie import Document, PydanticObjectId


class ApiKeyPool(Document):
    """
    Pool of API keys (GLM or Bytez) that can be shared among users.
    Each key has a max_users limit to control distribution.
    """
    
    key_type: str  # "glm" or "bytez"
    key_value: str  # The actual API key
    label: Optional[str] = None  # Admin-defined label for identification
    max_users: int = 10  # Maximum users that can share this key
    assigned_user_ids: List[PydanticObjectId] = Field(default_factory=list)
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    
    class Settings:
        name = "api_key_pool"
        indexes = [
            "key_type",
            "is_active",
            "assigned_user_ids"
        ]
    
    @property
    def current_users(self) -> int:
        """Number of users currently assigned to this key."""
        return len(self.assigned_user_ids)
    
    @property
    def has_capacity(self) -> bool:
        """Check if key can accept more users."""
        return self.is_active and self.current_users < self.max_users
    
    @property
    def usage_percentage(self) -> float:
        """Percentage of capacity used."""
        if self.max_users == 0:
            return 100.0
        return (self.current_users / self.max_users) * 100
    
    def assign_user(self, user_id: PydanticObjectId) -> bool:
        """
        Assign a user to this key.
        Returns True if successful, False if at capacity or already assigned.
        """
        if user_id in self.assigned_user_ids:
            return True  # Already assigned
        if not self.has_capacity:
            return False
        self.assigned_user_ids.append(user_id)
        self.updated_at = datetime.now(UTC)
        return True
    
    def release_user(self, user_id: PydanticObjectId) -> bool:
        """
        Remove a user from this key.
        Returns True if user was removed, False if not found.
        """
        if user_id in self.assigned_user_ids:
            self.assigned_user_ids.remove(user_id)
            self.updated_at = datetime.now(UTC)
            return True
        return False
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "id": str(self.id),
            "key_type": self.key_type,
            "key_preview": f"{self.key_value[:8]}...{self.key_value[-4:]}" if len(self.key_value) > 12 else "***",
            "label": self.label,
            "max_users": self.max_users,
            "current_users": self.current_users,
            "usage_percentage": round(self.usage_percentage, 1),
            "has_capacity": self.has_capacity,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_admin_dict(self) -> dict:
        """Convert to dictionary with full details for admin."""
        base = self.to_dict()
        base["key_value"] = self.key_value  # Include full key for admin
        base["assigned_user_ids"] = [str(uid) for uid in self.assigned_user_ids]
        return base
