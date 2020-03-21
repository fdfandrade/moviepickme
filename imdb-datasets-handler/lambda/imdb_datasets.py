# -*- coding: utf-8 -*-
"""
Contains the lambda handler
"""

import imdb_datasets_handler

# pylint: disable=W0613
def lambda_handler(event, context):
    """
    Lambda function to be called by the CW rule
    """

    handler = imdb_datasets_handler.ImdbDatasetsHandler()
    handler.process()
