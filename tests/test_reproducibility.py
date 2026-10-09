"""
Golden Reproducibility Test Suite for GeoSmart Price AI
Verifies exact 544-D Multimodal Feature Vector assembly, XGBoost regression,
and TreeSHAP explainability across clean machine installations.
"""

import os
import sys

# Ensure backend directory is in python path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, os.path.abspath(backend_dir))

from tests.test_reproducibility import *  # noqa
