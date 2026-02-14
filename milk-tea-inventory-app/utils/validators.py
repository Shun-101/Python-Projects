"""
BrewMetric Validators Module
Input validation utilities for forms and user data.
"""

import re
from datetime import datetime


class Validators:
    """Input validation utilities."""
    
    @staticmethod
    def validate_positive_number(value: str, allow_zero: bool = False) -> tuple[bool, str]:
        """
        Validate that input is a positive number.
        
        Args:
            value: String value to validate
            allow_zero: Whether to allow zero as valid
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            num = float(value)
            if num < 0:
                return False, "Value cannot be negative"
            if num == 0 and not allow_zero:
                return False, "Value must be greater than 0"
            return True, "Valid number"
        except ValueError:
            return False, "Invalid number format"
    
    @staticmethod
    def validate_integer(value: str) -> tuple[bool, str]:
        """
        Validate that input is an integer.
        
        Args:
            value: String value to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            int(value)
            return True, "Valid integer"
        except ValueError:
            return False, "Invalid integer format"
    
    @staticmethod
    def validate_quantity(value: str) -> tuple[bool, str]:
        """
        Validate stock quantity.
        
        Args:
            value: Quantity as string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        return Validators.validate_positive_number(value, allow_zero=True)
    
    @staticmethod
    def validate_threshold(value: str) -> tuple[bool, str]:
        """
        Validate minimum threshold.
        
        Args:
            value: Threshold as string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        return Validators.validate_positive_number(value, allow_zero=False)
    
    @staticmethod
    def validate_price(value: str) -> tuple[bool, str]:
        """
        Validate unit cost/price.
        
        Args:
            value: Price as string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        return Validators.validate_positive_number(value, allow_zero=True)
    
    @staticmethod
    def validate_item_name(name: str) -> tuple[bool, str]:
        """
        Validate inventory item name.
        
        Requirements:
        - 2-150 characters
        - Alphanumeric with spaces, hyphens, parentheses
        
        Args:
            name: Item name to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(name) < 2:
            return False, "Item name must be at least 2 characters"
        
        if len(name) > 150:
            return False, "Item name cannot exceed 150 characters"
        
        if not re.match(r'^[a-zA-Z0-9\s\-\(\)]+$', name):
            return False, "Item name can only contain letters, numbers, spaces, hyphens, and parentheses"
        
        return True, "Valid item name"
    
    @staticmethod
    def validate_category(category: str, valid_categories: list[str]) -> tuple[bool, str]:
        """
        Validate category selection.
        
        Args:
            category: Category to validate
            valid_categories: List of valid categories
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not category:
            return False, "Category is required"
        
        if category not in valid_categories:
            return False, f"Invalid category. Must be one of: {', '.join(valid_categories)}"
        
        return True, "Valid category"
    
    @staticmethod
    def validate_expiration_date(date_str: str, date_format: str = "%Y-%m-%d") -> tuple[bool, str]:
        """
        Validate expiration date.
        
        Requirements:
        - Valid date format
        - Date must be in the future (or today)
        
        Args:
            date_str: Date string to validate
            date_format: Expected date format
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not date_str:
            return True, "Valid (optional expiration date)"
        
        try:
            exp_date = datetime.strptime(date_str, date_format)
            now = datetime.now()
            
            if exp_date.date() < now.date():
                return False, "Expiration date cannot be in the past"
            
            return True, "Valid expiration date"
        except ValueError:
            return False, f"Invalid date format. Use {date_format}"
    
    @staticmethod
    def validate_notes(notes: str, max_length: int = 500) -> tuple[bool, str]:
        """
        Validate notes/description field.
        
        Args:
            notes: Notes text
            max_length: Maximum allowed length
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(notes) > max_length:
            return False, f"Notes cannot exceed {max_length} characters"
        
        return True, "Valid notes"
    
    @staticmethod
    def validate_location(location: str) -> tuple[bool, str]:
        """
        Validate storage location.
        
        Args:
            location: Location string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if location and len(location) > 100:
            return False, "Location cannot exceed 100 characters"
        
        return True, "Valid location"
    
    @staticmethod
    def validate_unit(unit: str, valid_units: list[str] = None) -> tuple[bool, str]:
        """
        Validate unit of measurement.
        
        Args:
            unit: Unit string
            valid_units: List of valid units (if None, any unit is allowed)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not unit:
            return False, "Unit is required"
        
        if len(unit) > 20:
            return False, "Unit cannot exceed 20 characters"
        
        if valid_units and unit not in valid_units:
            return False, f"Invalid unit. Must be one of: {', '.join(valid_units)}"
        
        return True, "Valid unit"
    
    @staticmethod
    def validate_waste_reason(reason: str, valid_reasons: list[str]) -> tuple[bool, str]:
        """
        Validate waste log reason.
        
        Args:
            reason: Reason for waste
            valid_reasons: List of valid reasons
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not reason:
            return False, "Reason is required"
        
        if reason not in valid_reasons:
            return False, f"Invalid reason. Must be one of: {', '.join(valid_reasons)}"
        
        return True, "Valid reason"
    
    @staticmethod
    def validate_date_range(
        start_date_str: str,
        end_date_str: str,
        date_format: str = "%Y-%m-%d"
    ) -> tuple[bool, str]:
        """
        Validate date range for reports.
        
        Args:
            start_date_str: Start date string
            end_date_str: End date string
            date_format: Expected date format
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            start = datetime.strptime(start_date_str, date_format)
            end = datetime.strptime(end_date_str, date_format)
            
            if start > end:
                return False, "Start date cannot be after end date"
            
            return True, "Valid date range"
        except ValueError:
            return False, f"Invalid date format. Use {date_format}"
    
    @staticmethod
    def validate_percentage(value: str) -> tuple[bool, str]:
        """
        Validate percentage value (0-100).
        
        Args:
            value: Percentage value as string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            num = float(value)
            if num < 0 or num > 100:
                return False, "Percentage must be between 0 and 100"
            return True, "Valid percentage"
        except ValueError:
            return False, "Invalid percentage format"
