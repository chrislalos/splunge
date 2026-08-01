# stdlib import
import sys
# 3rd party import
import pytest
# relative imports
from . import rel
from . import rel2
from . import rel3

name="meat"
relName=rel.name
rel2Name=rel2.name
rel3Name=rel3.name

# importing rel4 should fail
try:
    from . import rel4
    rel4Name = rel4.name
except ImportError:
    rel4Name = "(neat!)"
