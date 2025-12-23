#!/bin/bash
# Wrapper script for Playwright MCP server that adds a delay
# to ensure the server is ready before MCPServerStdio tries to connect

# Increase delay to give server more time to initialize
sleep 2
exec /usr/local/bin/npx @playwright/mcp@latest "$@"

