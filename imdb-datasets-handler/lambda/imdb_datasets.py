# -*- coding: utf-8 -*-
"""
Contains the lambda handler
"""
import time

import imdb_datasets_handler

# pylint: disable=W0613
def lambda_handler(event, context):
    """
    Lambda function to be called by the CW rule
    """

    handler = imdb_datasets_handler.ImdbDatasetsHandler()

    start = time.time()
    handler.process()
    end = time.time()

    return {
        "timetaken": end - start
    }
