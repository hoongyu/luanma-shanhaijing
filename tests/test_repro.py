from luanma.repro import REGISTRY, repro


def test_decorator_puts_the_function_in_the_registry_under_its_name():
    @repro("_probe")
    def _probe():
        return "x"

    assert REGISTRY["_probe"]() == "x"
    del REGISTRY["_probe"]


def test_two_replacement_chars_read_as_gbk_become_kunjinkao():
    assert REGISTRY["kunjinkao"]() == "锟斤拷"


def test_an_odd_number_of_replacement_chars_cannot_form_it():
    """锟斤拷必成双 —— 第三枚只剩一个字节，GBK 解码直接失败。"""
    import pytest
    with pytest.raises(UnicodeDecodeError):
        ("\ufffd" * 3).encode("utf-8").decode("gbk")
