#!/usr/bin/env python3
import subprocess
import re

# Get all routes from Flask
result = subprocess.run(['flask', 'routes'], capture_output=True, text=True)
print("Available Flask Routes:")
print("=" * 80)
print(result.stdout)
