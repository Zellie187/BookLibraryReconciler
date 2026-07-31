import logging
from pathlib import Path


def setup_logger(log_folder):

    Path(log_folder).mkdir(exist_ok=True)

    logging.basicConfig(
        filename=Path(log_folder) / "library.log",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    return logging.getLogger("BookLibrary")
