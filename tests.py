#!/usr/bin/env python3
#-*-coding: utf-8-*-

import unittest
from unittest.mock import Mock, patch
from bf import BF, InvalidProgramException

class BFInterpreterTestCase(unittest.TestCase):
    
    def setUp(self):
        self.bf = BF()
        self.mock_print = Mock(return_value=None)
    
    def test_load_program_and_ignore_other_characters(self):
        self.bf.load(' .ab\nc\t>\r-')
        self.assertEqual(self.bf.dump_program(), '.>-')

    def test_load_unbalanced_bracket_program(self):
        with self.assertRaises(InvalidProgramException):
            self.bf.load('++[-][')

    def test_load_invalid_bracket_program(self):
        with self.assertRaises(InvalidProgramException):
            self.bf.load('++[-]][')

    def test_load_simple_loop(self):
        self.bf.load('++[-]')
        self.assertEqual(self.bf.dump_program(), '++[-]')

    @unittest.skip
    def test_print_initialized_memory_cell(self):
        self.bf.load('.')
        with patch('builtins.print', self.mock_print):
            self.bf.run()
        self.mock_print.assert_called_once_with('\x00')

    def test_add_one_to_memory(self):
        self.bf.load('+')
        self.bf.run()
        self.assertEqual(self.bf.dump_memory(0), 1)

    def test_add_two_to_memory(self):
        self.bf.load('++')
        self.bf.run()
        self.assertEqual(self.bf.dump_memory(0), 2)

    def test_add_to_multiple_memory_cells(self):
        self.bf.load('+>++')
        self.bf.run()
        self.assertEqual(self.bf.dump_memory(0), 1)
        self.assertEqual(self.bf.dump_memory(1), 2)

    def test_dump_all_memory(self):
        self.bf.load('+>++')
        self.bf.run()
        self.assertEqual(self.bf.dump_memory(), [1, 2])

    def test_sub_underflow(self):
        self.bf.load('--')
        self.bf.run()
        self.assertEqual(self.bf.dump_memory(0), 254)

    def test_sub_one_from_memory(self):
        self.bf.load('++-')
        self.bf.run()
        self.assertEqual(self.bf.dump_memory(0), 1)

    def test_sub_overflow(self):
        self.bf.load('-++')
        self.bf.run()
        self.assertEqual(self.bf.dump_memory(0), 1)

    def test_add_five_memory_cells(self):
        self.bf.load('>>>>>')
        self.bf.run()
        self.assertEqual(self.bf.memory_size, 5)

    def test_add_three_memory_cells(self):
        self.bf.load('>><>>')
        self.bf.run()
        self.assertEqual(self.bf.memory_size, 4)
