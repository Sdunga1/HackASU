import sys
from . import server
from .server import run

def main():
    try:
        run()
    except KeyboardInterrupt:
        print("\nShutting down Jira MCP Server...")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

