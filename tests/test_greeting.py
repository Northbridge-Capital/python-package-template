import package_name


def test_greet() -> None:
    assert package_name.greet("Ada") == "Hello, Ada!"


def test_greet_can_shout() -> None:
    assert package_name.greet("Ada", shout=True) == "HELLO, ADA!"
