"""
------------------------------------------------------------
YouGile API Client - Исключения
------------------------------------------------------------
Модуль содержит исключения, используемые в обертке YouGile API
------------------------------------------------------------
"""

class YouGileAPIError(Exception):
    """Базовое исключение для ошибок API YouGile"""
    pass

class YouGileAuthError(YouGileAPIError):
    """Ошибка авторизации в API YouGile"""
    pass

class YouGileRequestError(YouGileAPIError):
    """Ошибка запроса к API YouGile"""
    pass

class YouGileResponseError(YouGileAPIError):
    """Ошибка в ответе API YouGile"""
    pass
