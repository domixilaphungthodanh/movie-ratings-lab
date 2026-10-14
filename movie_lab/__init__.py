"""Movie ratings database learning project."""
import os
import sys
if os.name == 'nt':
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
