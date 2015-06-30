# -*- coding: utf8 -*-


class DoesNotHaveInverseMatrixError(Exception):

    def __init__(self, message):
        super(DoesNotHaveInverseMatrixError, self).__init__(message)


class InvalidAxisError(Exception):

    def __init__(self, message):
        super(InvalidAxisError, self).__init__(message)
