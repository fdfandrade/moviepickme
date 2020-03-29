#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Tests IMDB datasets handler module """
import os
import logging
import json

import pytest
import boto3

from moto import mock_s3, mock_stepfunctions, mock_sts

import fixtures
import imdb_dataset_processor_handler

boto3.set_stream_logger("", logging.CRITICAL)

account_id = None
region = "us-east-1"

# pylint: disable=redefined-outer-name
# pylint: disable=W0212


@pytest.fixture
def handler(scope="session", autouse=True):
    """ Setup the handler to be used in the tests """
    os.environ["STORAGE_BUCKET"] = "mybucket"

    s3_mock = mock_s3()
    s3_mock.start()

    sts_mock = mock_sts()
    sts_mock.start()

    stepfunctions_mock = mock_stepfunctions()
    stepfunctions_mock.start()

    yield imdb_dataset_processor_handler.ImdbDatasetProcessorHandler(
        "title.basics.small.tsv.gz"
    )

    s3_mock.stop()
    sts_mock.stop()
    stepfunctions_mock.stop()


def test_generate_input(handler):
    """ Test the generation of the stateMachine input """
    header = "tconst	titleType	primaryTitle	originalTitle	isAdult	startYear	endYear	runtimeMinutes	genres"
    header = header.split("\t")

    line = "tt0000001	short	Carmencita	Carmencita	0	1894	\\N	1	Documentary,Short"
    line = line.split("\t")

    _input = handler._input(header, line)
    _input = json.loads(_input)

    assert _input["tconst"] == "tt0000001"
    assert _input["titleType"] == "short"
    assert _input["primaryTitle"] == "Carmencita"
    assert _input["originalTitle"] == "Carmencita"


def test_handler(handler, request):
    """ Test the read of tsv file """

    s3_client = boto3.client("s3", "eu-east-1")
    s3_client.create_bucket(Bucket="mybucket")

    base_dir = request.fspath.dirname + "\\\\"
    dataset = "title.basics.small.tsv.gz"

    s3_client.upload_file(base_dir + dataset, "mybucket", dataset)

    response = handler.sf_client.create_state_machine(
        name="StateMachine",
        definition=fixtures.state_machine(),
        roleArn=_get_default_role(),
    )

    os.environ["IMDB_TITLE_STATE_MACHINE"] = response["stateMachineArn"]

    handler.handle()


def _get_account_id():
    """ Account lookup for tests """
    global account_id
    if account_id:
        return account_id
    sts = boto3.client("sts", region_name=region)
    identity = sts.get_caller_identity()
    account_id = identity["Account"]
    return account_id


def _get_default_role():
    """ Role ARN needed for tests """
    return "arn:aws:iam::" + _get_account_id() + ":role/unknown_sf_role"
