"""
Test for module eoworkflow_tasks.py
"""
import os

import pytest

from eolearn.core import EOPatch, EOTask, EOWorkflow, FeatureType, LoadTask, OutputTask


EOPATCH_PATH = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'example_data', 'TestEOPatch')


class DummyTask(EOTask):

    def execute(self, *eopatches):
        return eopatches[0]


@pytest.fixture(name='eopatch')
def eopatch_fixture():
    return EOPatch.load(EOPATCH_PATH)


def test_output_task(eopatch):
    """ Tests basic functionalities of OutputTask
    """
    task = OutputTask(name='my-task', features=[FeatureType.BBOX, (FeatureType.DATA, 'NDVI')])

    assert task.name == 'my-task'

    new_eopatch = task.execute(eopatch)
    assert id(new_eopatch) != id(eopatch)

    assert len(new_eopatch.get_feature_list()) == 2
    assert new_eopatch.bbox == eopatch.bbox


def test_output_task_in_workflow(eopatch):
    load = LoadTask(EOPATCH_PATH)
    output = OutputTask(name='result-name')

    workflow = EOWorkflow([
        (load, []),
        (output, [load]),
        (DummyTask(), [load])
    ])

    results = workflow.execute()

    assert len(results.outputs) == 1
    assert results.outputs['result-name'] == eopatch
