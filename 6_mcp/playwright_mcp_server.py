#!/usr/bin/env python3
"""
Wrapper script for Playwright MCP server that properly handles initialization timing.
This script starts the npx process and ensures it's ready before MCPServerStdio connects.
"""
import sys
import subprocess
import time
import os

# Start the npx process
process = subprocess.Popen(
    ['/usr/local/bin/npx', '@playwright/mcp@latest'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    env=os.environ.copy()
)

# Give the server time to initialize
time.sleep(1)

# Pass through stdin/stdout/stderr
try:
    # Forward stdin to the process
    if sys.stdin.isatty():
        # If running interactively, just wait
        process.wait()
    else:
        # If running as a subprocess, forward data
        import shutil
        shutil.copyfileobj(sys.stdin, process.stdin)
        process.stdin.close()
        
        # Forward stdout
        shutil.copyfileobj(process.stdout, sys.stdout)
        process.stdout.close()
        
        # Forward stderr
        shutil.copyfileobj(process.stderr, sys.stderr)
        process.stderr.close()
        
        process.wait()
except KeyboardInterrupt:
    process.terminate()
    process.wait()
    sys.exit(0)

sys.exit(process.returncode)

