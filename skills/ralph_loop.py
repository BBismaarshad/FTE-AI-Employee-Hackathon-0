"""
Ralph Wiggum Loop - Gold Tier AI Employee Skill

Autonomous multi-step task completion loop that keeps the AI working
until a task is fully complete.

Two completion strategies:
1. Promise-based: AI outputs a completion promise tag
2. File-movement: Task file moves to /Done folder

Named after Ralph Wiggum's "I'm helping!" persistence.

Part of the Gold Tier requirements for the FTE AI Employee Hackathon.
"""

import os
import sys
import subprocess
import argparse
import logging
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List


class RalphLoop:
    """Autonomous task completion loop with persistence."""

    def __init__(self, vault_path: str, command: str = 'claude', max_iterations: int = 10):
        """
        Initialize Ralph Loop.

        Args:
            vault_path: Path to Obsidian vault
            command: AI command to execute (claude, qwen, etc.)
            max_iterations: Maximum loop iterations before giving up
        """
        self.vault_path = Path(vault_path)
        self.command = command
        self.max_iterations = max_iterations
        self.logger = logging.getLogger('RalphLoop')

        # Vault folders
        self.needs_action = self.vault_path / 'Needs_Action'
        self.done_folder = self.vault_path / 'Done'
        self.logs_folder = self.vault_path / 'Logs'
        self.state_folder = self.vault_path / '.ralph_state'

        # Create folders
        for folder in [self.state_folder, self.logs_folder]:
            folder.mkdir(parents=True, exist_ok=True)

    def run_promise_loop(self, prompt: str, promise: str, context: str = None) -> bool:
        """
        Run loop until AI outputs the completion promise.

        Args:
            prompt: Initial task prompt
            promise: Completion promise string to look for (e.g., "TASK_COMPLETE")
            context: Optional additional context

        Returns:
            True if task completed, False if max iterations reached
        """
        self.logger.info(f"🔄 Starting Ralph Loop (promise-based)")
        self.logger.info(f"📋 Task: {prompt[:100]}...")
        self.logger.info(f"🎯 Looking for promise: {promise}")

        current_prompt = prompt
        if context:
            current_prompt = f"{context}\n\n{prompt}"

        for iteration in range(1, self.max_iterations + 1):
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"🔁 Iteration {iteration}/{self.max_iterations}")
            self.logger.info(f"{'='*60}")

            # Execute AI command
            try:
                result = self._execute_command(current_prompt)

                if result['success']:
                    output = result['output']

                    # Check for completion promise
                    if promise in output or f"<promise>{promise}</promise>" in output:
                        self.logger.info(f"✅ Promise '{promise}' found! Task complete.")
                        self._log_completion(prompt, iteration, 'promise_found')
                        return True

                    # Task not complete, prepare next iteration
                    self.logger.info("⏳ Promise not found. Continuing...")

                    # Feed output back as context for next iteration
                    current_prompt = self._build_continuation_prompt(prompt, output, iteration)

                else:
                    self.logger.error(f"❌ Command failed: {result.get('error')}")
                    # Continue anyway, AI might recover

            except Exception as e:
                self.logger.error(f"❌ Iteration {iteration} failed: {e}")

            # Small delay between iterations
            time.sleep(2)

        # Max iterations reached
        self.logger.warning(f"⚠️  Max iterations ({self.max_iterations}) reached without completion")
        self._log_completion(prompt, self.max_iterations, 'max_iterations')
        return False

    def run_file_movement_loop(self, task_file: Path, prompt: str = None) -> bool:
        """
        Run loop until task file moves to /Done folder.

        Args:
            task_file: Path to task file in Needs_Action
            prompt: Optional custom prompt (otherwise reads from file)

        Returns:
            True if task completed, False if max iterations reached
        """
        self.logger.info(f"🔄 Starting Ralph Loop (file-movement based)")
        self.logger.info(f"📄 Tracking file: {task_file.name}")

        if not task_file.exists():
            self.logger.error(f"❌ Task file not found: {task_file}")
            return False

        # Read prompt from file if not provided
        if not prompt:
            try:
                content = task_file.read_text(encoding='utf-8')
                prompt = f"Process the task in file: {task_file.name}\n\nContent:\n{content}"
            except Exception as e:
                self.logger.error(f"Failed to read task file: {e}")
                return False

        current_prompt = prompt

        for iteration in range(1, self.max_iterations + 1):
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"🔁 Iteration {iteration}/{self.max_iterations}")
            self.logger.info(f"{'='*60}")

            # Check if file moved to Done
            if not task_file.exists():
                # Check if it's in Done folder
                done_path = self.done_folder / task_file.name
                if done_path.exists():
                    self.logger.info(f"✅ Task file moved to Done! Task complete.")
                    self._log_completion(prompt, iteration, 'file_moved')
                    return True
                else:
                    self.logger.warning(f"⚠️  Task file disappeared but not in Done folder")

            # Execute AI command
            try:
                result = self._execute_command(current_prompt)

                if result['success']:
                    output = result['output']

                    # Check again if file moved
                    if not task_file.exists():
                        done_path = self.done_folder / task_file.name
                        if done_path.exists():
                            self.logger.info(f"✅ Task completed and moved to Done!")
                            self._log_completion(prompt, iteration, 'file_moved')
                            return True

                    # Prepare next iteration
                    current_prompt = self._build_continuation_prompt(
                        f"Continue working on: {task_file.name}",
                        output,
                        iteration
                    )

                else:
                    self.logger.error(f"❌ Command failed: {result.get('error')}")

            except Exception as e:
                self.logger.error(f"❌ Iteration {iteration} failed: {e}")

            time.sleep(2)

        self.logger.warning(f"⚠️  Max iterations reached without completion")
        self._log_completion(prompt, self.max_iterations, 'max_iterations')
        return False

    def _execute_command(self, prompt: str) -> Dict:
        """
        Execute the AI command with the given prompt.

        Args:
            prompt: Prompt to send to AI

        Returns:
            dict with success status and output
        """
        try:
            # Save prompt to temp file for complex prompts
            temp_prompt_file = self.state_folder / f"prompt_{int(time.time())}.txt"
            temp_prompt_file.write_text(prompt, encoding='utf-8')

            # Execute command
            # Note: Adjust command format based on your AI tool
            cmd = [self.command, '--prompt', prompt]

            self.logger.debug(f"Executing: {' '.join(cmd[:2])}...")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                encoding='utf-8'
            )

            # Clean up temp file
            temp_prompt_file.unlink(missing_ok=True)

            output = result.stdout if result.stdout else result.stderr

            return {
                'success': result.returncode == 0,
                'output': output,
                'error': result.stderr if result.returncode != 0 else None
            }

        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output': '',
                'error': 'Command timeout (5 minutes)'
            }
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'error': str(e)
            }

    def _build_continuation_prompt(self, original_task: str, previous_output: str, iteration: int) -> str:
        """
        Build prompt for next iteration with context.

        Args:
            original_task: Original task description
            previous_output: Output from previous iteration
            iteration: Current iteration number

        Returns:
            Prompt string for next iteration
        """
        # Truncate output if too long
        max_output_length = 2000
        if len(previous_output) > max_output_length:
            previous_output = previous_output[:max_output_length] + "\n...(truncated)"

        prompt = f"""Previous iteration output:
---
{previous_output}
---

The task is NOT yet complete. Continue working on:

{original_task}

This is iteration {iteration}. Keep working until the task is fully complete.
When done, output the completion promise or move the task file to /Done.
"""
        return prompt

    def _log_completion(self, task: str, iterations: int, completion_type: str):
        """Log task completion to daily log."""
        log_file = self.logs_folder / f"{datetime.now().strftime('%Y-%m-%d')}.json"

        entry = {
            "timestamp": datetime.now().isoformat(),
            "action_type": "ralph_loop_complete",
            "actor": "ralph_loop",
            "task": task[:200],
            "iterations": iterations,
            "completion_type": completion_type,
            "status": "success" if completion_type != "max_iterations" else "incomplete"
        }

        # Read existing logs
        logs = []
        if log_file.exists():
            try:
                logs = json.loads(log_file.read_text(encoding='utf-8'))
            except:
                logs = []

        logs.append(entry)
        log_file.write_text(json.dumps(logs, indent=2), encoding='utf-8')


