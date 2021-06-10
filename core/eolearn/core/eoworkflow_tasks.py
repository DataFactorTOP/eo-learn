"""
Module implementing tasks that have a special effect in `EOWorkflow`
"""
from .eotask import EOTask


class OutputTask(EOTask):
    """ Stores `EOPatch` as an output of `EOWorkflow` results
    """
    def __init__(self, name=None, features=...):
        """
        :param name: A name under which `EOPatch` will be saved in `WorkflowResults`
        :type name: str or None
        :param features: A collection of features to be kept
        :type features: an object supported by the :class:`FeatureParser<eolearn.core.utilities.FeatureParser>`
        """
        self._name = name or f'output_{self.private_task_config.uuid}'  # TODO: rename to uid
        self.features = features

    @property
    def name(self):
        """ Provides a name under which output `EOPatch` will be saved

        :return: A name
        :rtype: str
        """
        return self._name

    def execute(self, eopatch):
        """
        :param eopatch: input `EOPatch`
        :type eopatch: EOPatch
        :return: A shallow copy of the given `EOPatch` which will be stored as a result of a workflow
        :rtype: EOPatch
        """
        return eopatch.__copy__(features=self.features)
