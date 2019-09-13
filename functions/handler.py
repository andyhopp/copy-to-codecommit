import os
import tempfile
import json
import subprocess
import boto3
import requests

def lambda_handler(event, context):
    if event["RequestType"] == 'Delete':
        respond_cloudformation(event, "SUCCESS")
        return "Handled Delete operation successfully."

    if event["RequestType"] == 'Update':
        respond_cloudformation(event, "SUCCESS")
        return "Handled Update operation successfully."

    # Validation
    if event["ResourceProperties"] is None:
        respond_cloudformation(event, "FAILED")
        return "Invalid request structure: expected 'ResourceProperties' member on the event."

    if event["ResourceProperties"]["SourceRepositoryUrl"] is None:
        respond_cloudformation(event, "FAILED")
        return "Invalid request structure: expected 'SourceRepositoryUrl' resource property."

    if event["ResourceProperties"]["TargetRepositoryName"] is None:
        respond_cloudformation(event, "FAILED")
        return "Invalid request structure: expected 'TargetRepositoryName' resource property."

    codecommit = boto3.client('codecommit')
    try:
        repo = codecommit.get_repository(repositoryName=event["ResourceProperties"]["TargetRepositoryName"])
    except Exception as e:
        error_message = "Unable to fetch target repository information:\n{}".format(e)
        print(error_message)
        respond_cloudformation(event, "FAILED", e)
        return

    target_url = repo["repositoryMetadata"]["cloneUrlHttp"]
    target_branch = event["ResourceProperties"]["TargetRepositoryBranch"] if "TargetRepositoryBranch" in event["ResourceProperties"] else "master"
    source_branch = event["ResourceProperties"]["SourceRepositoryBranch"] if "SourceRepositoryBranch" in event["ResourceProperties"] else "master"
    
    try:
        os.environ["PATH"] = os.environ["PATH"] + ":/opt/awscli"
        temp_dir = tempfile.mkdtemp(prefix='codecommit-fork-')
        os.environ["HOME"] = temp_dir
        
        subprocess.run(["git", "config", "--global", "credential.helper", "!aws codecommit credential-helper $@"], check=True)  
        subprocess.run(["git", "config", "--global", "credential.UseHttpPath", "true"], check=True)
        
        os.chdir(temp_dir)
        print("Cloning from {}".format(event["ResourceProperties"]["SourceRepositoryUrl"]))
        subprocess.run(["git", "clone", event["ResourceProperties"]["SourceRepositoryUrl"]], check=True)

        dir_name = os.path.splitext(os.path.basename(event["ResourceProperties"]["SourceRepositoryUrl"]))[0]
        os.chdir(dir_name)

        print("Adding remote '{}'".format(target_url))
        subprocess.run(["git", "remote", "add", "target-repo", target_url], check=True)
        print("Pushing to remote...")
        subprocess.run(["git", "push", "target-repo", ":".join([source_branch, target_branch])], check=True)
        
        print("Done!")

        respond_cloudformation(event, "SUCCESS")
    except Exception as e:
        error_message = "Unexpected error:\n{}".format(e)
        print(error_message)
        respond_cloudformation(event, "FAILED", e)
        return error_message
    return "Handled Create operation successfully."

def respond_cloudformation(event, status, data=None):
    responseBody = {
        'Status': status,
        'Reason': 'See the details in CloudWatch Log Stream',
        'PhysicalResourceId': 'Custom Lambda Function',
        'StackId': event['StackId'],
        'RequestId': event['RequestId'],
        'LogicalResourceId': event['LogicalResourceId'],
        'Data': data
    }

    print('Response = ' + json.dumps(responseBody))
    requests.put(event['ResponseURL'], data=json.dumps(responseBody))