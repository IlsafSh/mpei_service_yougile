"""
YouGile API Client
~~~~~~~~~~~~~~~~~

Клиент для работы с YouGile REST API v2.0.

"""

from .client import YouGileClient
from .exceptions import YouGileApiError, YouGileAuthError, YouGileNotFoundError

__all__ = ['YouGileClient', 'YouGileApiError', 'YouGileAuthError', 'YouGileNotFoundError']
__version__ = '0.1.0'
