import os

file_path = '/home/cis/Music/backend-services/user-management-backend/app/api/components.py'

with open(file_path, 'r') as f:
    content = f.read()

# Replace Component.get with Component.find_one
old_get = 'component = await Component.get(object_id)'
new_get = 'component = await Component.find_one({"_id": object_id})'

if old_get in content:
    content = content.replace(old_get, new_get)
    print("Replaced Component.get with Component.find_one")
else:
    print("Could not find Component.get call")

# Replace the ID mismatch logging with an exception
old_check = 'if str(component.id) != component_id:'
new_check = '''if str(component.id) != component_id:
            logger.error(f"🚨 ID MISMATCH DETECTED! Requested: {component_id}, Returned: {component.id}")
            raise HTTPException(status_code=500, detail="Database integrity error: ID mismatch")'''

# We need to be careful with indentation and context.
# The original code has logging inside the if block.
# Let's try to replace the whole block if possible, or just inject the raise.

# Actually, let's just find the specific log line and add the raise after it.
log_line = 'logger.error(f"   This indicates Component.get() returned the wrong document!")'
raise_line = '            raise HTTPException(status_code=500, detail="Database integrity error: ID mismatch")'

if log_line in content and raise_line not in content:
    content = content.replace(log_line, log_line + '\n' + raise_line)
    print("Added raise HTTPException to ID mismatch block")
else:
    print("Could not find log line or raise already exists")

with open(file_path, 'w') as f:
    f.write(content)

print("Patch applied successfully")
