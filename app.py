#!/usr/bin/env python3
import os
from dotenv import load_dotenv
# load our env file
print ('Loading env file')
load_dotenv("./env")

import aws_cdk as cdk

from reverse_proxy.reverse_proxy_stack import ReverseProxyStack


app = cdk.App()
ReverseProxyStack(app, "ReverseProxyStack",
    env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
   )

# synthesize it
print ('Synthesizing stack')
app.synth()
