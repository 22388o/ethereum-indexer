import pytest

from extract.main import Extract
from exceptions import InvalidAddress


def test_nonchecksum_address():
    nonchecksum = "0x94d8f036a0fbc216bb532d33bdf6564157af0cd7"
    with pytest.raises(InvalidAddress):
        Extract([nonchecksum])


def test_checksum_address():
    checksum = "0x94D8f036a0fbC216Bb532D33bDF6564157Af0cD7"
    Extract([checksum])
