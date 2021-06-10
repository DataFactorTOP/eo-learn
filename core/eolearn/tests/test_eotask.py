"""
Credits:
Copyright (c) 2017-2019 Matej Aleksandrov, Matej Batič, Andrej Burja, Eva Erzin (Sinergise)
Copyright (c) 2017-2019 Grega Milčinski, Matic Lubej, Devis Peresutti, Jernej Puc, Tomislav Slijepčević (Sinergise)
Copyright (c) 2017-2019 Blaž Sovdat, Nejc Vesel, Jovan Višnjić, Anže Zupanc, Lojze Žust (Sinergise)

This source code is licensed under the MIT license found in the LICENSE
file in the root directory of this source tree.
"""

import unittest
import logging
import copy

from eolearn.core import EOTask


logging.basicConfig(level=logging.DEBUG)


class TwoParamException(BaseException):
    def __init__(self, param1, param2):
        # accept two parameters as opposed to BaseException, which just accepts one
        super().__init__()
        self.param1 = param1
        self.param2 = param2


class ExceptionTestingTask(EOTask):
    def __init__(self, task_arg):
        self.task_arg = task_arg

    def execute(self, exec_param):
        # try raising a subclassed exception with an unsupported __init__ arguments signature
        if self.task_arg == 'test_exception':
            raise TwoParamException(1, 2)

        # try raising a subclassed exception with an unsupported __init__ arguments signature without initializing it
        if self.task_arg == 'test_exception_fail':
            raise TwoParamException

        # raise one of the standard errors
        if self.task_arg == 'value_error':
            raise ValueError('Testing value error.')

        return self.task_arg + ' ' + exec_param


class TestEOTask(unittest.TestCase):
    class PlusOneTask(EOTask):

        @staticmethod
        def execute(x):
            return x + 1

    class PlusConstSquaredTask(EOTask):
        def __init__(self, const):
            self.const = const

        def execute(self, x):
            return (x + self.const)**2

    class SelfRecursiveTask(EOTask):
        def __init__(self, x, *args, **kwargs):
            self.recursive = self
            self.arg_x = x
            self.args = args
            self.kwargs = kwargs

        def execute(self, _):
            return self.x

    def test_call_equals_execute(self):
        task = self.PlusOneTask()
        self.assertEqual(task(1), task.execute(1), msg="t(x) should given the same result as t.execute(x)")
        task = self.PlusConstSquaredTask(20)
        self.assertEqual(task(14), task.execute(14), msg="t(x) should given the same result as t.execute(x)")

    def test_task_uids(self):
        task1 = self.PlusOneTask()
        task2 = self.PlusOneTask()
        self.assertNotEqual(task1.private_task_config.uid, task2.private_task_config.uid,
                            msg="Different tasks should have different uids.")

    def test_task_copy(self):
        task1 = self.PlusConstSquaredTask(12)
        task2 = self.SelfRecursiveTask([1, 2, 3], 3, "apple", this=12, that=task1)
        self.assertNotEqual(task1.private_task_config.uid, copy.copy(task1).private_task_config.uid,
                            msg="Copied tasks should have different uids.")
        self.assertNotEqual(task1.private_task_config.uid, copy.deepcopy(task1).private_task_config.uid,
                            msg="Copied tasks should have different uids.")
        self.assertEqual(task2.arg_x, copy.copy(task2).arg_x, msg="Shallow copies should not recursively copy values.")
        self.assertNotEqual(task2.kwargs["that"].private_task_config.uid,
                            copy.deepcopy(task2).kwargs["that"].private_task_config.uid,
                            msg="Deep copies should recursively copy values.")
        self.assertTrue(all(x == y for x, y in zip(task2.arg_x, copy.deepcopy(task2).arg_x)),
                        msg="Recursively copied values should be copied correctly.")
        deepcopied_task = copy.deepcopy(task2)
        self.assertEqual(deepcopied_task.private_task_config.uid, deepcopied_task.recursive.private_task_config.uid,
                         msg="Recursive copies of same task should have equal uids.")



class TestExecutionHandling(unittest.TestCase):

    def test_execution_handling(self):
        task = ExceptionTestingTask('test_exception')
        self.assertRaises(TwoParamException, task, 'test')

        task = ExceptionTestingTask('success')
        self.assertEqual(task('test'), 'success test')

        for parameter, exception_type in [('test_exception_fail', TypeError), ('value_error', ValueError)]:
            task = ExceptionTestingTask(parameter)
            self.assertRaises(exception_type, task, 'test')
            try:
                task('test')
            except exception_type as exception:
                message = str(exception)
                self.assertTrue(message.startswith('During execution of task ExceptionTestingTask: '))


if __name__ == '__main__':
    unittest.main()
