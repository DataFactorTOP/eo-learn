"""
Module containing integrations with Ray framework

In order to use this module you have to install `ray` Python package.
"""
try:
    import ray
except ImportError:
    raise ImportError('To use this module you have to install ray Python package')
from tqdm.auto import tqdm

from ..eoexecution import EOExecutor, _ProcessingType


class RayExecutor(EOExecutor):
    """ A special type of `EOExecutor` that works with Ray framework
    """
    def run(self, return_results=False):
        """ Runs the executor using a Ray cluster

        Before calling this method make sure to initialize a Ray cluster using `ray.init`.

        :param return_results: If `True` this method will return a list of all results of the execution. Note that
            this might exceed the available memory. By default this parameter is set to `False`.
        :type: bool
        :return: If `return_results` is set to `True` it will return a list of results, otherwise it will return `None`
        :rtype: None or list(eolearn.core.WorkflowResults)
        """
        if not ray.is_initialized():
            raise RuntimeError('Please initialize a Ray cluster before calling this method')

        return super().run(workers=None, multiprocess=True, return_results=return_results)

    @staticmethod
    def _get_processing_type(*args, **kwargs):
        """ Provides a type of processing for later references
        """
        return _ProcessingType.RAY

    @classmethod
    def _run_execution(cls, processing_args, *args, **kwargs):
        """ Runs ray execution
        """
        workflow_executor = _ray_workflow_executor
        futures = [workflow_executor.remote(workflow_args) for workflow_args in processing_args]

        for _ in tqdm(_progress_bar_iterator(futures), total=len(futures)):
            pass

        return ray.get(futures)


@ray.remote
def _ray_workflow_executor(workflow_args):
    return RayExecutor._execute_workflow(workflow_args)


def _progress_bar_iterator(futures):
    """ A utility to help tracking finished ray processes

    Note that using directly tqdm(futures) would cause memory problems and is not accurate
    """
    while futures:
        done, futures = ray.wait(futures, num_returns=1)
        yield
