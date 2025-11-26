"""
Seed script to populate the database with sample components.
Run this script to create sample components for testing the component API.

Usage:
    python seed_components.py
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent))

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.component import Component, ContentStatus
from app.models.user import User
from app.config import settings


async def create_sample_components():
    """Create sample components in the database."""
    
    print("🔄 Connecting to database...")
    client = AsyncIOMotorClient(settings.database_url)
    database = client["user_management_db"]
    
    print("🔄 Initializing Beanie...")
    await init_beanie(database=database, document_models=[Component, User])
    
    print("✅ Database connected")
    
    # Get or create a default user for the components
    default_user = await User.find_one({"email": {"$regex": ".*@.*"}})
    if not default_user:
        print("⚠️ No users found in database. Components will be created without user_id.")
        user_id = None
    else:
        user_id = default_user.id
        print(f"✅ Using user: {default_user.email}")
    
    # Sample components data
    sample_components = [
        {
            "title": "Modern Button Component",
            "category": "UI Components",
            "type": "Button",
            "language": "React",
            "difficulty_level": "Beginner",
            "plan_type": "Free",
            "short_description": "A modern, customizable button component with multiple variants and sizes",
            "full_description": """
# Modern Button Component

A highly customizable button component built with React and TypeScript. Features multiple variants, sizes, and loading states.

## Features
- Multiple variants: primary, secondary, outline, ghost
- Size options: small, medium, large
- Loading state with spinner
- Disabled state
- Custom icons support
- Accessible (ARIA compliant)

## Usage
```jsx
<Button variant="primary" size="medium" onClick={handleClick}>
  Click me
</Button>
```
            """,
            "preview_images": ["https://via.placeholder.com/800x600/4F46E5/FFFFFF?text=Modern+Button"],
            "git_repo_url": "https://github.com/example/modern-button",
            "live_demo_url": "https://example.com/button-demo",
            "dependencies": ["react", "typescript", "tailwindcss"],
            "tags": ["button", "ui", "react", "typescript", "accessible"],
            "developer_name": "UI Team",
            "developer_experience": "5 years",
            "featured": True,
            "code": {
                "Button.tsx": """import React from 'react';
import { ButtonHTMLAttributes } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  isLoading = false,
  children,
  ...props
}) => {
  return (
    <button className={`btn btn-${variant} btn-${size}`} {...props}>
      {isLoading ? 'Loading...' : children}
    </button>
  );
};""",
                "Button.css": """.btn {
  font-weight: 600;
  border-radius: 0.5rem;
  transition: all 0.2s;
}

.btn-primary {
  background: #4F46E5;
  color: white;
}

.btn-sm { padding: 0.5rem 1rem; }
.btn-md { padding: 0.75rem 1.5rem; }
.btn-lg { padding: 1rem 2rem; }"""
            },
            "readme_content": "# Modern Button Component\n\nA beautiful, accessible button component for modern React applications.",
        },
        {
            "title": "Responsive Card Component",
            "category": "UI Components",
            "type": "Card",
            "language": "React",
            "difficulty_level": "Beginner",
            "plan_type": "Free",
            "short_description": "A flexible card component with header, body, and footer sections",
            "full_description": """
# Responsive Card Component

A versatile card component that adapts to different screen sizes and content types.

## Features
- Responsive design
- Optional header, body, and footer
- Image support
- Hover effects
- Shadow variants
            """,
            "preview_images": ["https://via.placeholder.com/800x600/10B981/FFFFFF?text=Card+Component"],
            "dependencies": ["react", "css-modules"],
            "tags": ["card", "ui", "responsive", "react"],
            "developer_name": "Frontend Dev",
            "developer_experience": "3 years",
            "featured": True,
            "code": """<Card>
  <CardHeader>Title</CardHeader>
  <CardBody>Content here</CardBody>
  <CardFooter>Actions</CardFooter>
</Card>""",
        },
        {
            "title": "Modal Dialog Component",
            "category": "UI Components",
            "type": "Modal",
            "language": "Vue",
            "difficulty_level": "Intermediate",
            "plan_type": "Free",
            "short_description": "A customizable modal dialog with overlay and animations",
            "full_description": """
# Modal Dialog Component

A fully-featured modal dialog component with smooth animations and keyboard navigation.

