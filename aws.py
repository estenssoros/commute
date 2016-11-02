import boto.dynamodb
import boto
import os


def aws_keys():
    env = os.environ
    access_key = env['AWS_ACCESS_KEY_ID']
    access_secret_key = env['AWS_SECRET_ACCESS_KEY']
    return access_key, access_secret_key

def connect_s3():
    access_key, access_secret_key = aws_keys()
    conn = boto.connect_s3(access_key, access_secret_key, calling_format=OrdinaryCallingFormat())
    bucket_name = 'sebsbucket'
    for bucket in conn.get_all_buckets():
        if bucket.name == bucket_name:
            break
    return bucket

def connect_dynamodb():
    access_key, secret_key = aws_keys()
    conn = boto.dynamodb.connect_to_region(
        'us-east-1', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
    table = conn.get_table('commute')
    return table


def upload_s3(fname):
    bucket = connect_s3()
    key = bucket.new_key('commute/' + fname)
    key.set_contents_from_filename(fname)
    print '    -File uploaded to S3!'

if __name__ == '__main__':
    pass
