# Reasoning Scaffold: Plan -> Execute -> Verify -> Report

Follow this structured reasoning loop for every task to ensure 100% reliability.

### 1. Plan
- **Discovery**: Use your discovery tools (Grep/Read/Glob) to map the territory.
- **Decomposition**: Break the goal into small, actionable steps.
- **Hypothesis**: State your assumptions and expected outcomes.
- **Update**: Write your plan to the todo list using `todo_write`.

### 2. Execute
- **Implementation**: Perform the implementation using targeted, surgical tools.
- **Conventions**: Adhere to the project's style, naming, and architecture.
- **Safety**: Never hardcode secrets; prioritize error handling and guard clauses.

### 3. Verify
- **Automated Testing**: Run existing tests or write new ones to verify the change.
- **Manual Smoke Test**: Ping endpoints or check UI state if applicable.
- **Artifact Review**: Verify that all files were written/modified as expected.

### 4. Report
- **Headline Summary**: Start with a concise confirmation of the goal's status.
- **Impact Analysis**: List key changes and their effect on the system.
- **Next Steps**: Propose any necessary follow-up actions or optimizations.
