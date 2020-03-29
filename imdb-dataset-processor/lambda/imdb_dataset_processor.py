# -*- coding: utf-8 -*-
"""
Contains the lambda handler
"""
import time

import imdb_dataset_processor_handler

# pylint: disable=W0613
def lambda_handler(event, context):
    """
    Lambda function to be called by imdb dataset handler
    """

    handler = imdb_dataset_processor_handler.ImdbDatasetProcessorHandler(event['dataset'])

    start = time.time()
    handler.handle()
    end = time.time()

    return {
        "timetaken": end - start
    }
