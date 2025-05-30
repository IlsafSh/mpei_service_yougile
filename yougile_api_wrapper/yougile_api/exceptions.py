"""
Исключения для работы с YouGile API.
"""

class YouGileApiError(Exception):
    """Базовое исключение для ошибок API."""
    pass

class YouGileAuthError(YouGileApiError):
    """Исключение для ошибок аутентификации."""
    pass

class YouGileNotFoundError(YouGileApiError):
    """Исключение для случаев, когда ресурс не найден."""
    pass

class YouGileValidationError(YouGileApiError):
    """Исключение для ошибок валидации данных."""
    pass
