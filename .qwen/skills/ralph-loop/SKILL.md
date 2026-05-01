# Ralph Wiggum Loop - Agent Skill

**Tier:** Gold  
**Category:** Autonomous Task Completion  
**Status:** ✅ Ready

## Overview

Autonomous multi-step task completion loop that keeps the AI working until a task is fully complete. Named after Ralph Wiggum's persistent "I'm helping!" attitude. Prevents the "lazy agent" problem by continuously iterating until completion.

## Features

- 🔄 **Autonomous Iteration** - Keeps working until done
- 🎯 **Two Completion Modes** - Promise-based or file-movement
- 📊 **Progress Tracking** - Logs each iteration
- 🛡️ **Safety Limits** - Max iterations to prevent infinite loops
- 🔗 **Context Preservation** - Feeds previous output back
- 📝 **Audit Logging** - All iterations logged

## Installation

### Prerequisites

```bash
# No additional dependencies required
# Works with any AI command (claude, qwen, etc.)
```

### Verify Installation

```bash
python skills/ralph_loop.py --help
```

## Usage

### Promise-Based Mode

AI outputs a completion promise when done:

```bash
python skills/ralph_loop.py --vault .\AI_Employee_Vault --prompt "Fix all lint errors in the codebase" --promise "LINT_FIXED"
```

**How it works:**
1. AI receives prompt
2. AI works on task
3. AI outputs `<promise>LINT_FIXED</promise>` when complete
4. Loop detects promise and exits

### File-Movement Mode

Task completes when file moves to Done/:

```bash
python skills/ralph_loop.py --vault .\AI_Employee_Vault --file .\AI_Employee_Vault\Needs_Action\TASK_123.md
```

**How it works:**
1. AI receives task file
2. AI processes task
3. AI moves file to Done/ when complete
4. Loop detects file movement and exits

### Custom AI Command

```bash
# Use with different AI tools
python skills/ralph_loop.py --vault .\AI_Employee_Vault --prompt "Deploy to production" --promise "DEPLOYED" --command qwen

# Or with custom command
python skills/ralph_loop.py --vault .\AI_Employee_Vault --prompt "Run tests" --promise "TESTS_PASSED" --command "python run_ai.py"
```

### Max Iterations

```bash
# Set custom max iterations (default: 10)
python skills/ralph_loop.py --vault .\AI_Employee_Vault --prompt "Complex task" --promise "DONE" --max-iterations 20
```

## Completion Strategies

### 1. Promise-Based (Simple)

**Best for:** Well-defined tasks with clear completion criteria

**Example:**
```bash
python skills/ralph_loop.py --vault .\AI_Employee_Vault --prompt "Run all tests and fix failures" --promise "ALL_TESTS_PASS"
```

**AI should output:**
```
All tests are now passing!

<promise>ALL_TESTS_PASS</promise>
```

**Advantages:**
- Simple to implement
- Clear completion signal
- Works with any task

**Disadvantages:**
- AI must remember to output promise
- Can be forgotten in complex tasks

### 2. File-Movement (Advanced)

**Best for:** Workflow-integrated tasks

**Example:**
```bash
python skills/ralph_loop.py --vault .\AI_Employee_Vault --file .\AI_Employee_Vault\Needs_Action\EMAIL_urgent_client.md
```

**AI workflow:**
1. Read task file
2. Process task (reply to email)
3. Move file to Done/
4. Loop detects completion

**Advantages:**
- Natural workflow integration
- More reliable (file movement is explicit)
- Audit trail built-in

**Disadvantages:**
- Requires file-based workflow
- AI must understand file movement

## Configuration

### Context Addition

Add additional context to guide the AI:

```bash
python skills/ralph_loop.py --vault .\AI_Employee_Vault --prompt "Optimize database queries" --promise "OPTIMIZED" --context "Focus on the user authentication queries first"
```

### Custom Command Format

Modify the command execution in code:

```python
# Default format
cmd = [self.command, '--prompt', prompt]

# Custom format for your AI tool
cmd = [self.command, 'execute', '--task', prompt, '--output', 'json']
```

## Loop Behavior

### Iteration Flow

```
Iteration 1: Initial prompt
  ↓
AI works on task
  ↓
Check completion (promise or file)
  ↓
Not complete? → Build continuation prompt
  ↓
Iteration 2: Previous output + original task
  ↓
AI continues working
  ↓
Check completion
  ↓
Complete? → Exit with success
Not complete? → Continue loop
  ↓
Max iterations? → Exit with warning
```

### Continuation Prompt

Each iteration receives:
```
Previous iteration output:
---
[Previous AI output, truncated to 2000 chars]
---

The task is NOT yet complete. Continue working on:

[Original task]

This is iteration 3. Keep working until the task is fully complete.
When done, output the completion promise or move the task file to /Done.
```

### Safety Limits

- **Max iterations:** 10 (default), configurable
- **Command timeout:** 5 minutes per iteration
- **Output truncation:** 2000 chars for context
- **Delay between iterations:** 2 seconds

## Logging

All iterations logged to `Logs/YYYY-MM-DD.json`:

