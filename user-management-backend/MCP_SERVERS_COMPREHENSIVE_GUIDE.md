# MCP Servers Comprehensive Guide

This guide provides detailed information about all configured MCP (Model Context Protocol) servers, their available tools, usage examples, and current status.

## Final Status Summary for user-management-backend

### ✅ Working Servers (2 out of 5)
1. **Supermemory MCP Server** - Fully functional
2. **Serena MCP Server** - Works directly, MCP client connection issues

### ❌ Non-Working Servers (3 out of 5)
3. **Filesystem MCP Server** - Works directly, MCP client connection issues
4. **Sentry MCP Server** - Custom implementation works directly, MCP client connection issues
5. **GitHub Cline Community MCP Server** - Needs GitHub CLI installation

### Root Cause Analysis
The primary issue appears to be **MCP client connection problems** - servers work when run directly but fail to connect through the MCP client interface.

## Table of Contents

1. [Filesystem MCP Server](#filesystem-mcp-server)
2. [Serena MCP Server](#serena-mcp-server)
3. [Sentry MCP Server](#sentry-mcp-server)
4. [GitHub Cline Community MCP Server](#github-cline-community-mcp-server)
5. [Supermemory MCP Server](#supermemory-mcp-server)
6. [Usage Recommendations](#usage-recommendations)

---

## Filesystem MCP Server

### Configuration
```json
"filesystem": {
  "type": "stdio",
  "command": "npx",
  "args": [
    "@modelcontextprotocol/server-filesystem",
    "/home/cis/Music/extensionwithUIbuilder",
    "/home/cis/Downloads/backend-services/user-management-backend",
    "/home/cis/Music/Autogenlabs-Web-App/"
  ]
}
```

### Status
❌ **Not Working** - No tools available

### Issue
The server appears to be configured but returns "No tools available" when attempting to access any tools.

### Expected Tools
Based on the filesystem server configuration, it should provide file system operations like:
- Reading files
- Writing files
- Directory operations
- File search functionality

### Troubleshooting
- Check if the `@modelcontextprotocol/server-filesystem` package is properly installed
- Verify the npm/npx installation
- Check if the specified paths are accessible
- Consider reinstalling the filesystem server package

---

## Serena MCP Server

### Configuration
```json
"serena": {
  "timeout": 60,
  "type": "stdio",
  "command": "/home/cis/Documents/mcp/serena/.venv/bin/serena-mcp-server",
  "args": [],
  "alwaysAllow": [
    "get_symbols_overview",
    "activate_project",
    "write_memory",
    "read_memory",
    "list_memories",
    "read_file",
    "create_text_file",
    "list_dir",
    "find_file",
    "replace_regex",
    "search_for_pattern",
    "find_symbol",
    "find_referencing_symbols",
    "replace_symbol_body",
    "insert_after_symbol",
    "prepare_for_new_conversation",
    "think_about_whether_you_are_done",
    "think_about_task_adherence",
    "think_about_collected_information",
    "insert_before_symbol",
    "execute_shell_command",
    "delete_memory",
    "switch_modes",
    "check_onboarding_performed",
    "onboarding"
  ]
}
```

### Status
⚠️ **Partially Working** - Language server initialization issues

### Issue
The server activates projects successfully but encounters language server termination errors when trying to use most tools.

### Working Features
- ✅ Project activation: Successfully created and activated 'user-management-backend' project
- ✅ Memory system: Available memories for project overview, suggested commands, etc.

### Available Tools (Theoretical)
Based on configuration, these tools should be available:

#### Project Management
- `activate_project` - Activate a project for analysis
- `check_onboarding_performed` - Check if project onboarding was done
- `onboarding` - Perform project onboarding

#### Code Analysis
- `get_symbols_overview` - Get high-level understanding of code symbols
- `find_symbol` - Find specific code symbols/classes/methods
- `find_referencing_symbols` - Find references to specific symbols
- `search_for_pattern` - Search for patterns in codebase

#### File Operations
- `read_file` - Read file contents
- `create_text_file` - Create new files
- `list_dir` - List directory contents
- `find_file` - Find files matching patterns

#### Code Modification
- `replace_regex` - Replace content using regex
- `replace_symbol_body` - Replace entire symbol bodies
- `insert_after_symbol` - Insert content after symbols
- `insert_before_symbol` - Insert content before symbols

#### Memory Management
- `write_memory` - Store information in memory
- `read_memory` - Read stored memories
- `list_memories` - List available memories
- `delete_memory` - Delete memories

#### Workflow Tools
- `think_about_collected_information` - Analyze collected information
- `think_about_task_adherence` - Check if on track with task
- `think_about_whether_you_are_done` - Check if task is complete
- `prepare_for_new_conversation` - Prepare for new conversation
- `switch_modes` - Switch between different modes
- `execute_shell_command` - Execute shell commands

### Troubleshooting
- Language server (likely Python LSP) is terminating unexpectedly
- May need to check Python environment and dependencies
- Consider checking if the virtual environment is properly configured
- Verify that all required language server dependencies are installed

---

## Sentry MCP Server

### Configuration
```json
"sentry": {
  "timeout": 60,
  "type": "stdio",
  "command": "node",
  "args": [
    "/home/cis/.npm/_npx/mcp-server-sentry/index.js",
    "--auth-token",
    "YOUR_SENTRY_AUTH_TOKEN_HERE"
  ],
  "alwaysAllow": [
    "get_sentry_issue"
  ]
}
```

### Status
❌ **Not Working** - No tools available

### Issue
The server appears to be configured with authentication token but returns "No tools available" when attempting to access tools.

### Expected Tools
Based on configuration:
- `get_sentry_issue` - Retrieve Sentry issue information

### Troubleshooting
- Verify the Sentry MCP server installation at the specified path
- Check if the authentication token is valid and has proper permissions
- Ensure the Node.js environment is properly configured
- Consider reinstalling the Sentry MCP server package

---

## GitHub Cline Community MCP Server

### Configuration
```json
"github.com/cline/cline-community": {
  "autoApprove": [
    "preview_cline_issue"
  ],
  "timeout": 60,
  "type": "stdio",
  "command": "node",
  "args": [
    "/home/cis/mcp-servers/cline-community/build/index.js"
  ],
  "env": {
    "GH_TOKEN": "YOUR_GITHUB_TOKEN_HERE",
    "PATH": "/home/cis/mcp-servers/gh_2.40.0_linux_amd64/bin:$PATH"
  }
}
```

### Status
❌ **Not Configured** - Server not available

### Issue
The server is listed in configuration but reports as "not configured" when attempting to use it.

### Expected Tools
Based on configuration:
- `preview_cline_issue` - Preview GitHub issues

### Troubleshooting
- Check if the server file exists at the specified path
- Verify the GitHub token is valid and has proper permissions
- Ensure the GitHub CLI is properly installed and configured
- Check if the server build is complete and executable

---

## Supermemory MCP Server

### Configuration
```json
"github.com/supermemoryai/supermemory-mcp": {
  "disabled": false,
  "timeout": 60,
  "type": "stdio",
  "command": "node",
  "args": [
    "/home/cis/mcp-servers/supermemory-mcp-persistent.js"
  ],
  "env": {
    "SUPERMEMORY_API_KEY": "YOUR_SUPERMEMORY_API_KEY_HERE"
  },
  "autoApprove": [
    "tools/list",
    "addToSupermemory"
  ],
  "alwaysAllow": [
    "addToSupermemory"
  ]
}
```

### Status
✅ **Working** - Fully functional

### Working Features
- ✅ `addToSupermemory` - Successfully stores information in memory
- ✅ `searchSupermemory` - Successfully retrieves stored information

### Available Tools

#### addToSupermemory
**Purpose**: Store user information, preferences, and behaviors in memory

**Parameters**:
- `thingToRemember` (required): The information to store in memory

**Example Usage**:
```xml
<use_mcp_tool>
<server_name>github.com/supermemoryai/supermemory-mcp</server_name>
<tool_name>addToSupermemory</tool_name>
<arguments>
{
  "thingToRemember": "User prefers Python over JavaScript for backend development"
}
</arguments>
</use_mcp_tool>
```

**Response**: `Memory added successfully: "User prefers Python over JavaScript for backend development"`

#### searchSupermemory
**Purpose**: Search user memories and patterns using semantic matching

**Parameters**:
- `informationToGet` (required): What information to search for in memories

**Example Usage**:
```xml
<use_mcp_tool>
<server_name>github.com/supermemoryai/supermemory-mcp</server_name>
<tool_name>searchSupermemory</tool_name>
<arguments>
{
  "informationToGet": "programming language preferences"
}
</arguments>
</use_mcp_tool>
```

**Response**: Returns relevant memories matching the search query

### Use Cases
- Store user preferences and behaviors
- Remember project-specific decisions
- Maintain context across conversations
- Search for previously stored information
- Build knowledge base about user patterns

---

## Usage Recommendations

### Primary Working Server
**Supermemory MCP Server** is currently the only fully functional server and should be used for:
- Storing important information during development
- Maintaining context across sessions
- Remembering user preferences and decisions
- Building a knowledge base about the project

### Secondary Potential Server
**Serena MCP Server** has potential if the language server issues can be resolved:
- Excellent for code analysis and refactoring
- Provides comprehensive file operations
- Includes memory management capabilities
- Offers workflow management tools

### Servers Requiring Attention
1. **Filesystem MCP Server** - Check package installation and configuration
2. **Sentry MCP Server** - Verify authentication and server installation
3. **GitHub Cline Community MCP Server** - Check server configuration and GitHub token

### Recommended Actions

#### Immediate
1. **Fix Serena Language Server Issues**:
   - Check Python environment
   - Verify LSP dependencies
   - Consider reinstalling the Serena server

2. **Verify Filesystem Server Installation**:
   - Check if `@modelcontextprotocol/server-filesystem` is installed
   - Verify npm/npx configuration
   - Test with simple file operations

#### Medium Term
1. **Fix Sentry Server**:
   - Verify authentication token
   - Check server installation path
   - Test Sentry API connectivity

2. **Configure GitHub Cline Server**:
   - Verify server file exists
   - Check GitHub token permissions
   - Ensure GitHub CLI is properly configured

### Best Practices

#### When Using Supermemory
- Store meaningful, searchable information
- Use descriptive memory content
- Search using relevant keywords
- Build a comprehensive knowledge base over time

#### When Serena is Fixed
- Use semantic tools for code analysis
- Leverage symbolic operations for precise modifications
- Utilize memory features for project context
- Follow the workflow tools for systematic development

#### General MCP Usage
- Always check server status before use
- Handle errors gracefully
- Use appropriate tools for specific tasks
- Maintain consistent usage patterns

---

## Conclusion

Currently, only the **Supermemory MCP Server** is fully functional and provides reliable memory storage and retrieval capabilities. The **Serena MCP Server** shows promise but requires language server troubleshooting. The remaining servers (Filesystem, Sentry, and GitHub Cline Community) need configuration or installation fixes before they can be used effectively.

For immediate productivity, focus on using Supermemory for memory management while working on resolving the issues with the other servers. Once Serena is fixed, it will provide the most comprehensive development environment with its extensive set of code analysis and modification tools.