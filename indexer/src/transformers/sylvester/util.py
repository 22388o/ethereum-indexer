"""Util methods for sylvester"""

# TODO: move this to a seperate pypi package

import base64


def hex_to_int(hex_str: str) -> int:
    """hex bytes to integer"""
    return int(hex_str, 16)


def bytes_to_int(value) -> int:
    """bytes to interger"""
    return int.from_bytes(value, byteorder="big", signed=False)


def unpack_price(price: str) -> int:
    """
    Unpacks Price into number [-9999.9999, 9999.9999]

    Args:
        price (str): packed hexadecimal price

    Returns:
        (int): unpacked price
    """
    # Covalent returns bytes4 types encoded in base64
    price = base64.b64decode(price).hex().upper()  # decode into hex
    whole_hex = price[:4]
    decimal_hex = price[4:]

    whole = hex_to_int(whole_hex)
    decimal = hex_to_int(decimal_hex)

    whole = min(whole, 9999)
    decimal = min(decimal, 9999)

    # shift right 4 decimal places
    decimal = decimal * 10**-4
    return whole + decimal