```json
{
  "timestamp": "2026-05-01T12:00:00",
  "action_type": "ralph_loop_complete",
  "actor": "ralph_loop",
  "task": "Fix all lint errors in the codebase",
  "iterations": 5,
  "completion_type": "promise_found",
  "status": "success"
}
```

## Integration

### With Orchestrator

```python
from skills.ralph_loop import RalphLoop

ralph = RalphLoop(vault_path='./AI_Employee_Vault', command='claude')

# Run promise-based loop
success = ralph.run_promise_loop(
    prompt="Process all pending emails",
    promise="EMAILS_PROCESSED"
)

if success:
    print("✅ Task completed!")
```

### With Task Files

```python
from pathlib import Path
from skills.ralph_loop import RalphLoop

ralph = RalphLoop(vault_path='./AI_Employee_Vault')

# Process all tasks in Needs_Action
for task_file in Path('./AI_Employee_Vault/Needs_Action').glob('*.md'):
    ralph.run_file_movement_loop(task_file)
```

### Scheduled Execution

```powershell
# Run daily task completion loop
schtasks /create /tn "AI_Employee_Ralph_Loop" /tr "python skills\ralph_loop.py --vault .\AI_Employee_Vault --file .\AI_Employee_Vault\Needs_Action\DAILY_TASKS.md" /sc daily /st 09:00
```

## Best Practices

### Task Design

**Good tasks for Ralph Loop:**
- Multi-step processes
- Tasks requiring verification
- Iterative improvements
- Error fixing loops

**Poor tasks for Ralph Loop:**
- Single-step actions
- Tasks requiring human input
- Ambiguous completion criteria

### Promise Design

**Good promises:**
- `TESTS_PASSED` - Clear, verifiable
- `DEPLOYMENT_COMPLETE` - Specific outcome
- `ALL_ERRORS_FIXED` - Measurable

**Poor promises:**
- `DONE` - Too generic
- `MAYBE_FINISHED` - Ambiguous
- `TASK_COMPLETE` - Not specific enough

### Iteration Limits

- **Simple tasks:** 5 iterations
- **Medium tasks:** 10 iterations (default)
- **Complex tasks:** 20 iterations
- **Very complex:** Consider breaking into subtasks

## Troubleshooting

### Issue: "Max iterations reached"

**Cause:** Task too complex or AI stuck

**Solution:**
1. Break task into smaller subtasks
2. Increase max iterations
3. Add more specific context
4. Check AI command is working

### Issue: "Command timeout"

**Cause:** AI taking too long per iteration

**Solution:**
1. Simplify the task
2. Check AI performance
3. Increase timeout in code

### Issue: "Promise not found"

**Cause:** AI not outputting promise

**Solution:**
1. Make promise more explicit in prompt
2. Use file-movement mode instead
3. Check AI output format

### Issue: "File not moving to Done"

**Cause:** AI not understanding workflow

**Solution:**
1. Add explicit instructions in task file
2. Check AI has file system access
3. Verify Done/ folder exists

## Advanced Usage

### Custom Completion Detection

Modify `_execute_command()` to add custom detection:

```python
def _execute_command(self, prompt):
    result = subprocess.run(...)
    
    # Custom completion detection
    if "CUSTOM_SIGNAL" in result.stdout:
        return {'success': True, 'complete': True, 'output': result.stdout}
    
    return {'success': True, 'complete': False, 'output': result.stdout}
```

### Multi-Task Loop

```python
# Process multiple tasks in sequence
tasks = [
    ("Fix lint errors", "LINT_FIXED"),
    ("Run tests", "TESTS_PASSED"),
    ("Deploy", "DEPLOYED")
]

for prompt, promise in tasks:
    success = ralph.run_promise_loop(prompt, promise)
    if not success:
        print(f"Failed: {prompt}")
        break
```

### Conditional Continuation

```python
# Add conditions for continuation
def should_continue(iteration, output):
    if "CRITICAL_ERROR" in output:
        return False
    if iteration > 5 and "progress" not in output.lower():
        return False
    return True
```

## Performance Considerations

### Iteration Cost

- Each iteration = 1 AI call
- 10 iterations = 10 AI calls
- Consider API costs for long loops

### Context Window

- Previous output truncated to 2000 chars
- Prevents context overflow
- Adjust if needed for your AI

### Timeout Management

- 5 minute timeout per iteration
- Total time = iterations × timeout
- 10 iterations = up to 50 minutes

## Security Notes

- ⚠️ **Command Injection:** Validate prompts
- ✅ **Timeout Protection:** Prevents infinite runs
- 📝 **Audit Logging:** All iterations logged
- 🔒 **Iteration Limits:** Prevents runaway loops

## Related Skills

- **Orchestrator** - Triggers Ralph Loops
- **Weekly Audit** - Analyzes loop performance
- **All Skills** - Can be wrapped in Ralph Loop

## Support

- 📚 **Documentation:** This file
- 🐛 **Issues:** Check logs in Logs/ folder
- 💬 **Community:** Wednesday Research Meetings

## References

- [Ralph Wiggum Pattern](https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum)
- Original concept from Claude Code documentation

---

**Built for Gold Tier - FTE AI Employee Hackathon**  
**Enables true autonomous multi-step task completion**
