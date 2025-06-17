"""Organization management API endpoints."""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth.dependencies import get_current_user
from ..models.user import User
from ..schemas.organization import (
    OrganizationCreate, OrganizationUpdate, OrganizationResponse,
    OrganizationMemberCreate, OrganizationMemberUpdate, OrganizationMemberResponse,
    OrganizationInvitationCreate, OrganizationInvitationResponse,
    OrganizationApiKeyCreate, OrganizationApiKeyResponse, OrganizationApiKeyCreateResponse,
    OrganizationStats
)
from ..services.organization import OrganizationService, OrganizationPermissionService

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.post("/", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    org_data: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new organization"""
    try:
        org = OrganizationService.create_organization(db, current_user.id, org_data)
        
        # Add member_count for response
        org.member_count = 1  # Owner is the first member
        
        return org
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create organization: {str(e)}"
        )


@router.get("/", response_model=List[OrganizationResponse])
async def get_user_organizations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all organizations where user is a member"""
    try:
        organizations = OrganizationService.get_user_organizations(db, current_user.id)
        
        # Add member count for each organization
        for org in organizations:
            members = OrganizationService.get_organization_members(db, org.id)
            org.member_count = len(members)
        
        return organizations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch organizations: {str(e)}"
        )


@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get organization by ID"""
    # Check user has access to organization
    OrganizationPermissionService.require_organization_access(db, current_user.id, org_id, "member")
    
    org = OrganizationService.get_organization(db, org_id)
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Add member count
    members = OrganizationService.get_organization_members(db, org_id)
    org.member_count = len(members)
    
    return org


@router.put("/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    org_id: UUID,
    org_data: OrganizationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update organization (admin or owner only)"""
    # Check user has admin access
    OrganizationPermissionService.require_organization_access(db, current_user.id, org_id, "admin")
    
    try:
        org = OrganizationService.update_organization(db, org_id, org_data)
        
        # Add member count
        members = OrganizationService.get_organization_members(db, org_id)
        org.member_count = len(members)
        
        return org
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update organization: {str(e)}"
        )


