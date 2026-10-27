---
name: context-keeper
description: Maintain a concise and accurate summary of project architecture, goals, implementation status, and next tasks.
---

# Context Keeper Skill

Maintain a compact, accurate and up-to-date project context
in `.context.md` at the workspace root.

## Guidelines

1. If `.context.md` does not exist, create it.

2. Keep the document under 100 lines.

3. Include these sections:

### Project Goal
A single sentence explaining TimeLens.

### Tech Stack
Languages, frameworks, AI models, and major dependencies.

### Architecture
Brief explanation of the application structure.

### Core Files
Important files and their responsibilities.

### Current Implementation Status
Only verified completed features.

### Current Focus / TODO
Immediate development tasks.

### Known Issues
Unresolved problems affecting development or demonstration.

4. Update `.context.md` whenever a major component
is created, modified, or removed.

5. Do not duplicate detailed code documentation.

6. Never include secrets, API keys, credentials,
private image contents, or sensitive configuration.

7. Do not mark features complete without verification.

8. At the end of each task where the file is modified,
include:

> **Context Synced:** `.context.md` updated and complete.

