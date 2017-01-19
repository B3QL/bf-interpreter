#!/usr/bin/env python3
# -*-coding: utf-8-*-

from threading import Timer, Event


class InvalidProgramException(Exception):
    pass


class ExecutionTimeoutException(Exception):
    pass


class CyclicBoundedList(list):

    def __init__(self, lower, upper, elements=()):
        self._lower_bound = lower
        self._upper_bound = upper
        super(CyclicBoundedList, self).__init__(
                self._transform_value(e) for e in elements)

    @property
    def lower_bound(self):
        return self._lower_bound

    @property
    def upper_bound(self):
        return self._upper_bound

    def _transform_value(self, val):
        if val < self._lower_bound:
            val += self._upper_bound
        return val % self._upper_bound

    def __setitem__(self, idx, val):
        super(CyclicBoundedList, self).__setitem__(
            idx, self._transform_value(val))

    def append(self, item):
        super(CyclicBoundedList, self).append(
                self._transform_value(item))

    def insert(self, idx, val):
        super(CyclicBoundedList, self).insert(
                idx, self._transform_value(val))

    def extend(self, element):
        super(CyclicBoundedList, self).extend(
                self._transform_value(e) for e in element)


class ExpandableMemory(object):

    def __init__(self, cell_size, cell_value=0):
        self._list = CyclicBoundedList(lower=0, upper=2**cell_size)
        self._cell_value = cell_value

    def __getitem__(self, idx):
        self._check_and_expand(idx)
        return self._list[idx]

    def _check_and_expand(self, idx):
        if self._index_out_of_range(idx):
            self._expand_memory(idx)

    def _index_out_of_range(self, idx):
        return idx >= self.__len__()

    def _expand_memory(self, idx):
        offset = self._calculate_offset(idx)
        payload = [self._cell_value] * offset
        self._list.extend(payload)

    def _calculate_offset(self, idx):
        max_index = self.__len__() - 1
        return idx - max_index

    def __setitem__(self, idx, val):
        self._check_and_expand(idx)
        self._list[idx] = val

    def __len__(self):
        return len(self._list)

    def __repr__(self):
        cls = type(self)
        return '<%s Content: %s>' % (cls.__name__, repr(self._list))


class BF(object):

    def __init__(self, memory):
        self._program = None
        self._brackets_map = {}
        self._memory = memory
        self._data_pointer = 0
        self._inst_pointer = 0
        self._inst_counter = 0
        self._exec_timer = None
        self._timeout = Event()

    def load(self, program):
        self._program = self._ignore_characters(program)
        self._map_brackets()

    def _ignore_characters(self, program):
        symbols = '><+-.,[]'
        return ''.join(s for s in program if s in symbols)

    def _map_brackets(self):
        brackets = []
        for ptr, inst in enumerate(self._program):
            if inst == '[':
                brackets.append(ptr)
            if inst == ']':
                if len(brackets) > 0:
                    opening_bracket = brackets.pop()
                    closing_bracket = ptr
                    self._brackets_map[opening_bracket] = closing_bracket
                    self._brackets_map[closing_bracket] = opening_bracket
                else:
                    raise InvalidProgramException('Missing opening bracket')

        if len(brackets) > 0:
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
        return len(self._memory)

    @property
    def data_pointer(self):
        return self._data_pointer

    @property
    def instruction_counter(self):
        return self._inst_counter

    def run(self, timeout=None):
        if timeout is not None:
            self._exec_timer = Timer(timeout, self._timeout.set)
            self._exec_timer.start()

        while self._inst_pointer < len(self._program) and self._no_timeout():
            c = self._current_instruction()
            if c == '+':
                self._increment_memory(1)
            if c == '-':
                self._increment_memory(-1)
            if c == '>':
                self._move_data_pointer(1)
            if c == '<':
                self._move_data_pointer(-1)
            if c == '.':
                print(self._get_char_from_memory())
            if c == ',':
                self._read_char_to_memory()
            if c == '[' and self._memory[self._data_pointer] == 0:
                self._jump_to_bracket()
            if c == ']':
                self._jump_to_bracket()
                self._inst_pointer -= 1

            self._inst_pointer += 1
            self._inst_counter += 1
        if self._exec_timer is not None:
            self._exec_timer.cancel()

    def _no_timeout(self):
        if self._timeout.is_set():
            fmt = ('Timeout at {} instruction,'
                   'instruction counter: {},'
                   'data pointer: {}')
            data = self._inst_pointer, self._inst_counter, self._data_pointer
            raise ExecutionTimeoutException(fmt.format(*data))
        else:
            return True

    def _current_instruction(self):
        return self._program[self._inst_pointer]

    def _jump_to_bracket(self):
        self._inst_pointer = self._brackets_map[self._inst_pointer]

    def _increment_memory(self, val):
        self._memory[self._data_pointer] += val

    def _get_char_from_memory(self):
        num = self._memory[self._data_pointer]
        return chr(num)

    def _read_char_to_memory(self):
        self._memory[self._data_pointer] = ord(self._read_char())

    def _read_char(self):
        # http://code.activestate.com/recipes/134892/
        import sys, tty, termios # noqa
        fd = sys.stdin.fileno()
        settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, settings)
        return ch

    def _move_data_pointer(self, pos):
        next_pos = self._data_pointer + pos
        if next_pos >= 0:
            self._data_pointer = next_pos
            self._synchronize_memory()

    def _synchronize_memory(self):
        self._increment_memory(0)
