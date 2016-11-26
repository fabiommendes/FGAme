from FGAme.utils.text import snake_case
from FGAme.utils.util import popattr

def test_snake_case():
    assert snake_case("TestSnakeCase") == "test_snake_case"

def test_popattr():

	from FGAme.physics.bodies import Body

	b1 = Body(pos=(0, 30), mass=1)

	result = popattr(b1,'position')

	assert result == None 
	## example of deletable attr on FGAme?

