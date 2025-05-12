# Create a debug.py file at the root of your project
import sys
print(f"Python version: {sys.version}")
print("Python path:")
for path in sys.path:
    print(f"  - {path}")
    