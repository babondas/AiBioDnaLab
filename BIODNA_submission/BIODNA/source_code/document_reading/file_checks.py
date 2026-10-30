"""Checks 1-3: run before a file is opened."""
from source_code.common import config
from source_code.common import user_messages as messages
from source_code.common.custom_errors import FileReadingError


def check_format_is_supported(extension):
    if extension not in config.SUPPORTED_EXTENSIONS:
        reason = messages.UNSUPPORTED_MESSAGES.get(extension, messages.UNKNOWN_FORMAT)
        raise FileReadingError(reason + " " + messages.SUPPORTED_LIST)


def check_file_has_content(file_bytes):
    if len(file_bytes) == 0:
        raise FileReadingError(messages.FILE_IS_EMPTY)


def check_size_is_within_limit(file_bytes):
    max_bytes = config.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise FileReadingError(messages.FILE_TOO_LARGE)
