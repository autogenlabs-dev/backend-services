from beanie import Document
from typing import List, Optional
from datetime import datetime

class Component(Document):
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
    user_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Settings:
        name = "components"

    def to_dict(self):
        data = self.dict()
        # Convert ObjectId to string for frontend compatibility
        if 'id' in data:
            data['id'] = str(data['id'])
        if '_id' in data:
            data['_id'] = str(data['_id'])
        return data
