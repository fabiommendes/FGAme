# -*- coding: utf8 -*-
from random import shuffle, random
from math import sqrt
from FGAme.objects import Poly


def explode(obj, world, energy=0, prob_rec=0.5):
    world.remove(obj)
    N = obj.num_sides
    new_objects = []

    if N == 3:
        sides = [obj.get_side(i).norm() for i in range(3)]
        idx = sides.index(max(sides))
        middle = (obj.vertices[idx] + obj.vertices[(idx + 1) % N]) / 2
        pt0 = obj.vertices[idx]
        pt1 = obj.vertices[(idx + 1) % N]
        pt2 = obj.vertices[(idx + 2) % N]

        new_objects.append(
            Poly([pt0, middle, pt2], color=obj.color, omega=obj.omega, density=obj.density))
        new_objects.append(
            Poly([middle, pt1, pt2], color=obj.color, omega=obj.omega, density=obj.density))

    else:
        # Determina os vértices da triangulação e cria objeto
        for i in range(N):
            pt1 = obj.vertices[i]
            pt2 = obj.vertices[(i + 1) % N]
            pt3 = obj.pos
            new = Poly([pt1,
                        pt2,
                        pt3],
                       color=obj.color,
                       omega=obj.omega,
                       density=obj.density)
            new_objects.append(new)

    # Distribui as energias adicionais aleatoriamente entre os objetos
    N = len(new_objects)
    Z = sum(x ** 2 for x in range(1, N + 1))
    energies = [energy * x ** 2 / Z for x in range(1, N + 1)]
    shuffle(energies)

    # Processa os novos objetos criados
    for i, new in enumerate(new_objects):
        # Calcula a direção radial da explosão e move o objeto
        norm = (new.pos - obj.pos).normalize()
        new.move(norm)

        # Adiciona velocidade de acordo com a velocidade original e com a
        # contribuição de energia
        new.boost(obj.vpoint(new.pos))

        # Adiciona objeto ao mundo
        world.add(new)

        # Aplica a função recursivamente com uma determinada probabilidade
        if random() < prob_rec and new.area > 10:
            explode(new, world, energies[i], 2.0 * prob_rec / N)
        else:
            delta_speed = sqrt(2.0 * energies[i] / new.mass) * norm
            new.boost(delta_speed)
