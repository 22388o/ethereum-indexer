# import pytest

# ! see comments in utils.address for why this is commented out
# from extract.main import Extract
# from exceptions import InvalidAddress


# def test_nonchecksum_address():
#     nonchecksum_address = "0x94d8f036a0fbc216bb532d33bdf6564157af0cd7"
#     with pytest.raises(InvalidAddress):
#         Extract([nonchecksum_address])


# def test_checksum_address():
#     checksum_address = "0x94D8f036a0fbC216Bb532D33bDF6564157Af0cD7"
#     Extract([checksum_address])


# def test_duplicate_addresses():
#     address_1 = "0x94D8f036a0fbC216Bb532D33bDF6564157Af0cD7"
#     address_2 = "0x94D8f036a0fbC216Bb532D33bDF6564157Af0cD7"
#     with pytest.raises(ValueError):
#         Extract([address_1, address_2])
