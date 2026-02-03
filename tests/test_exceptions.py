"""Tests for custom exceptions."""

import pytest
from src.exceptions import (
    LAPException,
    ValidationError,
    DataCollectionError,
    DatabaseError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ExternalAPIError,
    ConfigurationError
)


class TestLAPException:
    """Tests for base LAP exception."""
    
    def test_basic_exception(self):
        """Test basic exception creation."""
        exc = LAPException("Test error")
        assert str(exc) == "Test error"
        assert exc.message == "Test error"
        assert exc.code is None
    
    def test_exception_with_code(self):
        """Test exception with code."""
        exc = LAPException("Test error", code="TEST_ERROR")
        assert exc.code == "TEST_ERROR"


class TestValidationError:
    """Tests for validation error."""
    
    def test_validation_error(self):
        """Test validation error creation."""
        exc = ValidationError("Invalid field")
        assert str(exc) == "Invalid field"
        assert exc.code == "VALIDATION_ERROR"
        assert exc.field is None
    
    def test_validation_error_with_field(self):
        """Test validation error with field."""
        exc = ValidationError("Invalid CNPJ", field="cnpj")
        assert exc.field == "cnpj"


class TestDataCollectionError:
    """Tests for data collection error."""
    
    def test_data_collection_error(self):
        """Test data collection error creation."""
        exc = DataCollectionError("Failed to collect data")
        assert str(exc) == "Failed to collect data"
        assert exc.code == "DATA_COLLECTION_ERROR"
        assert exc.source is None
    
    def test_data_collection_error_with_source(self):
        """Test data collection error with source."""
        exc = DataCollectionError("API timeout", source="PNCP")
        assert exc.source == "PNCP"


class TestDatabaseError:
    """Tests for database error."""
    
    def test_database_error(self):
        """Test database error creation."""
        exc = DatabaseError("Database connection failed")
        assert str(exc) == "Database connection failed"
        assert exc.code == "DATABASE_ERROR"
        assert exc.operation is None
    
    def test_database_error_with_operation(self):
        """Test database error with operation."""
        exc = DatabaseError("Failed to insert", operation="create")
        assert exc.operation == "create"


class TestAuthenticationError:
    """Tests for authentication error."""
    
    def test_authentication_error(self):
        """Test authentication error creation."""
        exc = AuthenticationError()
        assert str(exc) == "Authentication failed"
        assert exc.code == "AUTHENTICATION_ERROR"
    
    def test_authentication_error_custom_message(self):
        """Test authentication error with custom message."""
        exc = AuthenticationError("Invalid credentials")
        assert str(exc) == "Invalid credentials"


class TestAuthorizationError:
    """Tests for authorization error."""
    
    def test_authorization_error(self):
        """Test authorization error creation."""
        exc = AuthorizationError()
        assert str(exc) == "Insufficient permissions"
        assert exc.code == "AUTHORIZATION_ERROR"


class TestNotFoundError:
    """Tests for not found error."""
    
    def test_not_found_error(self):
        """Test not found error creation."""
        exc = NotFoundError("Resource not found")
        assert str(exc) == "Resource not found"
        assert exc.code == "NOT_FOUND"
        assert exc.resource is None
    
    def test_not_found_error_with_resource(self):
        """Test not found error with resource."""
        exc = NotFoundError("Licitacao not found", resource="licitacao")
        assert exc.resource == "licitacao"


class TestExternalAPIError:
    """Tests for external API error."""
    
    def test_external_api_error(self):
        """Test external API error creation."""
        exc = ExternalAPIError("API request failed")
        assert str(exc) == "API request failed"
        assert exc.code == "EXTERNAL_API_ERROR"
        assert exc.api is None
        assert exc.status_code is None
    
    def test_external_api_error_with_details(self):
        """Test external API error with details."""
        exc = ExternalAPIError("Rate limit exceeded", api="PNCP", status_code=429)
        assert exc.api == "PNCP"
        assert exc.status_code == 429


class TestConfigurationError:
    """Tests for configuration error."""
    
    def test_configuration_error(self):
        """Test configuration error creation."""
        exc = ConfigurationError("Invalid configuration")
        assert str(exc) == "Invalid configuration"
        assert exc.code == "CONFIGURATION_ERROR"
        assert exc.setting is None
    
    def test_configuration_error_with_setting(self):
        """Test configuration error with setting."""
        exc = ConfigurationError("Missing API key", setting="PNCP_API_KEY")
        assert exc.setting == "PNCP_API_KEY"
