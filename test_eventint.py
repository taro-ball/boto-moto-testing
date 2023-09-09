import unittest
import requests
import boto3
import json
import datetime
# run with 'AWS_PROFILE=test python script.py'
# qestion, do we have a 'GetEvent' API? want to avoid coupling tests with ddb

class IntegrationTestAddEvent(unittest.TestCase):
    def get_api_url(self, stack_name):
        client = boto3.client('cloudformation')
        response = client.describe_stacks(StackName=stack_name)
        outputs = response["Stacks"][0]["Outputs"]
        #print("~~~~~~~~~~~~~~~~",outputs[0]["OutputValue"])
        return outputs[0]["OutputValue"]

    def setUp(self):
        """Preparation for test case execution."""
        self.api_endpoint = self.get_api_url('data-integration-test')
        self.group_id = str(int(datetime.datetime.now().timestamp()))
        # Initialize dynamodb resource and table once
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table('group_events')

    def tearDown(self):
        """Clean up after test case execution."""
        # We might want to cron batch-clean of the table instead of removing one-by one
        # response = self.table.delete_item(Key={'group_id': str(self.group_id)})
        # print(response)

    def query_api_endpoint(self, payload):
        """Method to handle the POST request to the API endpoint."""
        print(f"quering {self.api_endpoint}")
        headers = {'content-type': 'application/json'}
        response = requests.post(self.api_endpoint, data=json.dumps(payload), headers=headers)
        return response

    def query_dynamo_db(self):
        """Method to handle querying DynamoDB."""
        response = self.table.query(KeyConditionExpression=boto3.dynamodb.conditions.Key('group_id').eq(self.group_id))
        return response

    def test_api_endpoint(self):
        """Main test case."""
        payload = {
            "event": {
                "local_start_time": "10:00",
                "local_end_time": "12:00",
                "created_at": "2022-10-08T11:34"
            }, 
            "group_id": str(self.group_id),
            "local_date": "2022-10-01"
        }

        # Query the endpoint
        response = self.query_api_endpoint(payload)
        # Check that the API Gateway responded with a 200 OK status
        self.assertEqual(response.status_code, 200)
        print(f'\nAPI response: {response.status_code} {response.json()}\n')

        # Query dynamodb
        response = self.query_dynamo_db()
        # Ensure that there are items in the response
        self.assertGreater(len(response['Items']), 0)
        print('ddb item: ',response['Items'][0])

if __name__ == "__main__":
    unittest.main()
