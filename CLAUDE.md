# CLAUDE.md - AI Assistant Guide for DatacenterDatabase

**Last Updated**: 2026-01-19
**Repository**: fergar369/datacenterdatabase
**Status**: Initial setup

## Overview

This document provides comprehensive guidance for AI assistants (like Claude) working on the DatacenterDatabase project. It covers codebase structure, development workflows, conventions, and best practices.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Codebase Structure](#codebase-structure)
3. [Development Workflow](#development-workflow)
4. [Coding Conventions](#coding-conventions)
5. [Git Workflow](#git-workflow)
6. [Testing Guidelines](#testing-guidelines)
7. [Common Tasks](#common-tasks)
8. [AI Assistant Guidelines](#ai-assistant-guidelines)
9. [Troubleshooting](#troubleshooting)

---

## Project Overview

**DatacenterDatabase** - A database management system for datacenter infrastructure.

### Technology Stack
- **Language**: [To be determined based on first implementation]
- **Framework**: [To be determined]
- **Database**: [To be determined]
- **Testing**: [To be determined]

### Project Goals
- [To be documented as project evolves]

---

## Codebase Structure

*Note: This section will be updated as the project structure is established.*

### Current Structure
```
datacenterdatabase/
├── CLAUDE.md           # This file - AI assistant guide
└── .git/              # Git repository metadata
```

### Planned Structure (Template)
```
datacenterdatabase/
├── src/               # Source code
│   ├── models/        # Data models
│   ├── controllers/   # Business logic
│   ├── services/      # Service layer
│   ├── utils/         # Utility functions
│   └── config/        # Configuration files
├── tests/             # Test files
│   ├── unit/          # Unit tests
│   ├── integration/   # Integration tests
│   └── fixtures/      # Test fixtures
├── docs/              # Documentation
├── scripts/           # Build and deployment scripts
├── .gitignore         # Git ignore rules
├── README.md          # Project documentation
├── CLAUDE.md          # This file
└── package.json       # Dependencies (if Node.js)
```

### Key Directories
*To be documented as they are created*

### Important Files
- **CLAUDE.md**: This file - comprehensive guide for AI assistants
- **README.md**: User-facing project documentation (to be created)

---

## Development Workflow

### Setting Up Development Environment

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd datacenterdatabase
   ```

2. **Install dependencies**
   ```bash
   # To be documented once technology stack is chosen
   ```

3. **Configure environment**
   ```bash
   # To be documented once configuration is needed
   ```

### Before Making Changes

1. **Always fetch latest changes**
   ```bash
   git fetch origin
   ```

2. **Create or switch to feature branch**
   ```bash
   git checkout -b claude/<descriptive-branch-name>-<session-id>
   ```

3. **Review existing code** before making modifications
   - Read files thoroughly before editing
   - Understand the current implementation
   - Check for existing patterns and conventions

### Making Changes

1. **Follow the principle of least change**
   - Only modify what's necessary
   - Avoid refactoring unrelated code
   - Don't add features beyond the request

2. **Write clean, maintainable code**
   - Follow established patterns in the codebase
   - Add comments only where logic isn't self-evident
   - Keep functions focused and small

3. **Test your changes**
   - Run existing tests
   - Add new tests for new functionality
   - Verify manually if applicable

### After Making Changes

1. **Review your changes**
   ```bash
   git status
   git diff
   ```

2. **Commit with clear messages**
   ```bash
   git add <files>
   git commit -m "Brief description of changes"
   ```

3. **Push to remote**
   ```bash
   git push -u origin <branch-name>
   ```

---

## Coding Conventions

### General Principles

1. **Simplicity over cleverness**
   - Write straightforward code
   - Avoid premature optimization
   - Don't add abstractions until needed

2. **Consistency**
   - Follow existing code style
   - Match naming conventions used in the project
   - Maintain consistent file structure

3. **Security first**
   - Never commit secrets or credentials
   - Validate input at system boundaries
   - Follow OWASP guidelines for web applications
   - Avoid common vulnerabilities (XSS, SQL injection, etc.)

### Naming Conventions

*To be documented based on chosen language/framework*

### Code Style

*To be documented based on chosen language/framework*

### Comments and Documentation

- **DO**: Comment complex algorithms or business logic
- **DO**: Document public APIs and interfaces
- **DON'T**: Comment obvious code
- **DON'T**: Leave commented-out code
- **DON'T**: Add TODO comments without tickets

---

## Git Workflow

### Branch Naming

AI assistants should use branches in this format:
```
claude/<feature-description>-<session-id>
```

Example: `claude/add-user-auth-abc123xyz`

### Commit Messages

Follow this format:
```
<type>: <brief description>

<optional detailed explanation>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `docs`: Documentation changes
- `chore`: Maintenance tasks
- `style`: Code style changes (formatting, etc.)

**Examples**:
```
feat: add user authentication system

Implements JWT-based authentication with refresh tokens.
Includes login, logout, and token validation endpoints.
```

```
fix: resolve database connection timeout

Increased connection pool size and added retry logic.
```

### Push Protocol

- Always use: `git push -u origin <branch-name>`
- Branch must start with `claude/` and end with session ID
- Retry on network failures: up to 4 times with exponential backoff (2s, 4s, 8s, 16s)

### Pull Request Guidelines

When creating PRs:
1. Include a clear description of changes
2. Reference any related issues
3. Ensure all tests pass
4. Request review if needed

---

## Testing Guidelines

*To be documented once testing framework is established*

### Running Tests
```bash
# To be documented
```

### Writing Tests
- Test public interfaces, not implementation details
- Use descriptive test names
- Follow AAA pattern: Arrange, Act, Assert
- Keep tests isolated and independent

### Test Coverage
- Aim for high coverage on business logic
- Don't test framework code
- Focus on edge cases and error conditions

---

## Common Tasks

### Adding a New Feature

1. Read relevant existing code
2. Plan the implementation (use TodoWrite tool)
3. Write the code following conventions
4. Add tests
5. Update documentation if needed
6. Commit and push

### Fixing a Bug

1. Reproduce the issue
2. Locate the problematic code
3. Understand the root cause
4. Fix the issue
5. Add regression test
6. Commit with clear message

### Refactoring Code

1. Only refactor when explicitly requested
2. Ensure tests pass before and after
3. Make incremental changes
4. Don't change behavior

---

## AI Assistant Guidelines

### Core Principles

1. **Read before writing**
   - Always read files before modifying them
   - Understand existing patterns and conventions
   - Never guess at implementation details

2. **Use appropriate tools**
   - Use Read/Edit/Write for file operations
   - Use Task tool for exploratory work
   - Use TodoWrite for task planning and tracking
   - Avoid Bash for file operations

3. **Be thorough but focused**
   - Complete the requested task fully
   - Don't add unrequested features
   - Don't over-engineer solutions

4. **Communicate clearly**
   - Explain what you're doing
   - Ask questions when requirements are unclear
   - Report issues immediately

### Task Management

**ALWAYS use TodoWrite for:**
- Multi-step tasks (3+ steps)
- Complex implementations
- Multiple related changes
- User-requested todo lists

**Todo workflow:**
1. Create todos at start of task
2. Mark ONE task as in_progress before starting
3. Complete current task before starting next
4. Update todos immediately after finishing each task

### File Operations

**DO**:
- Use Read tool to read files
- Use Edit tool for precise modifications
- Use Write tool only for new files
- Preserve exact indentation and formatting

**DON'T**:
- Use cat, grep, sed, awk via Bash for file operations
- Create new files when editing existing ones works
- Modify files you haven't read

### Code Modifications

**DO**:
- Read the entire file context before editing
- Preserve existing code style
- Follow established patterns
- Test changes thoroughly

**DON'T**:
- Add features beyond the request
- Refactor unrelated code
- Add unnecessary comments or docstrings
- Over-engineer simple solutions

### Security Awareness

**Always check for:**
- Hardcoded secrets or credentials
- SQL injection vulnerabilities
- XSS vulnerabilities
- Command injection risks
- Insecure file operations
- Improper input validation

**If you introduce a security issue:**
- Fix it immediately
- Don't wait for review
- Explain what was wrong

### Error Handling

**When errors occur:**
1. Read the error message carefully
2. Understand the root cause
3. Fix the underlying issue
4. Don't just suppress the error
5. Test the fix

**Don't:**
- Add generic try-catch blocks without understanding why
- Suppress errors silently
- Add error handling for impossible scenarios

### Git Operations

**DO**:
- Commit with clear, descriptive messages
- Push using: `git push -u origin <branch>`
- Verify branch name matches requirements
- Check git status after operations

**DON'T**:
- Use --force without explicit permission
- Push to wrong branches
- Skip commit hooks
- Commit sensitive data

### Performance Considerations

**DO**:
- Run multiple independent tool calls in parallel
- Use specialized agents (Explore, Plan) when appropriate
- Cache results when beneficial

**DON'T**:
- Run sequential calls when parallel is possible
- Re-read files unnecessarily
- Perform redundant searches

---

## Troubleshooting

### Common Issues

#### "File not found" errors
- Verify the path is absolute, not relative
- Check if file exists with `ls -la`
- Ensure you're in the correct directory

#### Git push failures
- Verify branch name starts with `claude/`
- Check network connection
- Retry with exponential backoff
- Ensure you're pushing to the correct branch

#### Test failures
- Read the test output carefully
- Check recent changes
- Verify dependencies are installed
- Look for environment-specific issues

#### Build failures
- Check error messages for root cause
- Verify all dependencies are installed
- Clear cache/build artifacts
- Check for syntax errors

### Getting Help

- Review this CLAUDE.md file
- Check README.md for project-specific info
- Review existing code for patterns
- Ask clarifying questions when needed

---

## Updating This Document

This CLAUDE.md should be updated when:
- Project structure changes significantly
- New conventions are established
- New tools or frameworks are added
- Common patterns emerge
- AI assistants encounter recurring issues

**To update:**
1. Read the current version
2. Make targeted changes
3. Update "Last Updated" date
4. Commit with message: `docs: update CLAUDE.md`

---

## Quick Reference

### Essential Commands

```bash
# Check status
git status
git log --oneline -10

# Create branch
git checkout -b claude/<description>-<session-id>

# Stage and commit
git add <files>
git commit -m "type: description"

# Push changes
git push -u origin <branch-name>

# Run tests (to be documented)
# npm test

# Build project (to be documented)
# npm run build
```

### Essential File Paths

- **This file**: `/home/user/datacenterdatabase/CLAUDE.md`
- **Root directory**: `/home/user/datacenterdatabase/`

### Key Reminders

- ✓ Always read before editing
- ✓ Use TodoWrite for multi-step tasks
- ✓ Test all changes
- ✓ Commit with clear messages
- ✓ Push to correct branch
- ✗ Don't add unrequested features
- ✗ Don't refactor unnecessarily
- ✗ Don't commit secrets
- ✗ Don't skip reading files

---

*This document is a living guide and should evolve with the project.*
