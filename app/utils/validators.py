import phonenumbers

def validate_and_format_phone_number(value: str) -> str:
    try:
        parsed = phonenumbers.parse(value, None)  # or "IN" for India-specific
        if not phonenumbers.is_valid_number(parsed):
            raise ValueError('Invalid phone number')
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except Exception:
        raise ValueError('Invalid phone number format')
