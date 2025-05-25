"""
------------------------------------------------------------
YouGile API Client
------------------------------------------------------------
Библиотека для работы с REST API YouGile v2.0
Документация API: https://ru.yougile.com/api-v2#/
------------------------------------------------------------
"""

from .YouGileRestAPI import YouGileRestAPI
from .exceptions import YouGileAPIError

__all__ = ['YouGileRestAPI']
__version__ = "1.0.1"
