# -*- coding: utf-8 -*-
"""
Handles imdb datasets download
1. Get all datasets
2. Store in S3 bucket
"""

import logging
import gzip
import time
import json
import os
from io import BytesIO

import requests
import boto3

from boto3.s3.transfer import TransferConfig

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

class ImdbDatasetHandler:
    """ Class to handle the download of the files """

    def __init__(self):
        self.basedir = os.getenv("BASEDIR", "/tmp/")
        self.base_url = os.getenv(
            "IMDB_DATASET_BASE_URL", "https://datasets.imdbws.com/"
        )
        self.s3_bucket = os.getenv("STORAGE_BUCKET")
        self.datasets = os.getenv("IMDB_DATASET_FILES").split(
            ";"
        )  # this is ; separated list
        self.sf_client = boto3.client("stepfunctions")
        self.s3_client = boto3.client("s3")

    def handle(self):
        """ Process all datasets """

        LOGGER.debug("Datasets to process '%s'", self.datasets)

        for dataset in self.datasets:
            LOGGER.info("Start processing '%s'", dataset)

            self._download(dataset)
            self._upload(dataset)
            self._start_workflow(dataset)

            LOGGER.info("End processing '%s'", dataset)

    def _download(self, dataset):
        """ Download imdb file dataset """

        url = self.base_url + dataset
        local_file = self.basedir + dataset

        LOGGER.debug("Download file from '%s' to '%s'", url, local_file)

        # Use a chunk size of 50 MiB (feel free to change this)
        chunk_size = 52428800

        # NOTE the stream=True parameter below
        with requests.get(url, stream=True) as request:
            request.raise_for_status()
            with open(local_file, "wb") as file:
                for chunk in request.iter_content(chunk_size=chunk_size):
                    if chunk:  # filter out keep-alive new chunks
                        file.write(chunk)

        LOGGER.debug("Finish the download, total size: %s", os.path.getsize(local_file))

    def _upload(self, dataset):
        """ Upload the downloaded dataset file to S3 """

        LOGGER.debug("Upload uncompress file to S3")

        config = TransferConfig(
            multipart_threshold=1024 * 25,
            max_concurrency=10,
            multipart_chunksize=1024 * 25,
            use_threads=True,
        )

        filename = dataset
        file_fulpath = self.basedir + filename

        LOGGER.debug(
            "Uploaded file '%s' to '%s'",
            file_fulpath,
            (self.s3_bucket + "/" + filename),
        )

        s3_conn = boto3.resource("s3")
        s3_conn.meta.client.upload_file(
            file_fulpath,
            self.s3_bucket,
            filename,
            ExtraArgs={"ACL": "public-read", "ContentType": "text/tsv"},
            Config=config,
        )

    def _start_workflow(self, dataset):
        self._call_state_machine(dataset.replace(".gz", ""))

    def _call_state_machine(self, filename):
        """ Calls the State Machine """

        state_machine_arn = os.getenv("IMDB_DATASET_STATE_MACHINE")

        try:
            response = self.sf_client.start_execution(
                stateMachineArn=state_machine_arn,
                name=self._get_execution_name(filename),
                input=self._get_state_machine_input(filename)
            )
        except:
            LOGGER.exception("Error executing state machine for dataset: '%s'", filename)
            raise
        else:
            LOGGER.info("State machine executed. Response: %s", response)

    @staticmethod
    def _get_execution_name(filename):
        return filename + "_" + str(time.time())

    @staticmethod
    def _get_state_machine_input(filename):
        return json.dumps({"dataset": filename})
    