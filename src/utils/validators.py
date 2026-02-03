"""Validation utilities for CNPJ, CPF and other data formats."""

import re
from typing import Optional
from src.exceptions import ValidationError


def validate_cnpj(cnpj: str, raise_exception: bool = True) -> bool:
    """
    Validate CNPJ (Brazilian company registration number).
    
    Args:
        cnpj: CNPJ string to validate
        raise_exception: Whether to raise exception on invalid CNPJ
        
    Returns:
        True if valid, False otherwise
        
    Raises:
        ValidationError: If CNPJ is invalid and raise_exception is True
    """
    if not cnpj:
        if raise_exception:
            raise ValidationError("CNPJ cannot be empty", field="cnpj")
        return False
    
    # Remove non-numeric characters
    cnpj_numbers = re.sub(r'[^0-9]', '', cnpj)
    
    # CNPJ must have 14 digits
    if len(cnpj_numbers) != 14:
        if raise_exception:
            raise ValidationError(f"CNPJ must have 14 digits, got {len(cnpj_numbers)}", field="cnpj")
        return False
    
    # Check for known invalid patterns (all same digits)
    if cnpj_numbers == cnpj_numbers[0] * 14:
        if raise_exception:
            raise ValidationError("CNPJ cannot have all digits the same", field="cnpj")
        return False
    
    # Calculate first check digit
    weights = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    sum_digits = sum(int(cnpj_numbers[i]) * weights[i] for i in range(12))
    remainder = sum_digits % 11
    first_digit = 0 if remainder < 2 else 11 - remainder
    
    if int(cnpj_numbers[12]) != first_digit:
        if raise_exception:
            raise ValidationError("Invalid CNPJ check digit", field="cnpj")
        return False
    
    # Calculate second check digit
    weights = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    sum_digits = sum(int(cnpj_numbers[i]) * weights[i] for i in range(13))
    remainder = sum_digits % 11
    second_digit = 0 if remainder < 2 else 11 - remainder
    
    if int(cnpj_numbers[13]) != second_digit:
        if raise_exception:
            raise ValidationError("Invalid CNPJ check digit", field="cnpj")
        return False
    
    return True


def validate_cpf(cpf: str, raise_exception: bool = True) -> bool:
    """
    Validate CPF (Brazilian individual registration number).
    
    Args:
        cpf: CPF string to validate
        raise_exception: Whether to raise exception on invalid CPF
        
    Returns:
        True if valid, False otherwise
        
    Raises:
        ValidationError: If CPF is invalid and raise_exception is True
    """
    if not cpf:
        if raise_exception:
            raise ValidationError("CPF cannot be empty", field="cpf")
        return False
    
    # Remove non-numeric characters
    cpf_numbers = re.sub(r'[^0-9]', '', cpf)
    
    # CPF must have 11 digits
    if len(cpf_numbers) != 11:
        if raise_exception:
            raise ValidationError(f"CPF must have 11 digits, got {len(cpf_numbers)}", field="cpf")
        return False
    
    # Check for known invalid patterns (all same digits)
    if cpf_numbers == cpf_numbers[0] * 11:
        if raise_exception:
            raise ValidationError("CPF cannot have all digits the same", field="cpf")
        return False
    
    # Calculate first check digit
    sum_digits = sum(int(cpf_numbers[i]) * (10 - i) for i in range(9))
    remainder = sum_digits % 11
    first_digit = 0 if remainder < 2 else 11 - remainder
    
    if int(cpf_numbers[9]) != first_digit:
        if raise_exception:
            raise ValidationError("Invalid CPF check digit", field="cpf")
        return False
    
    # Calculate second check digit
    sum_digits = sum(int(cpf_numbers[i]) * (11 - i) for i in range(10))
    remainder = sum_digits % 11
    second_digit = 0 if remainder < 2 else 11 - remainder
    
    if int(cpf_numbers[10]) != second_digit:
        if raise_exception:
            raise ValidationError("Invalid CPF check digit", field="cpf")
        return False
    
    return True


def validate_cnpj_cpf(document: str, raise_exception: bool = True) -> bool:
    """
    Validate CNPJ or CPF based on length.
    
    Args:
        document: CNPJ or CPF string to validate
        raise_exception: Whether to raise exception on invalid document
        
    Returns:
        True if valid, False otherwise
        
    Raises:
        ValidationError: If document is invalid and raise_exception is True
    """
    if not document:
        if raise_exception:
            raise ValidationError("Document cannot be empty", field="document")
        return False
    
    # Remove non-numeric characters
    numbers = re.sub(r'[^0-9]', '', document)
    
    if len(numbers) == 11:
        return validate_cpf(document, raise_exception)
    elif len(numbers) == 14:
        return validate_cnpj(document, raise_exception)
    else:
        if raise_exception:
            raise ValidationError(
                f"Document must have 11 (CPF) or 14 (CNPJ) digits, got {len(numbers)}",
                field="document"
            )
        return False


def format_cnpj(cnpj: str) -> Optional[str]:
    """
    Format CNPJ to standard format XX.XXX.XXX/XXXX-XX.
    
    Args:
        cnpj: CNPJ string to format
        
    Returns:
        Formatted CNPJ or None if invalid
    """
    if not validate_cnpj(cnpj, raise_exception=False):
        return None
    
    numbers = re.sub(r'[^0-9]', '', cnpj)
    return f"{numbers[:2]}.{numbers[2:5]}.{numbers[5:8]}/{numbers[8:12]}-{numbers[12:14]}"


def format_cpf(cpf: str) -> Optional[str]:
    """
    Format CPF to standard format XXX.XXX.XXX-XX.
    
    Args:
        cpf: CPF string to format
        
    Returns:
        Formatted CPF or None if invalid
    """
    if not validate_cpf(cpf, raise_exception=False):
        return None
    
    numbers = re.sub(r'[^0-9]', '', cpf)
    return f"{numbers[:3]}.{numbers[3:6]}.{numbers[6:9]}-{numbers[9:11]}"


def clean_document(document: str) -> str:
    """
    Remove all non-numeric characters from document.
    
    Args:
        document: Document string to clean
        
    Returns:
        Clean numeric-only string
    """
    return re.sub(r'[^0-9]', '', document)
