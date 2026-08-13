from luanma.loader import load_all


def test_loads_every_yaml_in_the_yao_directory():
    yaos = load_all()

    ids = {y.id for y in yaos}
    assert "kunjinkao" in ids


def test_entries_come_back_as_validated_objects():
    (kjk,) = [y for y in load_all() if y.id == "kunjinkao"]

    assert kjk.name == "錕斤拷"
    assert kjk.expect == "锟斤拷"
