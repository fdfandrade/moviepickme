""" Tests IMDB datasets handler module """
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import boto3

import imdb_datasets_handler

from moto import mock_s3


@mock_s3
def test_download():
    os.environ["IMDB_DATASET_BASE_URL"] = "https://datasets.imdbws.com/"
    os.environ["AWS_ID"] = "ID"
    os.environ["AWS_SECRET"] = "SECRET"
    os.environ["DATASETS_BUCKET"] = "mybucket"
    os.environ["IMDB_DATASET_FILES"] = "title.akas.tsv.gz"

    # create s3 client
    # conn = boto3.client('s3', "eu-east-1")

    handler = imdb_datasets_handler.ImdbDatasetsHandler()
    handler.process()
