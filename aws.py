import boto.dynamodb
import os

def connect_dynamodb():
    conn = boto.dynamodb.connect_to_region('us-east-1', aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'], aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'])
    table = conn.get_table('commute')
    return table

if __name__ == '__main__':
    pass
