# Gemini CLI Execution Prompt

Use this prompt to have Gemini CLI execute the implementation plan in agent mode.

---

## Prompt for Gemini CLI

```
I need you to implement the career scraper notification system following the detailed plan in docs/plans/2026-01-05-career-scraper-notification-system.md.

Execute the plan task-by-task using Test-Driven Development (TDD):

1. Start with Phase 1, Task 1
2. For each task:
   - Read the task requirements carefully
   - Write the failing test FIRST (as specified in the plan)
   - Run the test to verify it fails
   - Implement the minimal code to make it pass
   - Run the test again to verify it passes
   - Commit with the suggested commit message
   - Show me the results and WAIT for my approval before proceeding

3. After each task completion:
   - Summarize what was accomplished
   - Show test results
   - Show git commit hash
   - Ask: "Task N complete. Proceed to Task N+1? (yes/no)"

4. If any test fails or error occurs:
   - Stop immediately
   - Show me the full error
   - Suggest fixes
   - Wait for my decision

Key constraints:
- Follow the exact file paths and code from the plan
- Use the tech stack specified (Python 3.12, Playwright, Pydantic, etc.)
- Maintain test coverage above 80%
- Do not skip ahead - execute in order
- Do not deviate from the plan unless I approve changes

The GEMINI.md file in the project root contains additional context about the project architecture, coding standards, and troubleshooting tips.

Ready to start with Phase 1, Task 1?
```

---

## How to Use with Gemini CLI

### Option 1: Interactive Agent Mode (Recommended)
```bash
cd /path/to/employment-whats-that
gemini-cli
```

Then paste the prompt above in the Gemini CLI agent chat.

### Option 2: Direct Command
```bash
gemini-cli chat --agent "Implement the plan in docs/plans/2026-01-05-career-scraper-notification-system.md task-by-task using TDD. Wait for approval between tasks."
```

### Option 3: VS Code Gemini Code Assist
1. Open project in VS Code
2. Click Gemini Code Assist in activity bar
3. Select "Agent" tab
4. Paste the prompt above
5. Click "Start Agent"

---

## Monitoring Progress

The agent will:
- Create files as specified in the plan
- Run pytest tests automatically
- Make git commits after each task
- Show you diffs before applying changes
- Wait for your approval between tasks

You can check progress at any time:
```bash
# View current task status
git log --oneline -10

# Check test coverage
pytest backend/tests --cov=backend/src --cov-report=term-missing

# See what files were created
git status
```

---

## If Execution Stops

Resume from where it left off:
```bash
gemini-cli chat --agent "Continue implementation from the last completed task. Review the git log to see what's been done, then proceed with the next task in the plan."
```

---

## References
- [Gemini CLI Documentation](https://developers.google.com/gemini-code-assist/docs/gemini-cli)
- [Agent Mode Guide](https://developers.google.com/gemini-code-assist/docs/use-agentic-chat-pair-programmer)
- [GEMINI.md Context Files](https://google-gemini.github.io/gemini-cli/docs/cli/gemini-md.html)
