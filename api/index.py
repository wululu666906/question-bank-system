import os
import sys

# Ensure the root directory and question_generator directory are in the python path
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, base_dir)
sys.path.insert(0, os.path.join(base_dir, 'question_generator'))

from question_generator.api_server import app
