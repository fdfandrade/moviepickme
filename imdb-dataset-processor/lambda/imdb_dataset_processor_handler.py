# -*- coding: utf-8 -*-
"""
Handles the process of an individual dataset
"""

import logging
import time
import os
import json
import gzip
import boto3

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

class ImdbDatasetProcessorHandler:
    """ Handle data inside """

    def __init__(self, dataset):
        self.s3_bucket = os.getenv("STORAGE_BUCKET")
        self.dataset = dataset
        self.sf_client = boto3.client("stepfunctions")
        self.s3_client = boto3.client("s3")

    def handle(self):
        """ Process dataset """

        LOGGER.debug("Processing dataset: '%s'", self.dataset)

        obj = self.s3_client.get_object(Bucket=self.s3_bucket, Key=self.dataset)

        body = obj["Body"]

        with gzip.open(body, "rt", encoding="utf-8") as file_content:
            # jump header line
            header = next(file_content).replace("\n", "").split("\t")

            for line in file_content:
                line = line.replace("\n", "").split("\t")
                self.call_state_machine(
                    self._input(header, line)
                )

    def call_state_machine(self, sm_input):
        """ Calls the State Machine """

        state_machine_arn = os.getenv("IMDB_TITLE_STATE_MACHINE")

        try:
            response = self.sf_client.start_execution(
                stateMachineArn=state_machine_arn,
                name=self.dataset + "_" + str(time.time()),
                input=sm_input,
            )
        except:
            LOGGER.exception(
                "Error executing state machine for dataset: '%s'", self.dataset
            )
            raise
        else:
            LOGGER.info("State machine executed. Response: %s", response)

    @staticmethod
    def _input(header, line):
        """ build input to send to statemachine """
        result = {}

        for idx, key in enumerate(header):
            result[key] = line[idx]

        return json.dumps(result)
