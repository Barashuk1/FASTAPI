import sys
import os

sys.path.append(os.path.abspath('..'))
project = 'PhotoShare'
copyright = '2024, P.O.N.D.A.M 2'
author = 'P.O.N.D.A.M 2'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx_autodoc_typehints',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'nature'
html_static_path = ['_static']
