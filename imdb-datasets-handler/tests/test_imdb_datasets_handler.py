#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Tests IMDB datasets handler module """
import os
import boto3
import pytest

from moto import mock_s3

import imdb_datasets_handler

# pylint: disable=redefined-outer-name
# pylint: disable=W0212

@pytest.fixture
def handler():
    """ Setup the handler to be used in the tests """
    os.environ["BASEDIR"] = "D:\\Personnal\\repos\\moviepickme-lambdas\\tmp\\"
    os.environ["IMDB_DATASET_BASE_URL"] = "https://datasets.imdbws.com/"
    os.environ["STORAGE_BUCKET"] = "mybucket"
    os.environ["IMDB_DATASET_FILES"] = "title.basics.tsv.gz"

    return imdb_datasets_handler.ImdbDatasetsHandler()


def test_download(handler):
    """ Test the download file from IMDB datasets repository """
    handler._download("title.basics.tsv.gz")


@mock_s3
def test_upload(handler):
    """ Test the upload file to S3 bucket """

    conn = boto3.client("s3", "eu-east-1")
    conn.create_bucket(Bucket="mybucket")

    handler._upload("title.basics.tsv.gz")
