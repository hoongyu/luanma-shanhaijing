from luanma.repro import REGISTRY, repro


def test_decorator_puts_the_function_in_the_registry_under_its_name():
    @repro("_probe")
    def _probe():
        return "x"

    assert REGISTRY["_probe"]() == "x"
    del REGISTRY["_probe"]
