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

from boto3.s3.transfer import TransferConfig

LOG = logging.getLogger("ImdbDatasetsHandler")


class ImdbDatasetsHandler:
    """ Class to handle the download of the files """

    def __init__(self):
        self.basedir = os.getenv("BASEDIR", "/tmp/")
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
        local_file = self.basedir + dataset

        # Use a chunk size of 50 MiB (feel free to change this)
        chunk_size = 52428800

        # NOTE the stream=True parameter below
        with requests.get(url, stream=True) as request:
            request.raise_for_status()
            with open(local_file, "wb") as file:
                for chunk in request.iter_content(chunk_size=chunk_size):
                    if chunk:  # filter out keep-alive new chunks
                        file.write(chunk)

        # Uncompress File
        uncompress_file = open(local_file.replace(".gz", ""), "wb")
        with gzip.open(local_file, "rb") as file:
            bindata = file.read()
        uncompress_file.write(bindata)
        uncompress_file.close()

    def _upload(self, dataset):
        """ Upload the downloaded dataset file to S3 """

        config = TransferConfig(
            multipart_threshold=1024 * 25,
            max_concurrency=10,
            multipart_chunksize=1024 * 25,
            use_threads=True,
        )

        filename = dataset.replace(".gz", "")
        file_fulpath = self.basedir + filename

        s3 = boto3.resource('s3')
        s3.meta.client.upload_file(file_fulpath, self.s3_bucket, filename,
                           ExtraArgs={'ACL': 'public-read', 'ContentType': 'text/pdf'},
                           Config=config)
