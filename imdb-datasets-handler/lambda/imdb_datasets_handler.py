# -*- coding: utf-8 -*-
"""
Handles imdb datasets download
1. Get all datasets
2. Store in S3 bucket
"""

import logging
import gzip
import os
import requests
import boto3

LOG = logging.getLogger("ImdbDatasetsHandler")


class ImdbDatasetsHandler:
    """ Class to handle the download of the files """

    def __init__(self):
        self.base_url = os.getenv(
            "IMDB_DATASET_BASE_URL", "https://datasets.imdbws.com/"
        )
        # self.aws_id = os.getenv("AWS_ID")  # get this from SSM
        # self.aws_secret = os.getenv("AWS_SECRET")  # get this from SSM
        self.s3_bucket = os.getenv("STORAGE_BUCKET")
        self.datasets = os.getenv("IMDB_DATASET_FILES").split(
            ";"
        )  # this is ; separated list

    def process(self):
        """ Process all datasets """

        for dataset in self.datasets:
            self._download(dataset)
            self._upload(dataset)


    def _download(self, dataset):
        """ Download imdb file dataset """

        url = self.base_url + dataset
        local_file = "/tmp/" + dataset

        # Use a chunk size of 50 MiB (feel free to change this)
        chunk_size = 52428800

        # NOTE the stream=True parameter below
        with requests.get(url, stream=True) as request:
            request.raise_for_status()
            with open(local_file, "wb") as file:
                for chunk in request.iter_content(chunk_size=chunk_size):
                    if chunk:  # filter out keep-alive new chunks
                        file.write(chunk)

    def _upload(self, dataset):
        """ Upload the downloaded dataset file to S3 """

        local_file = "/tmp/" + dataset

        s3_conn = boto3.client("s3")
        with gzip.open(local_file, "rb") as file:
            s3_conn.upload_fileobj(file, self.s3_bucket, dataset)
