## The Industry-Standard Fof Branch Naming rules

The most effective pattern follows this structure:
`[category]/[issue-number]-[short-description]`

### 1. Dimension: Purpose (The Category)

Use a prefix to immediately signal the intent of the code change. This helps you and your teammate, R, quickly filter branches in the terminal or on GitHub.

* **`feature/`**: New functionality for your AI agent (e.g., `feature/llm-integration`).
* **`bugfix/`**: Fixing an error in existing code (e.g., `bugfix/connection-timeout`).
* **`hotfix/`**: Urgent fixes for the `main` branch that cannot wait for a standard release cycle.
* **`docs/`**: Updates to the README or project documentation.
* **`refactor/`**: Code changes that neither fix a bug nor add a feature, but improve code structure.

### 2. Dimension: Lifecycle (The Issue Number)

Since you are using **GitHub Projects**, always include the **Issue Number** directly in the branch name.

* **Example**: `feature/42-sql-injection-module`
* **Why**: It creates an unbreakable link between your management board (the Project) and your work (the Repository). When you search your Git history in six months, you can jump directly back to the project discussion for context.

### 3. Dimension: Features (The Description)

Keep descriptions lowercase, use hyphens (kebab-case) instead of spaces, and be concise.

* **Avoid**: `feature/working-on-the-thing-now`
* **Better**: `feature/12-prompt-template-validation`

---

## Implementation Summary

When you and R start a new task from your project board, the workflow should look like this:

| Dimension | Rule | Example |
| :--- | :--- | :--- |
| **Category** | Define the work type first. | `feature/` |
| **ID** | Reference the project issue. | `8-` |
| **Feature** | Use 2-4 descriptive keywords. | `agent-auth` |
| **Full Name** | **The Final Result** | **`feature/8-agent-auth`** |


