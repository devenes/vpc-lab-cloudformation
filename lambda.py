import boto3
import json
import logging
import threading
import cfnresponse

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)


def handler(event, context):
    # Send a failure to CloudFormation if the function timesout
    timer = threading.Timer((context.get_remaining_time_in_millis()
                            / 1000.00) - 0.5, timeout, args=[event, context])
    timer.start()

    try:
        # Loop through regions
        ec2 = boto3.client('ec2')
        regions = ['us-east-1', 'us-west-2']
        for region in regions:

            # SSM Client
            ssm = boto3.client('ssm', region_name=region)

            # Get all Parameter Store parameters for region
            get_region_params = ssm.describe_parameters()
            names = [p['Name']
                     for p in get_region_params['Parameters']]
            print(region, names)

            # Delete them
            if len(names) > 0:
                del_region_params = ssm.delete_parameters(
                    Names=names)
            else:
                print(('No parameters to delete in region ' + region))

        cfnresponse.send(event, context, cfnresponse.SUCCESS, {
            "Message": "Resource creation successful!"}, None)
    except:
        cfnresponse.send(event, context, cfnresponse.FAILED, {
            "Message": "Problem deleting parameters!"}, None)


def timeout(event, context):
    logging.error(
        "Execution is about to time out, sending failure response to CloudFormation")
    cfnresponse.send(event, context, cfnresponse.FAILED, {}, None)
