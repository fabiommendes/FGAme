from FGAme.utils.text import snake_case

def test_snake_case():
    assert snake_case("TestSnakeCase") == "test_snake_case"
