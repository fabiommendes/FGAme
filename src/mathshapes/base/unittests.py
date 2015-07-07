# -*- coding: utf8 -*-

from unittest import TestCase
import operator

opmap = {
    '+': operator.add, 'add': operator.add,
    '-': operator.sub, 'sub': operator.sub,
    '*': operator.mul, 'mul': operator.mul,
    '/': operator.truediv, 'div': operator.truediv,
}


class aUnittest(object):
    test_type = None
    commutes = ['add', 'mul']
    str_equality = False
    equal_alternatives = True

    def names(self):
        return {}

    def bin_examples(self, name,
                     commutes=False, alternatives=False, scalar=False):
        '''Retorna um iterador sobre os exemplos (a, b, c) onde
        bin(a, b) == c, para um operador binário fornecido'''

        # Extrai todos os resultados registrados
        prefix = '%s_' % name
        names = self.names()
        res = {k[4:]: v for (k, v) in names.items() if k.startswith(prefix)}

        # Itera sobre os resultados para selecionar os operandos
        obj_tt = self.test_type
        for k, res in res.items():
            a, b = [names[c] for c in k]

            # Caso scalar esteja ligado, só utiliza os resultados em que um
            # dos membros do par não seja de obj_tt
            if scalar:
                if isinstance(a, obj_tt) and isinstance(b, obj_tt):
                    continue
            else:
                if ((not alternatives)
                    and ((not isinstance(a, obj_tt)) or
                         (not isinstance(b, obj_tt)))):
                    continue

            if alternatives:
                name_a, name_b = k

                # Retorna todas permutações com a
                a_alts = [v for (k, v) in names.items()
                          if k.startswith(name_a + '_')]
                for a_alt in a_alts:
                    if isinstance(b, obj_tt) or isinstance(a_alt, obj_tt):
                        if commutes:
                            yield (b, a_alt, res)
                        yield (a_alt, b, res)

                # Retorna todas permutações com b
                b_alts = [v for (k, v) in names.items()
                          if k.startswith(name_b + '_')]
                for b_alt in b_alts:
                    if isinstance(a, obj_tt) or isinstance(b_alt, obj_tt):
                        if commutes:
                            yield (b_alt, a, res)
                        yield (a, b_alt, res)

            else:
                # Retorna a comutação
                if commutes:
                    yield (b, a, res)
                yield (a, b, res)

    def bin_assert(self, op, a, b, res):
        value = opmap[op](a, b)
        msg = '%s + %s != %s, got %s' % (a, b, res, value)
        assert self.equals(value, res), msg

    def bin_worker(self, op, **kwds):
        commutes = op in self.commutes
        for a, b, res in self.bin_examples(op, commutes=commutes):
            self.bin_assert(op, a, b, res)

    def equals(self, a, b):
        if a == b:
            return True
        elif hasattr(a, 'almost_equal'):
            if a.almost_equal(b):
                return True
        elif hasattr(b, 'almost_equal'):
            if b.almost_equal(a):
                return True
        elif self.str_equality and str(a) == str(b):
            return True
        else:
            return False

    # Operações binárias de tipos iguais ######################################
    def test_add(self):
        self.bin_worker('add')

    def test_sub(self):
        self.bin_worker('sub')

    def test_mul(self):
        self.bin_worker('mul')

    def test_div(self):
        self.bin_worker('div')

    # Operações binárias com tipos escalares ##################################
    def test_add_scalar(self):
        self.bin_worker('add', scalar=True)

    def test_sub_scalar(self):
        self.bin_worker('sub', scalar=True)

    def test_mul_scalar(self):
        self.bin_worker('mul', scalar=True)

    def test_div_scalar(self):
        self.bin_worker('div', scalar=True)

    # Operações binárias de tipos alternativos ################################
    def test_add_alts(self):
        self.bin_worker('add', alternatives=True)

    def test_sub_alts(self):
        self.bin_worker('add', alternatives=True)

    def test_mul_alts(self):
        self.bin_worker('add', alternatives=True)

    def test_div_alts(self):
        self.bin_worker('add', alternatives=True)

    # Testa igualdade com alternativas ########################################
    def test_equal_alternatives(self):
        if self.equal_alternatives:
            names = self.names()
            objs = [(k, v) for (k, v) in names.items() if len(k) == 1 and
                    isinstance(v, self.test_type)]
            for name, obj in objs:
                prefix = name + '_'
                alts = [v for (k, v) in names.items() if k.startswith(prefix)]
                for alt in alts:
                    msg = '%s != %s' % (obj, alt)
                    assert obj == alt, msg

if __name__ == '__main__':
    from unittest import TestCase
    from FGAme import Vec2

    class VectorTest(aUnittest, TestCase):
        test_type = Vec2

        def names(self):
            a = Vec2(1, 2)
            b = Vec2(3, 4)
            c = Vec2(5, 6)
            a_tuple = (1, 2)
            a_list = [1, 2]
            m = 2

            add_ab = (4, 6)
            sub_ab = (-2, -2)
            sub_ba = (2, 2)

            mul_ma = (2, 4)
            div_am = (0.5, 1)

            return locals()

    t = VectorTest()
    t.test_mul_alts()

    import nose
    nose.runmodule('__main__')
