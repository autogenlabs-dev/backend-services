# Kilo Code File Creation Instructions

This guide provides comprehensive instructions for Kilo Code on how to use the available tools to create, modify, and manage files in the project.

## Core File Creation Tools

### 1. create_text_file
**Purpose**: Write a new file or overwrite an existing file
**When to use**: Creating completely new files or completely replacing existing file content

**Parameters**:
- `relative_path` (required): The relative path to the file to create
- `content` (required): The UTF-8 encoded content to write to the file

**Example Usage**:
```
<create_text_file>
<relative_path>src/new_component.py</relative_path>
<content>
def new_function():
    """A new function in a new file"""
    return "Hello, World!"
</content>
</create_text_file>
```

**Important Notes**:
- Automatically creates any necessary directories
- Overwrites existing files completely
- Always provide the COMPLETE intended content
- Do NOT include line numbers in the content

### 2. insert_content
**Purpose**: Add new lines of content into a file without modifying existing content
**When to use**: Adding imports, functions, configuration blocks, or any multi-line text to existing files

**Parameters**:
- `relative_path` (required): File path relative to workspace directory
- `line` (required): Line number where content will be inserted (1-based)
  - Use `0` to append at end of file
  - Use positive number to insert before that line
- `content` (required): The content to insert at the specified line

**Example Usage**:
```
<insert_content>
<path>src/utils.py</path>
<line>1</line>
<content>
# Add imports at start of file
import os
import sys
</content>
</insert_content>
```

## File Reading and Analysis Tools

### 3. read_file
**Purpose**: Read the contents of one or more files
**When to use**: Understanding existing code before making changes

**Parameters**:
- `args`: Contains one or more file elements
  - `path` (required): File path (relative to workspace directory)
  - `start_line` (optional): 0-based index of first line to retrieve
  - `end_line` (optional): 0-based index of last line to retrieve (inclusive)
  - `max_answer_chars` (optional): Maximum characters to return

**Example Usage**:
```
<read_file>
<args>
  <file>
    <path>src/main.py</path>
  </file>
  <file>
    <path>src/utils.py</path>
  </file>
</args>
</read_file>
```

**Important Notes**:
- Can read maximum of 5 files in a single request
- Outputs line-numbered content for easy reference
- Supports text extraction from .pdf, .docx, .ipynb, and .xlsx files

## File Modification Tools

### 4. apply_diff
**Purpose**: Apply precise, targeted modifications to existing files
**When to use**: SURGICAL EDITS ONLY - specific changes to existing code

**Parameters**:
- `path` (required): The path of the file to modify
- `diff` (required): The search/replace block defining the changes

**Diff Format**:
```
<<<<<<< SEARCH
:start_line: (required) The line number of original content where the search block starts.
-------
[exact content to find including whitespace]
=======
[new content to replace with]
>>>>>>> REPLACE
```

**Example Usage**:
```
<apply_diff>
<path>src/calculator.py</path>
<diff>
<<<<<<< SEARCH
:start_line:1
-------
def calculate_total(items):
    total = 0
    for item in items:
        total += item
    return total
=======
def calculate_total(items):
    """Calculate total with 10% markup"""
    return sum(item * 1.1 for item in items)
>>>>>>> REPLACE
</diff>
</apply_diff>
```

### 5. search_and_replace
**Purpose**: Find and replace specific text strings or patterns within a file
**When to use**: Targeted replacements across multiple locations within a file

**Parameters**:
- `path` (required): The path of the file to modify
- `search` (required): The text or pattern to search for
- `replace` (required): The text to replace matches with
- `start_line` (optional): Starting line number for restricted replacement
- `end_line` (optional): Ending line number for restricted replacement
- `use_regex` (optional): Treat search as regex pattern (default: false)
- `ignore_case` (optional): Ignore case when matching (default: false)

## Project Structure Analysis Tools

### 6. list_files
**Purpose**: List files and directories within a specified directory
**When to use**: Understanding project structure or finding specific files

**Parameters**:
- `path` (required): The path of the directory to list contents for
- `recursive` (optional): Whether to list files recursively (default: false)

### 7. search_files
**Purpose**: Perform regex searches across files in a specified directory
**When to use**: Finding code patterns, specific implementations, or areas needing refactoring

**Parameters**:
- `path` (required): The path of the directory to search in
- `regex` (required): The regular expression pattern to search for
- `file_pattern` (optional): Glob pattern to filter files (e.g., '*.ts')

## Best Practices for File Creation

### 1. Planning Before Creating
- Always understand the existing project structure first
- Use `list_files` or `get_symbols_overview` to understand the codebase
- Read related files to understand patterns and conventions

### 2. Choose the Right Tool
- **New file**: Use `create_text_file`
- **Add to existing file**: Use `insert_content` or `apply_diff`
- **Small changes**: Use `search_and_replace`
- **Multiple file reads**: Use `read_file` with multiple files

### 3. Follow Project Patterns
- Maintain consistent naming conventions
- Follow existing directory structure
- Include appropriate imports and dependencies
- Add comments where necessary to explain complex logic

### 4. File Organization
- Group related functionality in modules/packages
- Use consistent naming conventions across the project
- Maintain clear directory structure with logical separation
- Keep configuration separate from business logic

## Workflow Example

### Creating a New API Endpoint
1. **Analyze existing structure**:
   ```
   <list_files>
   <path>app/api</path>
   <recursive>false</recursive>
   </list_files>
   ```

2. **Read similar files for patterns**:
   ```
   <read_file>
   <args>
     <file>
       <path>app/api/users.py</path>
     </file>
   </args>
   </read_file>
   ```

3. **Create the new endpoint file**:
   ```
   <create_text_file>
   <relative_path>app/api/new_endpoint.py</relative_path>
   <content>
   from fastapi import APIRouter, Depends
   from app.auth.dependencies import get_current_user
   
   router = APIRouter()
   
   @router.get("/new-endpoint")
   async def get_new_endpoint(current_user = Depends(get_current_user)):
       """New endpoint description"""
       return {"message": "New endpoint working"}
   </content>
   </create_text_file>
   ```

4. **Update main router if needed**:
   ```
   <read_file>
   <args>
     <file>
       <path>app/main.py</path>
     </file>
   </args>
   </read_file>
   ```
   
   Then use `apply_diff` or `insert_content` to add the new router

## Error Handling

- Always wait for user confirmation after each tool use
- If a tool fails, analyze the error and adjust your approach
- Use more specific regex patterns if search operations return too many results
- Check file paths carefully - they must be relative to the workspace directory

## Advanced Tips

1. **Use wildcards in regex**: When using `search_and_replace` or `apply_diff`, use `.*?` for non-greedy matching to avoid over-matching

2. **Batch operations**: Use `read_file` to read multiple related files at once when possible

3. **Symbol-based operations**: For code files, consider using symbolic tools (`find_symbol`, `replace_symbol_body`) for more precise modifications

4. **Memory usage**: Be mindful of `max_answer_chars` parameter when working with large files

This instruction set should help Kilo Code effectively create and manage files in the project while following best practices and maintaining code quality.