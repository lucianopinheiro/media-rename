"""Entry point for ``python -m src``.

Delegates to :func:`App.main`, so the package can be launched from the project
root without changing the working directory.
"""

from .app import main

if __name__ == "__main__":
    main()
