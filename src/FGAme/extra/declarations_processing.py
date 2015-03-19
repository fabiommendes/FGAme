#-*- coding: utf8 -*-

from FGAme.extra.declarations_parsing import parse_data, Group, Declaration, Assignment
import FGAme

# TODO: fazer um processo de filtragem das classes permitidas
DECLARATIONS_FGAME = ['AABB', 'Triangle', 'Poly']
DECLARATIONS_MAPPING = {}
DECLARATIONS_MAPPING.update({ k: 'FGAme.' + k for k in DECLARATIONS_FGAME })


def load_tree(tree):
    out = []
    for obj in tree:
        if isinstance(obj, Declaration):
            kwds = { c.name: c.value for c in obj.children }
            obj_type = getattr(FGAme, obj.name)
            out.append(obj_type(**kwds))
            
        elif isinstance(obj, Group):
            raise NotImplementedError

    return out

if __name__ == '__main__':
    example = (
        'Circle:\n'
        '    radius: 30\n'
        '    pos: (400, 300)\n'
    )
    tree = parse_data(example)
    print(load_tree(tree))