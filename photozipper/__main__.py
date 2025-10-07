"""Entry point for running photozipper as a module.

Allows running with: python -m photozipper
"""

import sys
from photozipper.cli import main

if __name__ == '__main__':
    sys.exit(main())
