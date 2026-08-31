import logging
from rich.logging import RichHandler
from rich.console import Console

console = Console()

def setup_logger(name: str = "k8s-guard", level: str = "INFO"):
    """Setup rich logger"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
    )
    return logging.getLogger(name)

logger = setup_logger()
