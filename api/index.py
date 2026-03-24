import os
import sys

# Ensure the root directory is in the python path so it can find question_generator
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from question_generator.api_server import app
