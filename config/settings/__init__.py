from .base import *
import socket
import re

# if re.match(r"ip-.*", socket.gethostname()):
#     from .production import *
# else:
#     from .local import *
from .local import *
