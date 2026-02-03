"""Custom exception classes for the LAP system."""


class LAPException(Exception):
    """Base exception for LAP system."""
    
    def __init__(self, message: str, code: str = None):
        """
        Initialize LAP exception.
        
        Args:
            message: Error message
            code: Optional error code
        """
        self.message = message
        self.code = code
        super().__init__(self.message)


class ValidationError(LAPException):
    """Exception raised for validation errors."""
    
    def __init__(self, message: str, field: str = None):
        """
        Initialize validation error.
        
        Args:
            message: Error message
            field: Optional field name that failed validation
        """
        super().__init__(message, code="VALIDATION_ERROR")
        self.field = field


class DataCollectionError(LAPException):
    """Exception raised when data collection fails."""
    
    def __init__(self, message: str, source: str = None):
        """
        Initialize data collection error.
        
        Args:
            message: Error message
            source: Optional source that failed (e.g., 'PNCP', 'CEIS/CNEP')
        """
        super().__init__(message, code="DATA_COLLECTION_ERROR")
        self.source = source


class DatabaseError(LAPException):
    """Exception raised for database operations errors."""
    
    def __init__(self, message: str, operation: str = None):
        """
        Initialize database error.
        
        Args:
            message: Error message
            operation: Optional operation that failed (e.g., 'create', 'update')
        """
        super().__init__(message, code="DATABASE_ERROR")
        self.operation = operation


class AuthenticationError(LAPException):
    """Exception raised for authentication failures."""
    
    def __init__(self, message: str = "Authentication failed"):
        """
        Initialize authentication error.
        
        Args:
            message: Error message
        """
        super().__init__(message, code="AUTHENTICATION_ERROR")


class AuthorizationError(LAPException):
    """Exception raised for authorization failures."""
    
    def __init__(self, message: str = "Insufficient permissions"):
        """
        Initialize authorization error.
        
        Args:
            message: Error message
        """
        super().__init__(message, code="AUTHORIZATION_ERROR")


class NotFoundError(LAPException):
    """Exception raised when a resource is not found."""
    
    def __init__(self, message: str, resource: str = None):
        """
        Initialize not found error.
        
        Args:
            message: Error message
            resource: Optional resource type (e.g., 'licitacao', 'municipio')
        """
        super().__init__(message, code="NOT_FOUND")
        self.resource = resource


class ExternalAPIError(LAPException):
    """Exception raised when external API calls fail."""
    
    def __init__(self, message: str, api: str = None, status_code: int = None):
        """
        Initialize external API error.
        
        Args:
            message: Error message
            api: Optional API name (e.g., 'PNCP', 'CEIS')
            status_code: Optional HTTP status code
        """
        super().__init__(message, code="EXTERNAL_API_ERROR")
        self.api = api
        self.status_code = status_code


class ConfigurationError(LAPException):
    """Exception raised for configuration errors."""
    
    def __init__(self, message: str, setting: str = None):
        """
        Initialize configuration error.
        
        Args:
            message: Error message
            setting: Optional setting name that has an error
        """
        super().__init__(message, code="CONFIGURATION_ERROR")
        self.setting = setting
