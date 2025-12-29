#!/usr/bin/env python3
"""
Test role-based access control for templates and components endpoints.
Since authentication is handled by Clerk, this script documents expected behavior
and provides a framework for manual testing with real tokens.

Usage:
  # Test with unauthenticated requests (should see 401/403)
  python3 scripts/test_role_based_access.py
  
  # Test with user token
  USER_TOKEN="<clerk_jwt>" python3 scripts/test_role_based_access.py
  
  # Test with admin token
  ADMIN_TOKEN="<clerk_jwt>" python3 scripts/test_role_based_access.py
  
  # Test with both
  USER_TOKEN="<user_jwt>" ADMIN_TOKEN="<admin_jwt>" python3 scripts/test_role_based_access.py
"""

import os
import requests
import json
from typing import Dict, List, Optional

BASE_URL = "http://127.0.0.1:8000/api"

# Endpoint definitions with expected access levels
ENDPOINTS = {
    "templates": {
        "POST /templates/": {
            "method": "POST",
            "path": "/templates/",
            "user": False,  # USER role without can_publish_content: FORBIDDEN
            "user_creator": True,  # USER with can_publish_content: ALLOWED
            "admin": True,  # ADMIN: ALLOWED
            "public": False,  # Unauthenticated: FORBIDDEN
            "payload": {
                "title": "Test Template",
                "category": "test",
                "type": "test",
                "language": "python",
                "difficulty_level": "beginner",
                "short_description": "Test",
                "full_description": "Test template",
                "developer_name": "Test Dev",
                "developer_experience": "5 years"
            }
        },
        "GET /templates/": {
            "method": "GET",
            "path": "/templates/",
            "user": True,
            "user_creator": True,
            "admin": True,
            "public": True,  # Public endpoints usually allow listing
        },
        "GET /templates/my-templates": {
            "method": "GET",
            "path": "/templates/my-templates",
            "user": True,  # User can see their own
            "user_creator": True,
            "admin": True,
            "public": False,
        },
        "GET /templates/{id}": {
            "method": "GET",
            "path": "/templates/000000000000000000000000",
            "user": True,
            "user_creator": True,
            "admin": True,
            "public": True,
        },
        "PUT /templates/{id}": {
            "method": "PUT",
            "path": "/templates/000000000000000000000000",
            "user": False,  # Can't update unless creator or admin
            "user_creator": True,  # Creator can update their own
            "admin": True,
            "public": False,
            "payload": {"title": "Updated"}
        },
        "DELETE /templates/{id}": {
            "method": "DELETE",
            "path": "/templates/000000000000000000000000",
            "user": False,
            "user_creator": True,  # Creator can delete their own
            "admin": True,
            "public": False,
        },
        "POST /templates/{id}/like": {
            "method": "POST",
            "path": "/templates/000000000000000000000000/like",
            "user": True,  # Any authenticated user can like
            "user_creator": True,
            "admin": True,
            "public": False,
        },
        "POST /templates/{id}/download": {
            "method": "POST",
            "path": "/templates/000000000000000000000000/download",
            "user": True,
            "user_creator": True,
            "admin": True,
            "public": False,
        },
    },
    "components": {
        "POST /components/": {
            "method": "POST",
            "path": "/components/",
            "user": False,
            "user_creator": True,
            "admin": True,
            "public": False,
            "payload": {
                "title": "Test Component",
                "category": "test",
                "type": "test",
                "language": "react",
                "difficulty_level": "beginner",
                "short_description": "Test",
                "full_description": "Test component",
                "developer_name": "Test Dev",
                "developer_experience": "5 years"
            }
        },
        "GET /components/": {
            "method": "GET",
            "path": "/components/",
            "user": True,
            "user_creator": True,
            "admin": True,
            "public": True,
        },
        "GET /components/my-components": {
            "method": "GET",
            "path": "/components/my-components",
            "user": True,
            "user_creator": True,
            "admin": True,
            "public": False,
        },
        "GET /components/{id}": {
            "method": "GET",
            "path": "/components/000000000000000000000000",
            "user": True,
            "user_creator": True,
            "admin": True,
            "public": True,
        },
        "PUT /components/{id}": {
            "method": "PUT",
            "path": "/components/000000000000000000000000",
            "user": False,
            "user_creator": True,
            "admin": True,
            "public": False,
            "payload": {"title": "Updated"}
        },
        "DELETE /components/{id}": {
            "method": "DELETE",
            "path": "/components/000000000000000000000000",
            "user": False,
            "user_creator": True,
            "admin": True,
            "public": False,
        },
        "POST /components/{id}/like": {
            "method": "POST",
            "path": "/components/000000000000000000000000/like",
            "user": True,
            "user_creator": True,
            "admin": True,
            "public": False,
        },
        "POST /components/{id}/download": {
            "method": "POST",
            "path": "/components/000000000000000000000000/download",
            "user": True,
            "user_creator": True,
            "admin": True,
            "public": False,
        },
    }
}


