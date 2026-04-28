# Clean Code Standards & Best Practices

## 1. Naming Conventions
- Use meaningful, pronounceable, and intention-revealing names.
- **Variables & Functions**: `camelCase` (JS/Java) or `snake_case` (Python). Example: `getUserData()` or `get_user_data()`.
- **Classes**: `PascalCase`. Example: `UserProfile`, `ChatService`.
- **Constants**: `UPPER_SNAKE_CASE`. Example: `MAX_RETRY_COUNT`.
- Avoid magic numbers and obscure abbreviations.

## 2. Functions & Methods
- **Single Responsibility Principle (SRP)**: A function should do exactly one thing and do it well.
- **Keep them small**: Functions should ideally be short (under 20-30 lines).
- **Limit arguments**: Aim for 0-3 arguments. If more are needed, group them into an object or dictionary.
- **No side effects**: Functions shouldn't unexpectedly alter global state.

## 3. Error Handling
- Never ignore caught exceptions. Log them or handle them gracefully.
- Use explicit exception types instead of generic `Exception` where possible.
- Fail fast: Validate inputs at the start of functions to prevent deeper logic from breaking.

## 4. Code Structure & Formatting
- Avoid deep nesting (arrow code). Use guard clauses and early returns.
- Keep lines under 120 characters for readability.
- Maintain consistent indentation (e.g., 4 spaces or 2 spaces).
- Group related methods and variables logically within classes.

## 5. Comments & Documentation
- Code should explain *how* it works. Comments should explain *why* it works.
- Avoid redundant comments that just restate the code.
- Write docstrings for public classes and complex functions.
- Update comments alongside code modifications.

## 6. Performance & Efficiency
- Prefer built-in functions and optimized libraries over reinventing the wheel.
- Avoid expensive operations (e.g., database queries, network calls) inside tight loops.
- Use asynchronous operations for I/O bound tasks.

## 7. Security
- Never hardcode API keys, passwords, or secrets. Use environment variables.
- Sanitize and validate all user inputs to prevent SQL Injection and XSS.
- Apply the principle of least privilege.
