"""Organization service layer for business logic."""

import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from fastapi import HTTPException, status

from ..models.user import (
    Organization, OrganizationMember, OrganizationInvitation, 
    OrganizationKey, KeyUsageLog, User, ApiKey, TokenUsageLog
)
from ..schemas.organization import (
    OrganizationCreate, OrganizationUpdate, OrganizationMemberCreate, 
    OrganizationMemberUpdate, OrganizationInvitationCreate, OrganizationApiKeyCreate
)


class OrganizationService:
    """Service class for organization operations"""
    
    @staticmethod
    def create_organization(db: Session, user_id: UUID, org_data: OrganizationCreate) -> Organization:
        """Create a new organization"""
        
        # Check if slug is already taken
        existing_org = db.query(Organization).filter(Organization.slug == org_data.slug).first()
        if existing_org:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Organization slug already exists"
            )
        
        # Create organization
        org = Organization(
            name=org_data.name,
            slug=org_data.slug,
            description=org_data.description,
            owner_id=user_id,
            subscription_plan="ultra",
            monthly_token_limit=1000000,
            reset_date=datetime.now(timezone.utc).replace(day=1) + timedelta(days=32)
        )
        
        db.add(org)
        db.flush()  # Get the ID
        
        # Add owner as member
        owner_member = OrganizationMember(
            organization_id=org.id,
            user_id=user_id,
            role="owner"
        )
        
        db.add(owner_member)
        db.commit()
        db.refresh(org)
        
        return org
    
    @staticmethod
    def get_organization(db: Session, org_id: UUID) -> Optional[Organization]:
        """Get organization by ID"""
        return db.query(Organization).filter(Organization.id == org_id).first()
    
    @staticmethod
    def get_organization_by_slug(db: Session, slug: str) -> Optional[Organization]:
        """Get organization by slug"""
        return db.query(Organization).filter(Organization.slug == slug).first()
    
    @staticmethod
    def get_user_organizations(db: Session, user_id: UUID) -> List[Organization]:
        """Get all organizations where user is a member"""
        return db.query(Organization).join(OrganizationMember).filter(
            OrganizationMember.user_id == user_id,
            Organization.is_active == True
        ).all()
    
    @staticmethod
    def update_organization(db: Session, org_id: UUID, org_data: OrganizationUpdate) -> Organization:
        """Update organization"""
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        update_data = org_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(org, field, value)
        
        db.commit()
        db.refresh(org)
        return org
    
    @staticmethod
    def delete_organization(db: Session, org_id: UUID) -> bool:
        """Soft delete organization"""
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            return False
        
        org.is_active = False
        db.commit()
        return True
    
    @staticmethod
    def check_user_permission(db: Session, user_id: UUID, org_id: UUID, required_role: str = "member") -> bool:
        """Check if user has required permission in organization"""
        member = db.query(OrganizationMember).filter(
            and_(
                OrganizationMember.user_id == user_id,
                OrganizationMember.organization_id == org_id
            )
        ).first()
        
        if not member:
            return False
        
        role_hierarchy = {"owner": 3, "admin": 2, "member": 1}
        return role_hierarchy.get(member.role, 0) >= role_hierarchy.get(required_role, 0)
    
    @staticmethod
    def get_organization_members(db: Session, org_id: UUID) -> List[OrganizationMember]:
        """Get all organization members"""
        return db.query(OrganizationMember).filter(
            OrganizationMember.organization_id == org_id
        ).all()
    
    @staticmethod
    def invite_member(db: Session, org_id: UUID, invited_by_id: UUID, invitation_data: OrganizationInvitationCreate) -> OrganizationInvitation:
        """Invite a new member to organization"""
        
        # Check if user already exists and is already a member
        existing_user = db.query(User).filter(User.email == invitation_data.email).first()
        if existing_user:
            existing_member = db.query(OrganizationMember).filter(
                and_(
                    OrganizationMember.user_id == existing_user.id,
                    OrganizationMember.organization_id == org_id
                )
            ).first()
            if existing_member:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User is already a member of this organization"
                )
        
        # Check for existing pending invitation
        existing_invitation = db.query(OrganizationInvitation).filter(
            and_(
                OrganizationInvitation.email == invitation_data.email,
                OrganizationInvitation.organization_id == org_id,
                OrganizationInvitation.status == "pending"
            )
        ).first()
        
        if existing_invitation:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Invitation already sent to this email"
            )
        
        # Create invitation
        invitation = OrganizationInvitation(
            organization_id=org_id,
            email=invitation_data.email,
            role=invitation_data.role,
            invited_by_id=invited_by_id,
            status="pending",
            token=secrets.token_urlsafe(32),
            expires_at=datetime.now(timezone.utc) + timedelta(days=7)
        )
        
        db.add(invitation)
        db.commit()
        db.refresh(invitation)
        
        return invitation
    
    @staticmethod
    def accept_invitation(db: Session, token: str, user_id: UUID) -> OrganizationMember:
        """Accept organization invitation"""
        invitation = db.query(OrganizationInvitation).filter(
            and_(
                OrganizationInvitation.token == token,
                OrganizationInvitation.status == "pending",
                OrganizationInvitation.expires_at > datetime.now(timezone.utc)
            )
        ).first()
        
        if not invitation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid or expired invitation"
            )
        
        # Get user email to verify
        user = db.query(User).filter(User.id == user_id).first()
        if not user or user.email != invitation.email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invitation is for a different email address"
            )
        
        # Create membership
        member = OrganizationMember(
            organization_id=invitation.organization_id,
            user_id=user_id,
            role=invitation.role
        )
        
        # Update invitation status
        invitation.status = "accepted"
        
        db.add(member)
        db.commit()
        db.refresh(member)
        
        return member
    
    @staticmethod
    def update_member_role(db: Session, org_id: UUID, member_id: UUID, role_data: OrganizationMemberUpdate) -> OrganizationMember:
        """Update organization member role"""
        member = db.query(OrganizationMember).filter(
            and_(
                OrganizationMember.id == member_id,
                OrganizationMember.organization_id == org_id
            )
        ).first()
        
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization member not found"
            )
        
        if member.role == "owner":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot change owner role"
            )
        
        member.role = role_data.role
        db.commit()
        db.refresh(member)
        
        return member
    
    @staticmethod
    def remove_member(db: Session, org_id: UUID, member_id: UUID) -> bool:
        """Remove member from organization"""
        member = db.query(OrganizationMember).filter(
            and_(
                OrganizationMember.id == member_id,
                OrganizationMember.organization_id == org_id
            )
        ).first()
        
        if not member:
            return False
        
        if member.role == "owner":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot remove organization owner"
            )
        
        db.delete(member)
        db.commit()
        return True
    
    @staticmethod
    def create_api_key(db: Session, org_id: UUID, user_id: UUID, key_data: OrganizationApiKeyCreate) -> tuple[ApiKey, str]:
        """Create organization API key"""
        
        # Generate API key
        api_key = f"org_{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        key_preview = api_key[:8]
        
        # Create API key record
        db_key = ApiKey(
            user_id=user_id,  # The user who created it
            key_hash=key_hash,
            key_preview=key_preview,
            name=key_data.name,
            organization_id=org_id  # Add this field to model
        )
        
        db.add(db_key)
        db.commit()
        db.refresh(db_key)
        
        return db_key, api_key
    
    @staticmethod
    def get_organization_api_keys(db: Session, org_id: UUID) -> List[ApiKey]:
        """Get all API keys for organization"""
        return db.query(ApiKey).filter(
            and_(
                ApiKey.organization_id == org_id,
                ApiKey.is_active == True
            )
        ).all()
    
    @staticmethod
    def revoke_api_key(db: Session, org_id: UUID, key_id: UUID) -> bool:
        """Revoke organization API key"""
        api_key = db.query(ApiKey).filter(
            and_(
                ApiKey.id == key_id,
                ApiKey.organization_id == org_id
            )
        ).first()
        
        if not api_key:
            return False
        
        api_key.is_active = False
        db.commit()
        return True
    
    @staticmethod
    def get_organization_stats(db: Session, org_id: UUID) -> Dict[str, Any]:
        """Get organization statistics"""
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        # Get member count
        member_count = db.query(OrganizationMember).filter(
            OrganizationMember.organization_id == org_id
        ).count()
        
        # Get API key count
        api_key_count = db.query(ApiKey).filter(
            and_(
                ApiKey.organization_id == org_id,
                ApiKey.is_active == True
            )
        ).count()
        
        # Calculate usage percentage
        usage_percentage = (org.tokens_used / org.monthly_token_limit * 100) if org.monthly_token_limit > 0 else 0
        
        # Calculate days until reset
        days_until_reset = (org.reset_date - datetime.now(timezone.utc)).days if org.reset_date else 0
        
        # Get recent activity (last 7 days)
        recent_activity = db.query(TokenUsageLog).filter(
            and_(
                TokenUsageLog.organization_id == org_id,
                TokenUsageLog.created_at >= datetime.now(timezone.utc) - timedelta(days=7)
            )
        ).count()
        
        return {
            "total_members": member_count,
            "total_api_keys": api_key_count,
            "monthly_tokens_used": org.tokens_used,
            "monthly_token_limit": org.monthly_token_limit,
            "token_usage_percentage": round(usage_percentage, 2),
            "days_until_reset": max(0, days_until_reset),
            "recent_activity_count": recent_activity
        }
    
    @staticmethod
    def create_organization_key(db: Session, org_id: UUID, key_data: OrganizationApiKeyCreate, created_by: UUID) -> OrganizationKey:
        """Create a new organization key."""
        key = OrganizationKey(
            organization_id=org_id,
            name=key_data.name,
            key_hash=secrets.token_hex(32),
            permissions=key_data.permissions,
            created_by=created_by,
            created_at=datetime.now(timezone.utc)
        )
        db.add(key)
        db.commit()
        db.refresh(key)
        return key

    @staticmethod
    def update_organization_key(db: Session, key_id: UUID, key_data: OrganizationApiKeyCreate) -> OrganizationKey:
        """Update an existing organization key."""
        key = db.query(OrganizationKey).filter(OrganizationKey.id == key_id).first()
        if not key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization key not found"
            )
        key.name = key_data.name
        key.permissions = key_data.permissions
        db.commit()
        db.refresh(key)
        return key

    @staticmethod
    def delete_organization_key(db: Session, key_id: UUID) -> None:
        """Delete an organization key."""
        key = db.query(OrganizationKey).filter(OrganizationKey.id == key_id).first()
        if not key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization key not found"
            )
        db.delete(key)
        db.commit()


class OrganizationPermissionService:
    """Service for organization permission checks"""
    
    @staticmethod
    def require_organization_access(db: Session, user_id: UUID, org_id: UUID, required_role: str = "member"):
        """Require user to have access to organization with specified role"""
        if not OrganizationService.check_user_permission(db, user_id, org_id, required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {required_role}"
            )
    
    @staticmethod
    def get_user_org_role(db: Session, user_id: UUID, org_id: UUID) -> Optional[str]:
        """Get user's role in organization"""
        member = db.query(OrganizationMember).filter(
            and_(
                OrganizationMember.user_id == user_id,
                OrganizationMember.organization_id == org_id
            )
        ).first()
        
        return member.role if member else None