def test_endpoint(endpoint_name: str, config: Dict, token: Optional[str] = None, role: str = "public") -> Dict:
    """Test a single endpoint and return results."""
    method = config["method"]
    path = config["path"]
    url = BASE_URL + path
    
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    payload = config.get("payload")
    
    try:
        if method == "GET":
            resp = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            resp = requests.post(url, json=payload or {}, headers=headers, timeout=10)
        elif method == "PUT":
            resp = requests.put(url, json=payload or {}, headers=headers, timeout=10)
        elif method == "DELETE":
            resp = requests.delete(url, headers=headers, timeout=10)
        else:
            resp = requests.request(method, url, headers=headers, timeout=10)
        
        status = resp.status_code
        expected_allowed = config.get(role, False)
        
        # Determine if result matches expectation
        if expected_allowed:
            # Should succeed (2xx) or return 404 (resource not found, but auth OK)
            actual_allowed = status in [200, 201, 204, 404]
        else:
            # Should be forbidden (401, 403)
            actual_allowed = status not in [401, 403]
        
        result = {
            "endpoint": endpoint_name,
            "method": method,
            "path": path,
            "role": role,
            "status_code": status,
            "expected_allowed": expected_allowed,
            "actual_allowed": actual_allowed,
            "pass": actual_allowed == expected_allowed,
            "response_snippet": resp.text[:200] if resp.text else ""
        }
        
        return result
    
    except Exception as e:
        return {
            "endpoint": endpoint_name,
            "method": method,
            "path": path,
            "role": role,
            "status_code": None,
            "expected_allowed": config.get(role, False),
            "actual_allowed": False,
            "pass": False,
            "error": str(e)
        }


def main():
    user_token = os.getenv("USER_TOKEN")
    admin_token = os.getenv("ADMIN_TOKEN")
    
    results = []
    
    print("=" * 80)
    print("ROLE-BASED ACCESS CONTROL TEST")
    print("=" * 80)
    print(f"Testing against: {BASE_URL}")
    print(f"USER_TOKEN provided: {'Yes' if user_token else 'No'}")
    print(f"ADMIN_TOKEN provided: {'Yes' if admin_token else 'No'}")
    print("=" * 80)
    print()
    
    # If USER_TOKEN is provided, create a template and component owned by that user
    created_template_id = None
    created_component_id = None
    if user_token:
        print("\nCreating test resources for user token...\n")
        # Create template
        tpl_cfg = ENDPOINTS['templates']['POST /templates/']
        tpl_payload = tpl_cfg.get('payload', {})
        try:
            resp = requests.post(BASE_URL + tpl_cfg['path'], json=tpl_payload, headers={"Authorization": f"Bearer {user_token}"}, timeout=10)
            if resp.status_code in (200, 201):
                data = resp.json()
                created_template_id = data.get('template', {}).get('id') or data.get('id') or data.get('template', {}).get('_id')
                print(f"Created template id: {created_template_id}")
        except Exception as e:
            print(f"Warning: Creating template failed: {e}")

        # Create component
        comp_cfg = ENDPOINTS['components']['POST /components/']
        comp_payload = comp_cfg.get('payload', {})
        try:
            resp = requests.post(BASE_URL + comp_cfg['path'], json=comp_payload, headers={"Authorization": f"Bearer {user_token}"}, timeout=10)
            if resp.status_code in (200, 201):
                data = resp.json()
                created_component_id = data.get('component', {}).get('id') or data.get('id') or data.get('component', {}).get('_id')
                print(f"Created component id: {created_component_id}")
        except Exception as e:
            print(f"Warning: Creating component failed: {e}")

    # If created IDs exist, update endpoints for get/put/delete/like/download
    if created_template_id:
        for key, cfg in ENDPOINTS['templates'].items():
            ENDPOINTS['templates'][key]['path'] = ENDPOINTS['templates'][key]['path'].replace('000000000000000000000000', created_template_id)

    if created_component_id:
        for key, cfg in ENDPOINTS['components'].items():
            ENDPOINTS['components'][key]['path'] = ENDPOINTS['components'][key]['path'].replace('000000000000000000000000', created_component_id)

    # Test each endpoint with each role
    for category, endpoints in ENDPOINTS.items():
        print(f"\n{'=' * 80}")
        print(f"Testing {category.upper()} endpoints")
        print('=' * 80)
        
        for endpoint_name, config in endpoints.items():
            print(f"\n{endpoint_name}:")
            
            # Test public (unauthenticated)
            result = test_endpoint(endpoint_name, config, None, "public")
            results.append(result)
            status_icon = "✓" if result["pass"] else "✗"
            print(f"  PUBLIC: {status_icon} {result['status_code']} (expected: {'ALLOW' if result['expected_allowed'] else 'DENY'})")
            
            # Test user (if token provided)
            if user_token:
                result = test_endpoint(endpoint_name, config, user_token, "user")
                results.append(result)
                status_icon = "✓" if result["pass"] else "✗"
                print(f"  USER: {status_icon} {result['status_code']} (expected: {'ALLOW' if result['expected_allowed'] else 'DENY'})")
            
            # Test admin (if token provided)
            if admin_token:
                result = test_endpoint(endpoint_name, config, admin_token, "admin")
                results.append(result)
                status_icon = "✓" if result["pass"] else "✗"
                print(f"  ADMIN: {status_icon} {result['status_code']} (expected: {'ALLOW' if result['expected_allowed'] else 'DENY'})")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    total = len(results)
    passed = sum(1 for r in results if r["pass"])
    failed = total - passed
    
    print(f"Total tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Pass rate: {100*passed/total if total > 0 else 0:.1f}%")
    
    if failed > 0:
        print("\nFailed tests:")
        for r in results:
            if not r["pass"]:
                print(f"  - {r['endpoint']} ({r['role']}): got {r['status_code']}, expected {'ALLOW' if r['expected_allowed'] else 'DENY'}")
    
    # Write JSON report
    with open("role_based_access_report.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nDetailed results written to: role_based_access_report.json")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    exit(main())
