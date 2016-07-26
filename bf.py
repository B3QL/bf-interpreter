#!/usr/bin/env python3
#-*-coding: utf-8-*-

class InvalidProgramException(Exception):
    pass

class CyclicBoundedList(list):
    
    def __init__(self, lower, upper, elements=[]):
        self._lower_bound = lower
        self._upper_bound = upper
        super(CyclicBoundedList, self).__init__(
                self.__transform_value(e) for e in elements)
    
    @property
    def lower_bound(self):
        return self._lower_bound

    @property
    def upper_bound(self):
        return self._upper_bound

    def __transform_value(self, val):
        if val < self._lower_bound:
            val += self._upper_bound
        return val % self._upper_bound

    def __setitem__(self, idx, val):
        super(CyclicBoundedList, self).__setitem__(idx,
                self.__transform_value(val))

    def append(self, item):
        super(CyclicBoundedList, self).append(
                self.__transform_value(item))


class BF(object):

    def __init__(self):
        self._program = None
        cell_size = 256 # 8-bit
        self._memory = CyclicBoundedList(lower=0, upper=cell_size)
        self._memory.append(0)
        self._data_pointer = 0

    def load(self, program):
        self._program = self._ignore_characters(program)
        self._check_brackets()

    def _ignore_characters(self, program):
        symbols = '><+-.,[]'
        return ''.join(s for s in program if s in symbols)

    def _check_brackets(self):
        counter = 0
        for s in self._program:
            if counter < 0:
                break
            if s == '[':
                counter += 1
            if s == ']':
                counter -= 1

        if counter < 0:
            raise InvalidProgramException('Missing opening bracket')

        if counter != 0:
            raise InvalidProgramException('Unbalanced brackets')

    def dump_program(self):
        return self._program

    def dump_memory(self, cell=None):
        if cell is not None:
            return self._memory[cell] 
        else:
            return self._memory 

    @property
    def memory_size(self):
        return len(self._memory) - 1

    def run(self):
        for c in self._program:
            if c == '+':
                self._increment_memory(1)
            if c == '-':
                self._increment_memory(-1)
            if c == '>':
                self._memory.append(0)
                self._data_pointer += 1
    
    def _increment_memory(self, value):
        self._memory[self._data_pointer] += value
