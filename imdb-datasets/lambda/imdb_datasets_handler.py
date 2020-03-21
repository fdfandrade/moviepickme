# -*- coding: utf-8 -*-
"""
Handles imdb datasets download
1. Get all datasets
2. Store in S3 bucket
"""

import logging
import os
import math
import requests
import boto3

from filechunkio import FileChunkIO

LOG = logging.getLogger("ImdbDatasetsHandler")


class ImdbDatasetsHandler:
    """ Class to handle the download of the files """

    def __init__(self):
        self.base_url = os.getenv(
            "IMDB_DATASET_BASE_URL", "https://datasets.imdbws.com/"
        )
        self.aws_id = os.getenv("AWS_ID")  # get this from SSM
        self.aws_secret = os.getenv("AWS_SECRET")  # get this from SSM
        self.s3_bucket = os.getenv("DATASETS_BUCKET")
        self.datasets = os.getenv("IMDB_DATASET_FILES").split(
            ";"
        )  # this is ; separated list

    def process(self):
        """ Process all datasets """

        for dataset in self.datasets:
            self._download(dataset)

    def _download(self, dataset):
        """ Download imdb file dataset and store it in S3 """

        # request = urllib2.Request(self.base_url + dataset)
        # response = urllib2.urlopen(request)

        # Connect to S3
        s3_conn = boto3.client('s3', 'eu-east-1')
        s3_bucket = s3_conn.get_bucket(self.s3_bucket)

        url = self.base_url + dataset

        # NOTE the stream=True parameter below
        with requests.get(url, stream=True) as request:
            request.raise_for_status()
            with open(dataset, "wb") as file:
                for chunk in request.iter_content(chunk_size=8192):
                    if chunk:  # filter out keep-alive new chunks
                        file.write(chunk)
                        # f.flush()


# # Get file info
# source_path = 'path/to/your/file.ext'
# source_size = os.stat(source_path).st_size

# # Create a multipart upload request
# mp = b.initiate_multipart_upload(os.path.basename(source_path))

# # Use a chunk size of 50 MiB (feel free to change this)
# chunk_size = 52428800
# chunk_count = int(math.ceil(source_size / float(chunk_size)))

# # Send the file parts, using FileChunkIO to create a file-like object
# # that points to a certain byte range within the original file. We
# # set bytes to never exceed the original file size.
# for i in range(chunk_count):
#     offset = chunk_size * i
#     bytes = min(chunk_size, source_size - offset)
#     with FileChunkIO(source_path, 'r', offset=offset,
#                          bytes=bytes) as fp:
#         mp.upload_part_from_file(fp, part_num=i + 1)

# # Finish the upload
# mp.complete_upload()
