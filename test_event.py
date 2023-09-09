import unittest
import boto3  # AWS SDK for Python
from moto import mock_dynamodb, mock_sts  # since we're going to mock DynamoDB service
import sys
import moto
from shared_test.test_initialization.table_initialiazer.group_events_initializer.GroupEventTableInitializer import GroupEventTableInitializer

region = 'us-west-2'
comparison_directory = "tmp"

@mock_dynamodb
class AddEventTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.mock_dynamodb = moto.mock_dynamodb()
        cls.mock_dynamodb.start()
        cls.dynamodb = boto3.resource('dynamodb', region_name=region)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.mock_dynamodb.stop()

    def setUp(self):
        """
        Create database resource and mock table
        """

        self.events_table = GroupEventTableInitializer(self.dynamodb)

    def tearDown(self) -> None:
        """
        Delete database resource and mock table
        """
        self.events_table.delete()

    def test_add_event_successful(self):

        payload = {
            "event": {
                "local_start_time": "10:00",
                "local_end_time": "12:00",
                "created_at": "2022-10-08T11:34"
            }, 
            "group_id": "111",
            "local_date": "2022-10-01"
        }
        from API.shared.add_event import lambda_handler
        lambda_handler({"body": payload}, None)
        events = self.events_table.scan_table()

        self.assertEqual(len(events), 1)

if __name__ == '__main__':
    unittest.main()
