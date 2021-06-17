"""
Module containing `ray` integrations
"""
try:
    import ray
except ImportError:
    raise ImportError('To use this module you have to install ray Python package')
from tqdm.auto import tqdm

from ..eoexecution import EOExecutor, _ProcessingType


class RayExecutor(EOExecutor):

    def run(self, return_results=False):
        """ Runs the executor using the Ray Cluster.

        :param return_results: If `True` this method will return a list of all results of the execution. Note that
            this might exceed the available memory. By default this parameter is set to `False`.
        :type: bool
        :return: If `return_results` is set to `True` it will return a list of results, otherwise it will return `None`
        :rtype: None or list(eolearn.core.WorkflowResults)
        """
        # TODO: perhaps try initializing ray with a given number of workers?
        return super().run(workers=None, multiprocess=True, return_results=return_results)

    @staticmethod
    def _get_processing_type(*args, **kwargs):
        return _ProcessingType.RAY

    def _run_execution(self, processing_args, *args, **kwargs):
        """ Runs ray execution
        """
        futures = [RayExecutor._ray_execute_workflow.remote(self, workflow_args) for workflow_args in processing_args]
        return [ray.get(future) for future in tqdm(futures)]

    @ray.remote
    def _ray_execute_workflow(self, workflow_args):
        return self._execute_workflow(workflow_args)
