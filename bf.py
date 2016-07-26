#!/usr/bin/env python3
#-*-coding: utf-8-*-

class InvalidProgramException(Exception):
    pass


class BF(object):

    def __init__(self):
        self._program = None
        self._memory = [0]
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
        cell_size = 256 # 8-bit
        current_value = self._memory[self._data_pointer] 
        new_val = current_value + value 
        if new_val < 0:
            new_val += cell_size
        self._memory[self._data_pointer] = new_val % cell_size
