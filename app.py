"""
Little wrapper to kick off web interface
"""

import os
from svbtle_subscriber import run_web


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    run_web(host='0.0.0.0', port=port)
