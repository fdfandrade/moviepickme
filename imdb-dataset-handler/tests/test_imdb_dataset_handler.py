#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Tests IMDB datasets handler module """
import os
import logging
import boto3
import pytest

from moto import mock_s3, mock_stepfunctions, mock_sts

import fixtures
import imdb_dataset_handler

boto3.set_stream_logger("", logging.CRITICAL)

# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=protected-access

account_id = None
region = "us-east-1"

@pytest.fixture
def handler(scope="session", autouse=True):
    """ Setup the handler to be used in the tests """
    os.environ["BASEDIR"] = "D:\\Personnal\\repos\\moviepickme\\tmp\\"
    os.environ["IMDB_DATASET_BASE_URL"] = "https://datasets.imdbws.com/"
    os.environ["STORAGE_BUCKET"] = "mybucket"
    os.environ["IMDB_DATASET_FILES"] = "title.ratings.tsv.gz"

    s3_mock = mock_s3()
    s3_mock.start()

    sts_mock = mock_sts()
    sts_mock.start()

    stepfunctions_mock = mock_stepfunctions()
    stepfunctions_mock.start()

    yield imdb_dataset_handler.ImdbDatasetHandler()

    s3_mock.stop()
    sts_mock.stop()
    stepfunctions_mock.stop()

def test_download(handler):
    """ Test the download file from IMDB datasets repository """
    handler._download("title.ratings.tsv.gz")

def test_upload(handler):
    """ Test the upload file to S3 bucket """
    handler.s3_client.create_bucket(Bucket="mybucket")
    handler._upload("title.ratings.tsv.gz")

def test_uncompress(handler):
    """ Test the uncompress of the file from and to S3 bucket """
    handler.s3_client.create_bucket(Bucket="mybucket")

    handler._upload("title.ratings.tsv.gz")
    handler._uncompress("title.ratings.tsv.gz")

def test_handle(handler):
    """ Test the upload file to S3 bucket """
    handler.s3_client.create_bucket(Bucket="mybucket")

    response = handler.sf_client.create_state_machine(
        name="IMDb-Datasets-StateMachine",
        definition=fixtures.state_machine(),
        roleArn=_get_default_role(),
    )

    os.environ["IMDB_DATASET_STATE_MACHINE"] = response["stateMachineArn"]

    handler.handle()

def test_start_workflow(handler):
    """ Test the start of the workflow """
    response = handler.sf_client.create_state_machine(
        name="Alerting-Response-StateMachine",
        definition=fixtures.state_machine(),
        roleArn=_get_default_role(),
    )

    os.environ["IMDB_DATASET_STATE_MACHINE"] = response["stateMachineArn"]

    handler._start_workflow("title.ratings.tsv")

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
