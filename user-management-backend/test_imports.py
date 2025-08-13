#!/usr/bin/env python3
"""
Test script to verify all interaction system imports work correctly.
"""

import sys
import traceback

def test_import(module_name, item_name=None):
    """Test importing a module or specific item from a module."""
    try:
        if item_name:
            exec(f"from {module_name} import {item_name}")
            print(f"✅ {module_name}.{item_name} imports successfully")
        else:
            exec(f"import {module_name}")
            print(f"✅ {module_name} imports successfully")
        return True
    except Exception as e:
        print(f"❌ {module_name}{f'.{item_name}' if item_name else ''} import error: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Testing interaction system imports...")
    print()
    
    # Test models
    print("📦 Testing Models:")
    test_import("app.models.template_interactions", "TemplateCommentEnhanced")
    test_import("app.models.component_interactions", "ComponentLike")
    test_import("app.models.interaction_schemas", "CommentCreate")
    print()
    
    # Test endpoints
    print("🛣️ Testing Endpoints:")
    test_import("app.endpoints.template_interactions", "router")
    test_import("app.endpoints.component_interactions", "router")
    print()
    
    print("✨ Import test completed!")
