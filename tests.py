#!/usr/bin/env python3
# -*-coding: utf-8-*-
import os
import unittest
from unittest.mock import Mock, patch
from timeout_decorator import timeout
from bf import BF, ExpandableMemory, InvalidProgramException,\
                ExecutionTimeoutException


class BFInterpreterTestCase(unittest.TestCase):

    def setUp(self):
        self.memory = ExpandableMemory(cell_size=8)
        self.bf = BF(self.memory)
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
        self.assertEqual(self.bf.dump_memory(0), 1)
        self.assertEqual(self.bf.dump_memory(1), 2)

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
        self.assertEqual(self.bf.memory_size, 6)

    def test_add_three_memory_cells(self):
        self.bf.load('>><>>')
        self.bf.run()
        self.assertEqual(self.bf.memory_size, 4)

    def test_empty_memory_length(self):
        self.assertEqual(self.bf.memory_size, 0)

    def test_out_of_range_memory(self):
        self.bf.load('<<<<')
        self.bf.run()
        self.assertEqual(self.bf.data_pointer, 0)
        self.assertEqual(self.bf.memory_size, 0)

    @unittest.skipIf(os.getenv('PYCHARM_HELPERS_DIR', False), 'Skip because of poor PyCharm terminal emulation')
    def test_read_char(self):
        self.bf.load(',')
        mock = Mock(return_value='a')
        with patch('sys.stdin.read', mock):
            self.bf.run()
        self.assertEqual(self.bf.dump_memory(0), ord('a'))

    def test_empty_loop(self):
        self.bf.load('[]')
        self.bf.run()
        self.assertEqual(self.bf.instruction_counter, 1)
        self.assertEqual(self.bf.memory_size, 1)

    def test_loop_once(self):
        self.bf.load('+[-]')
        self.bf.run()
        self.assertEqual(self.bf.instruction_counter, 5)
        self.assertEqual(self.bf.memory_size, 1)
        self.assertEqual(self.bf.dump_memory(0), 0)

    def test_operation_after_loop(self):
        self.bf.load('++[-]>+')
        self.bf.run()
        self.assertEqual(self.bf.memory_size, 2)
        self.assertEqual(self.bf.data_pointer, 1)
        self.assertEqual(self.bf.dump_memory(0), 0)
        self.assertEqual(self.bf.dump_memory(1), 1)

    @timeout(0.2)
    def test_time_out(self):
        self.bf.load('+[]')
        with self.assertRaises(ExecutionTimeoutException):
            self.bf.run(timeout=0)

    def hello_world_setup(self):
        return """
       ++++++++
       [
         >++++
         [
           >++
           >+++
           >+++
           >+
           <<<<-
         ]
         >+
         >+
         >-
         >>+
         [<]
         <-
       ]
       """

    def hello_world_print(self):
        return """
       >>.
       >---.
       +++++++..+++.
       >>.
       <-.
       <.+++.------.--------.
       >>+.
       >++.
       """

    def test_hello_world_setup(self):
        self.bf.load(self.hello_world_setup())
        self.bf.run()
        self.assertEqual(self.bf.data_pointer, 0)
        self.assertEqual(self.bf.memory_size, 7)
        self.assertEqual(self.bf.dump_memory(0), 0)
        self.assertEqual(self.bf.dump_memory(1), 0)
        self.assertEqual(self.bf.dump_memory(2), 72)
        self.assertEqual(self.bf.dump_memory(3), 104)
        self.assertEqual(self.bf.dump_memory(4), 88)
        self.assertEqual(self.bf.dump_memory(5), 32)
        self.assertEqual(self.bf.dump_memory(6), 8)

    @unittest.skip
    def test_hello_world(self):
        self.bf.load(self.hello_world_setup() + self.hello_world_print())
        self.bf.run()
