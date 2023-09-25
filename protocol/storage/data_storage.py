import logging
import pickle

import boto3
from botocore.exceptions import ClientError


class DataStorage:
    def __init__(self, bucket_name):
        self.bucket = bucket_name
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id="test",
            aws_secret_access_key="test",
            region_name="us-east-1",
            endpoint_url="http://localhost:4566",
        )

    def create_bucket(self):
        self.s3_client.create_bucket(Bucket=self.bucket)

    def save(self, obj, object_name):
        try:
            _ = self.s3_client.put_object(
                Body=obj, Bucket=self.bucket, Key=object_name
            )
        except ClientError as e:
            logging.error(e)
            return False
        return True

    def load(self, storage_key):
        return self.s3_client.get_object(Bucket=self.bucket, Key=storage_key)[
            "Body"
        ].read()

    def store_trace_list(self, task_id, traces):
        trace_locations = {}
        for trace in traces:
            snap_id = trace._exec_mode._snap_id
            snap_key = f"{task_id}_{snap_id}"
            self.save(pickle.dumps(trace), snap_key)
            trace_locations[snap_id] = {"location": snap_key, "trace": trace}
        return trace_locations
