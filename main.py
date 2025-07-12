#!/usr/bin/env python3
"""
4x10 Schedule Manager - Main Entry Point
"""

import sys
import os

sys.path.append(os.path.dirname(__file__))

from app.views.server import main

if __name__ == "__main__":
    main()
