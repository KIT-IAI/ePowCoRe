import os
import sys

sys.path.append(os.path.dirname(__file__))

# Cleanup and create output directory for tests
if os.path.isdir("./tests/out"):
    os.rmdir("./tests/out")
os.mkdir("./tests/out")
