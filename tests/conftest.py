# -*- coding: utf-8 -*-
import sys
from pathlib import Path

# Add package root to sys.path
package_root = Path(__file__).resolve().parent.parent
if str(package_root) not in sys.path:
    sys.path.insert(0, str(package_root))