def main():
    """CLI interface for Ralph Loop."""
    parser = argparse.ArgumentParser(
        description='Ralph Wiggum Loop - Autonomous Task Completion',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Promise-based loop
  python ralph_loop.py --vault ./AI_Employee_Vault --prompt "Fix all lint errors" --promise "LINT_FIXED"

  # File-movement loop
  python ralph_loop.py --vault ./AI_Employee_Vault --file ./AI_Employee_Vault/Needs_Action/TASK_123.md

  # Custom AI command
  python ralph_loop.py --vault ./AI_Employee_Vault --prompt "Deploy to production" --promise "DEPLOYED" --command qwen
        """
    )

    parser.add_argument('--vault', type=str, required=True, help='Path to Obsidian vault')
    parser.add_argument('--prompt', type=str, help='Task prompt')
    parser.add_argument('--promise', type=str, help='Completion promise string')
    parser.add_argument('--file', type=str, help='Task file to track (file-movement mode)')
    parser.add_argument('--command', type=str, default='claude', help='AI command to execute')
    parser.add_argument('--max-iterations', type=int, default=10, help='Maximum iterations')
    parser.add_argument('--context', type=str, help='Additional context for the task')

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Initialize Ralph Loop
    ralph = RalphLoop(
        vault_path=args.vault,
        command=args.command,
        max_iterations=args.max_iterations
    )

    # Determine mode and run
    if args.file:
        # File-movement mode
        task_file = Path(args.file)
        success = ralph.run_file_movement_loop(task_file, prompt=args.prompt)

    elif args.prompt and args.promise:
        # Promise-based mode
        success = ralph.run_promise_loop(args.prompt, args.promise, context=args.context)

    else:
        print("❌ Error: Must specify either --file OR (--prompt AND --promise)")
        parser.print_help()
        sys.exit(1)

    # Exit with appropriate code
    if success:
        print("\n✅ Task completed successfully!")
        sys.exit(0)
    else:
        print("\n⚠️  Task incomplete after max iterations")
        sys.exit(1)


if __name__ == '__main__':
    main()