@router.delete("/{org_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_organization(
    org_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete organization (owner only)"""
    # Check user is owner
    OrganizationPermissionService.require_organization_access(db, current_user.id, org_id, "owner")
    
    success = OrganizationService.delete_organization(db, org_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )


# Organization Members Management
@router.get("/{org_id}/members", response_model=List[OrganizationMemberResponse])
async def get_organization_members(
    org_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get organization members"""
    # Check user has access to organization
    OrganizationPermissionService.require_organization_access(db, current_user.id, org_id, "member")
    
    members = OrganizationService.get_organization_members(db, org_id)
    
    # Add user details to response
    member_responses = []
    for member in members:
        member_response = OrganizationMemberResponse(
            id=member.id,
            organization_id=member.organization_id,
            user_id=member.user_id,
            role=member.role,
            user_email=member.user.email,
            user_full_name=getattr(member.user, 'full_name', None),
            joined_at=member.joined_at
        )
        member_responses.append(member_response)
    
    return member_responses


@router.post("/{org_id}/members/invite", response_model=OrganizationInvitationResponse, status_code=status.HTTP_201_CREATED)
async def invite_organization_member(
    org_id: UUID,
    invitation_data: OrganizationInvitationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Invite member to organization (admin or owner only)"""
    # Check user has admin access
    OrganizationPermissionService.require_organization_access(db, current_user.id, org_id, "admin")
    
    try:
        invitation = OrganizationService.invite_member(db, org_id, current_user.id, invitation_data)
        
        # Create response with invited_by details
        response = OrganizationInvitationResponse(
            id=invitation.id,
            organization_id=invitation.organization_id,
            email=invitation.email,
            role=invitation.role,
            status=invitation.status,
            invited_by_id=invitation.invited_by_id,
            invited_by_email=current_user.email,
            created_at=invitation.created_at,
            expires_at=invitation.expires_at
        )
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send invitation: {str(e)}"
        )


@router.post("/invitations/{token}/accept", response_model=OrganizationMemberResponse)
async def accept_organization_invitation(
    token: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Accept organization invitation"""
    try:
        member = OrganizationService.accept_invitation(db, token, current_user.id)
        
        # Create response with user details
        response = OrganizationMemberResponse(
            id=member.id,
            organization_id=member.organization_id,
            user_id=member.user_id,
            role=member.role,
            user_email=current_user.email,
            user_full_name=getattr(current_user, 'full_name', None),
            joined_at=member.joined_at
        )
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to accept invitation: {str(e)}"
        )


@router.put("/{org_id}/members/{member_id}", response_model=OrganizationMemberResponse)
async def update_organization_member(
    org_id: UUID,
    member_id: UUID,
    role_data: OrganizationMemberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update organization member role (admin or owner only)"""
    # Check user has admin access
    OrganizationPermissionService.require_organization_access(db, current_user.id, org_id, "admin")
    
    try:
        member = OrganizationService.update_member_role(db, org_id, member_id, role_data)
        
        # Create response with user details
        response = OrganizationMemberResponse(
            id=member.id,
            organization_id=member.organization_id,
            user_id=member.user_id,
            role=member.role,
            user_email=member.user.email,
            user_full_name=getattr(member.user, 'full_name', None),
            joined_at=member.joined_at
        )
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update member: {str(e)}"
        )


@router.delete("/{org_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_organization_member(
    org_id: UUID,
    member_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove member from organization (admin or owner only)"""
    # Check user has admin access
    OrganizationPermissionService.require_organization_access(db, current_user.id, org_id, "admin")
    
    success = OrganizationService.remove_member(db, org_id, member_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization member not found"
        )


# Organization API Keys Management
@router.post("/{org_id}/api-keys", response_model=OrganizationApiKeyCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_organization_api_key(
    org_id: UUID,
    key_data: OrganizationApiKeyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create organization API key (admin or owner only)"""
    # Check user has admin access
    OrganizationPermissionService.require_organization_access(db, current_user.id, org_id, "admin")
    
    try:
        db_key, api_key = OrganizationService.create_api_key(db, org_id, current_user.id, key_data)
        
        response = OrganizationApiKeyCreateResponse(
            id=db_key.id,
            name=db_key.name,
            key_preview=db_key.key_preview,
            created_at=db_key.created_at,
            last_used_at=db_key.last_used_at,
            is_active=db_key.is_active,
            api_key=api_key  # Only included in creation response
        )
        
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create API key: {str(e)}"
        )


@router.get("/{org_id}/api-keys", response_model=List[OrganizationApiKeyResponse])
async def get_organization_api_keys(
    org_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get organization API keys (admin or owner only)"""
    # Check user has admin access
    OrganizationPermissionService.require_organization_access(db, current_user.id, org_id, "admin")
    
    api_keys = OrganizationService.get_organization_api_keys(db, org_id)
    return api_keys


@router.delete("/{org_id}/api-keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_organization_api_key(
    org_id: UUID,
    key_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Revoke organization API key (admin or owner only)"""
    # Check user has admin access
    OrganizationPermissionService.require_organization_access(db, current_user.id, org_id, "admin")
    
    success = OrganizationService.revoke_api_key(db, org_id, key_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )


# Organization Keys Management
@router.post("/{org_id}/keys", response_model=OrganizationApiKeyCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_organization_key(
    org_id: UUID,
    key_data: OrganizationApiKeyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new organization key."""
    OrganizationPermissionService.require_organization_access(db, current_user.id, org_id, "owner")
    key = OrganizationService.create_organization_key(db, org_id, key_data)
    return key


@router.put("/keys/{key_id}", response_model=OrganizationApiKeyResponse)
async def update_organization_key(
    key_id: UUID,
    key_data: OrganizationApiKeyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an existing organization key."""
    key = OrganizationService.update_organization_key(db, key_id, key_data)
    return key


@router.delete("/keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_organization_key(
    key_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an organization key."""
    OrganizationService.delete_organization_key(db, key_id)


# Organization Statistics
@router.get("/{org_id}/stats", response_model=OrganizationStats)
async def get_organization_stats(
    org_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get organization statistics (member access)"""
    # Check user has access to organization
    OrganizationPermissionService.require_organization_access(db, current_user.id, org_id, "member")
    
    try:
        stats = OrganizationService.get_organization_stats(db, org_id)
        return OrganizationStats(**stats)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch organization stats: {str(e)}"
        )
