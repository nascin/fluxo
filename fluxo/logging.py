import logging
from fluxo import fluxo_core

logging.basicConfig(
    format='%(asctime)s - %(levelname)s ===> %(message)s',
    datefmt='%Y/%m/%d %H:%M:%S',
    level=logging.INFO
)

logger = logging.getLogger(fluxo_core.__name__)