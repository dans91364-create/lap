"""Tests for validation utilities."""

import pytest
from src.utils.validators import (
    validate_cnpj,
    validate_cpf,
    validate_cnpj_cpf,
    format_cnpj,
    format_cpf,
    clean_document
)
from src.exceptions import ValidationError


class TestCNPJValidation:
    """Tests for CNPJ validation."""
    
    def test_valid_cnpj(self):
        """Test validation of valid CNPJ."""
        assert validate_cnpj("11.222.333/0001-81") is True
        assert validate_cnpj("11222333000181") is True
    
    def test_valid_cnpj_without_formatting(self):
        """Test validation of valid CNPJ without formatting."""
        assert validate_cnpj("11222333000181") is True
    
    def test_invalid_cnpj_wrong_length(self):
        """Test validation of CNPJ with wrong length."""
        with pytest.raises(ValidationError) as exc_info:
            validate_cnpj("123456789")
        assert "must have 14 digits" in str(exc_info.value)
    
    def test_invalid_cnpj_all_same_digits(self):
        """Test validation of CNPJ with all same digits."""
        with pytest.raises(ValidationError) as exc_info:
            validate_cnpj("11111111111111")
        assert "cannot have all digits the same" in str(exc_info.value)
    
    def test_invalid_cnpj_wrong_check_digit(self):
        """Test validation of CNPJ with wrong check digit."""
        with pytest.raises(ValidationError) as exc_info:
            validate_cnpj("11222333000180")  # Wrong check digit
        assert "Invalid CNPJ check digit" in str(exc_info.value)
    
    def test_empty_cnpj(self):
        """Test validation of empty CNPJ."""
        with pytest.raises(ValidationError) as exc_info:
            validate_cnpj("")
        assert "cannot be empty" in str(exc_info.value)
    
    def test_invalid_cnpj_no_exception(self):
        """Test validation of invalid CNPJ without exception."""
        assert validate_cnpj("123456789", raise_exception=False) is False
        assert validate_cnpj("", raise_exception=False) is False


class TestCPFValidation:
    """Tests for CPF validation."""
    
    def test_valid_cpf(self):
        """Test validation of valid CPF."""
        assert validate_cpf("111.444.777-35") is True
        assert validate_cpf("11144477735") is True
    
    def test_valid_cpf_without_formatting(self):
        """Test validation of valid CPF without formatting."""
        assert validate_cpf("11144477735") is True
    
    def test_invalid_cpf_wrong_length(self):
        """Test validation of CPF with wrong length."""
        with pytest.raises(ValidationError) as exc_info:
            validate_cpf("12345")
        assert "must have 11 digits" in str(exc_info.value)
    
    def test_invalid_cpf_all_same_digits(self):
        """Test validation of CPF with all same digits."""
        with pytest.raises(ValidationError) as exc_info:
            validate_cpf("11111111111")
        assert "cannot have all digits the same" in str(exc_info.value)
    
    def test_invalid_cpf_wrong_check_digit(self):
        """Test validation of CPF with wrong check digit."""
        with pytest.raises(ValidationError) as exc_info:
            validate_cpf("11144477736")  # Wrong check digit
        assert "Invalid CPF check digit" in str(exc_info.value)
    
    def test_empty_cpf(self):
        """Test validation of empty CPF."""
        with pytest.raises(ValidationError) as exc_info:
            validate_cpf("")
        assert "cannot be empty" in str(exc_info.value)
    
    def test_invalid_cpf_no_exception(self):
        """Test validation of invalid CPF without exception."""
        assert validate_cpf("12345", raise_exception=False) is False
        assert validate_cpf("", raise_exception=False) is False


class TestCNPJCPFValidation:
    """Tests for CNPJ/CPF combined validation."""
    
    def test_validate_cnpj_cpf_with_cpf(self):
        """Test validation of CPF using combined validator."""
        assert validate_cnpj_cpf("11144477735") is True
    
    def test_validate_cnpj_cpf_with_cnpj(self):
        """Test validation of CNPJ using combined validator."""
        assert validate_cnpj_cpf("11222333000181") is True
    
    def test_validate_cnpj_cpf_invalid_length(self):
        """Test validation with invalid length."""
        with pytest.raises(ValidationError) as exc_info:
            validate_cnpj_cpf("123456789")
        assert "must have 11 (CPF) or 14 (CNPJ) digits" in str(exc_info.value)
    
    def test_validate_cnpj_cpf_empty(self):
        """Test validation of empty document."""
        with pytest.raises(ValidationError) as exc_info:
            validate_cnpj_cpf("")
        assert "cannot be empty" in str(exc_info.value)


class TestFormatting:
    """Tests for formatting functions."""
    
    def test_format_cnpj(self):
        """Test CNPJ formatting."""
        formatted = format_cnpj("11222333000181")
        assert formatted == "11.222.333/0001-81"
    
    def test_format_cnpj_already_formatted(self):
        """Test CNPJ formatting with already formatted input."""
        formatted = format_cnpj("11.222.333/0001-81")
        assert formatted == "11.222.333/0001-81"
    
    def test_format_invalid_cnpj(self):
        """Test formatting of invalid CNPJ."""
        assert format_cnpj("12345") is None
    
    def test_format_cpf(self):
        """Test CPF formatting."""
        formatted = format_cpf("11144477735")
        assert formatted == "111.444.777-35"
    
    def test_format_cpf_already_formatted(self):
        """Test CPF formatting with already formatted input."""
        formatted = format_cpf("111.444.777-35")
        assert formatted == "111.444.777-35"
    
    def test_format_invalid_cpf(self):
        """Test formatting of invalid CPF."""
        assert format_cpf("12345") is None
    
    def test_clean_document(self):
        """Test document cleaning."""
        assert clean_document("11.222.333/0001-81") == "11222333000181"
        assert clean_document("111.444.777-35") == "11144477735"
        assert clean_document("abc123def456") == "123456"
