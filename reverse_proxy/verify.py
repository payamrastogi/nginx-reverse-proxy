import aws_cdk
from aws_cdk import aws_s3 as s3
print(s3)
import boto3
print (boto3.__version__)
import os
import dotenv

from dotenv import load_dotenv

def get_aws_keys():
    load_dotenv()
    return os.getenv('AWS_ACCESS_KEY'), os.getenv('AWS_SECRET_KEY')

def init_aws_session():
    access_key, secret_key = get_aws_keys()
    return boto3.Session(aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name=os.getenv('AWS_REGION'))


session = init_aws_session()
creds = session.get_credentials()
print ('Access key: ', creds.access_key)
print ('Secret key: ', creds.secret_key)
print ('Region: ', session.region_name)
print ('Profile: ', session.profile_name)