## Features
- Smooth fade-in/fade-out animations
- Backdrop click to close
- ESC key to close
- Focus trap for accessibility
- Customizable sizes
- Portal rendering
            """,
            "preview_images": ["https://via.placeholder.com/800x600/8B5CF6/FFFFFF?text=Modal+Dialog"],
            "dependencies": ["vue", "vue-router"],
            "tags": ["modal", "dialog", "overlay", "vue", "accessible"],
            "developer_name": "Vue Expert",
            "developer_experience": "4 years",
            "featured": False,
            "code": "<Modal v-model='isOpen' title='My Modal'>\n  <p>Modal content</p>\n</Modal>",
        },
        {
            "title": "Flex Grid System",
            "category": "Layout Components",
            "type": "Grid",
            "language": "CSS",
            "difficulty_level": "Beginner",
            "plan_type": "Free",
            "short_description": "A flexible grid system built with CSS Flexbox",
            "full_description": """
# Flex Grid System

A lightweight, responsive grid system using CSS Flexbox. No JavaScript required.

## Features
- 12-column grid
- Responsive breakpoints
- Gap utilities
- Alignment utilities
- Nesting support
            """,
            "preview_images": ["https://via.placeholder.com/800x600/F59E0B/FFFFFF?text=Grid+System"],
            "dependencies": [],
            "tags": ["grid", "layout", "flexbox", "css", "responsive"],
            "developer_name": "CSS Specialist",
            "developer_experience": "6 years",
            "featured": False,
        },
        {
            "title": "Advanced Data Table",
            "category": "UI Components",
            "type": "Table",
            "language": "React",
            "difficulty_level": "Advanced",
            "plan_type": "Paid",
            "short_description": "Feature-rich data table with sorting, filtering, and pagination",
            "full_description": """
# Advanced Data Table

A powerful data table component with all the features you need for complex data display.

## Features
- Sorting (single and multi-column)
- Filtering (text, select, date range)
- Pagination
- Row selection
- Export to CSV/Excel
- Responsive design
- Virtual scrolling for large datasets
- Customizable columns
            """,
            "preview_images": ["https://via.placeholder.com/800x600/EF4444/FFFFFF?text=Data+Table"],
            "git_repo_url": "https://github.com/example/data-table-pro",
            "live_demo_url": "https://example.com/table-demo",
            "dependencies": ["react", "typescript", "react-table", "date-fns"],
            "tags": ["table", "data-grid", "sorting", "filtering", "pagination", "enterprise"],
            "developer_name": "Enterprise Team",
            "developer_experience": "8 years",
            "featured": True,
        },
        {
            "title": "Form Validation Kit",
            "category": "Form Components",
            "type": "Form",
            "language": "React",
            "difficulty_level": "Intermediate",
            "plan_type": "Paid",
            "short_description": "Complete form validation solution with hooks and components",
            "full_description": """
# Form Validation Kit

A comprehensive form validation library with pre-built components and validation rules.

## Features
- Built-in validation rules
- Custom validation support
- Async validation
- Field-level and form-level validation
- Error messages
- Touch/dirty state tracking
- Integration with popular form libraries
            """,
            "preview_images": ["https://via.placeholder.com/800x600/06B6D4/FFFFFF?text=Form+Validation"],
            "dependencies": ["react", "yup", "react-hook-form"],
            "tags": ["form", "validation", "hooks", "react", "typescript"],
            "developer_name": "Form Masters",
            "developer_experience": "5 years",
        },
        {
            "title": "Dropdown Select Component",
            "category": "Form Components",
            "type": "Select",
            "language": "Angular",
            "difficulty_level": "Intermediate",
            "plan_type": "Free",
            "short_description": "An accessible dropdown select with search and multi-select",
            "full_description": """
# Dropdown Select Component

A feature-rich dropdown select component for Angular applications.

## Features
- Single and multi-select modes
- Search/filter options
- Keyboard navigation
- Virtual scrolling for large lists
- Custom option templates
- Loading state
- Disabled options
            """,
            "preview_images": ["https://via.placeholder.com/800x600/EC4899/FFFFFF?text=Dropdown+Select"],
            "dependencies": ["@angular/core", "@angular/forms"],
            "tags": ["select", "dropdown", "form", "angular", "accessible"],
            "developer_name": "Angular Team",
            "developer_experience": "4 years",
        },
        {
            "title": "Toast Notification System",
            "category": "UI Components",
            "type": "Notification",
            "language": "React",
            "difficulty_level": "Intermediate",
            "plan_type": "Free",
            "short_description": "Elegant toast notifications with queuing and animations",
            "full_description": """
