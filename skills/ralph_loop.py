"""
Ralph Wiggum Loop - Autonomous multi-step task completion.

Usage:
    python skills/ralph_loop.py --prompt "Fix all lint errors" --promise "LINT_FIXED"

This script will keep calling the AI agent until:
1. The AI outputs the completion promise
2. A file is moved to /Done (advanced)
3. Max iterations reached
"""

import os
import sys
import subprocess
import argparse
import logging
import time

def run_loop(prompt, promise, max_iterations=5, command='qwen'):
    """Run the autonomous loop."""
    logger = logging.getLogger('RalphLoop')
    logger.info(f"Starting Ralph Loop with prompt: {prompt}")
    
    current_prompt = prompt
    
    for i in range(max_iterations):
        logger.info(f"Iteration {i+1}/{max_iterations}")
        
        result = subprocess.run(
            [command, '--prompt', current_prompt],
            capture_output=True,
            text=True
        )
        
        output = result.stdout
        logger.info(f"Output received: {output[:100]}...")
        
        if promise in output:
            logger.info(f"Promise '{promise}' found! Task complete.")
            return True
        
        # If not complete, we feed the output back as context
        current_prompt = f"Previous output was:\n{output}\n\nTask not complete yet. Continue working on: {prompt}"
        
        # Small delay to avoid hammering
        time.sleep(2)
        
    logger.warning("Max iterations reached without finding promise.")
    return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--prompt', type=str, required=True)
    parser.add_argument('--promise', type=str, required=True)
    parser.add_argument('--max', type=int, default=5)
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    run_loop(args.prompt, args.promise, args.max)
