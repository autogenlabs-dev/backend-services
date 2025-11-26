import os

file_path = '/home/cis/Music/backend-services/user-management-backend/app/api/templates.py'

with open(file_path, 'r') as f:
    content = f.read()

# Replace Template.get with Template.find_one
old_get = 'template = await Template.get(PydanticObjectId(template_id))'
new_get = 'template = await Template.find_one({"_id": PydanticObjectId(template_id)})'

if old_get in content:
    content = content.replace(old_get, new_get)
    print("Replaced Template.get with Template.find_one")
else:
    print("Could not find Template.get call")

# Fix the hardcoded return
old_return = '''        # Simple test response
        return {
            "git_repo_url": "https://github.com/test/repo",
            "test_field": "this should work"
        }'''

new_return = '''        # Verify ID matches
        if str(template.id) != template_id:
            raise HTTPException(status_code=500, detail="Database integrity error: ID mismatch")
            
        return {
            "success": True,
            "template": template.to_dict()
        }'''

if old_return in content:
    content = content.replace(old_return, new_return)
    print("Fixed hardcoded return in get_template_by_id")
else:
    print("Could not find hardcoded return block")

with open(file_path, 'w') as f:
    f.write(content)

print("Template patch applied successfully")