# Toast Notification System

A beautiful toast notification system with smooth animations and smart positioning.

## Features
- Multiple positions (top-left, top-right, bottom-left, bottom-right)
- Auto-dismiss with configurable duration
- Manual dismiss
- Queue management
- Different variants (success, error, warning, info)
- Progress bar
- Custom icons
            """,
            "preview_images": ["https://via.placeholder.com/800x600/14B8A6/FFFFFF?text=Toast+Notifications"],
            "dependencies": ["react", "framer-motion"],
            "tags": ["toast", "notification", "alert", "react", "animation"],
            "developer_name": "UX Team",
            "developer_experience": "6 years",
            "featured": True,
        },
        {
            "title": "Chart & Graph Library",
            "category": "Data Visualization",
            "type": "Chart",
            "language": "React",
            "difficulty_level": "Advanced",
            "plan_type": "Paid",
            "short_description": "Comprehensive charting library with interactive visualizations",
            "full_description": """
# Chart & Graph Library

A powerful charting library supporting multiple chart types with rich interactivity.

## Chart Types
- Line charts
- Bar charts (vertical/horizontal)
- Pie & donut charts
- Area charts
- Scatter plots
- Candlestick charts
- Radar charts

## Features
- Responsive and adaptive
- Interactive tooltips
- Zoom and pan
- Export to PNG/SVG
- Real-time data updates
- Animations
            """,
            "preview_images": ["https://via.placeholder.com/800x600/F97316/FFFFFF?text=Charts+Library"],
            "git_repo_url": "https://github.com/example/chart-library",
            "live_demo_url": "https://example.com/charts-demo",
            "dependencies": ["react", "d3", "recharts"],
            "tags": ["chart", "graph", "visualization", "data", "d3", "analytics"],
            "developer_name": "Data Viz Team",
            "developer_experience": "7 years",
            "featured": True,
        },
        {
            "title": "Sidebar Navigation",
            "category": "Layout Components",
            "type": "Navigation",
            "language": "React",
            "difficulty_level": "Beginner",
            "plan_type": "Free",
            "short_description": "Collapsible sidebar navigation with nested menus",
            "full_description": """
# Sidebar Navigation

A responsive sidebar navigation component with collapsible sections and nested menus.

## Features
- Collapsible/expandable
- Nested menu items
- Active state indicators
- Icons support
- Responsive (drawer on mobile)
- Smooth animations
            """,
            "preview_images": ["https://via.placeholder.com/800x600/6366F1/FFFFFF?text=Sidebar+Nav"],
            "dependencies": ["react", "react-icons"],
            "tags": ["sidebar", "navigation", "menu", "layout", "responsive"],
            "developer_name": "UI Designer",
            "developer_experience": "3 years",
        },
    ]
    
    print(f"\n🔄 Creating {len(sample_components)} sample components...")
    
    created_count = 0
    for comp_data in sample_components:
        try:
            # Add common fields
            comp_data.update({
                "user_id": user_id,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
                "is_active": True,
                "approval_status": ContentStatus.APPROVED,
                "is_available_for_dev": True,
                "is_purchasable": True,
            })
            
            component = Component(**comp_data)
            await component.insert()
            created_count += 1
            print(f"  ✅ Created: {comp_data['title']} ({comp_data['category']} - {comp_data['type']})")
        except Exception as e:
            print(f"  ❌ Failed to create {comp_data['title']}: {e}")
    
    print(f"\n✅ Successfully created {created_count}/{len(sample_components)} components")
    
    # Verify components were created
    total_components = await Component.find({"is_active": True}).count()
    print(f"📊 Total active components in database: {total_components}")
    
    # Show breakdown by category
    print("\n📊 Components by category:")
    categories = await Component.distinct("category", {"is_active": True})
    for category in categories:
        count = await Component.find({"category": category, "is_active": True}).count()
        print(f"  - {category}: {count}")
    
    print("\n📊 Components by plan type:")
    for plan_type in ["Free", "Paid"]:
        count = await Component.find({"plan_type": plan_type, "is_active": True}).count()
        print(f"  - {plan_type}: {count}")
    
    # Close connection
    client.close()
    print("\n✅ Seed script completed successfully!")


if __name__ == "__main__":
    asyncio.run(create_sample_components())
