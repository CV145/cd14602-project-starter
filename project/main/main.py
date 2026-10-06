"""Main entry point delegating execution to the CLI frontend."""

import sys

import cli_frontend


def main() -> None:
    """Delegate CLI execution and forward exit status to operating system."""
    sys.exit(cli_frontend.main(sys.argv[1:]))

    # Edge Cases: Forwards all CLI arguments and handles status exit codes.
    # Security Vulnerabilities: None.


if __name__ == "__main__":
    main()
