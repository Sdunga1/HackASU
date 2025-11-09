#!/usr/bin/env python3
"""Command-line interface for HackASU MCP Server."""

import sys
# Import server module to ensure all tools are registered
import server
from server import run

def main():
    """Main entry point for the CLI."""
    try:
        run()
    except KeyboardInterrupt:
        print("\nShutting down HackASU MCP Server...")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

