import logging

logger = logging.getLogger(__name__)

def raise_assertion_error(message, row, method):
    error = {
        "message": message,
        "row": row,
        "method": method
    }
    logger.error(str(error))
    raise AssertionError(error)