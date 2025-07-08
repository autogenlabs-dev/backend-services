from pydantic import BaseModel
from typing import List, Optional

class ComponentCreateRequest(BaseModel):
    title: str
    category: str
    type: str
    language: str
    difficulty_level: str
    plan_type: str
    pricing_inr: int = 0
    pricing_usd: int = 0
    short_description: str
    full_description: str
    preview_images: List[str] = []
    git_repo_url: Optional[str] = None
    live_demo_url: Optional[str] = None
    dependencies: List[str] = []
    tags: List[str] = []
    developer_name: str
    developer_experience: str
    is_available_for_dev: bool = True
    featured: bool = False
    code: Optional[str] = None
    readme_content: Optional[str] = None

class ComponentUpdateRequest(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    type: Optional[str] = None
    language: Optional[str] = None
    difficulty_level: Optional[str] = None
    plan_type: Optional[str] = None
    pricing_inr: Optional[int] = None
    pricing_usd: Optional[int] = None
    short_description: Optional[str] = None
    full_description: Optional[str] = None
    preview_images: Optional[List[str]] = None
    git_repo_url: Optional[str] = None
    live_demo_url: Optional[str] = None
    dependencies: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    developer_name: Optional[str] = None
    developer_experience: Optional[str] = None
    is_available_for_dev: Optional[bool] = None
    featured: Optional[bool] = None
    code: Optional[str] = None
    readme_content: Optional[str] = None
