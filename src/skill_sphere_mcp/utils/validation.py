def validate_type(value: object, typ: type[T]) -> T:
    if not isinstance(value, typ):
        raise TypeError(f"Expected type {typ}, got {type(value)}")
    return value 