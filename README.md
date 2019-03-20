# CopyRepoToCodeCommit

This Lambda is designed to copy the contents from a publicly-accessible Git repository to a CodeCommit repo. In practice, it's very similar to a fork of the repo to CodeCommit.

This version is intended to be used as a CloudFormation Custom Resource and will look for two properties:
* SourceRepositoryUrl - the https URL to the repo that contains the source code.
* TargetRepositoryName - the name of a CodeCommit repository

## Example Usage
``` yaml
  Repository:
    Type: AWS::CodeCommit::Repository
    Properties: 
      RepositoryName: !Sub ${AWS::StackName}-repo
      RepositoryDescription: My CodeCommit repository

  CopyRepoToCodeCommitFunction:
    Type: AWS::Serverless::Application
    Properties:
      Location:
        ApplicationId: arn:aws:serverlessrepo:us-east-1:982831078337:applications/CopyRepoToCodeCommit
        SemanticVersion: 1.0.2
  
  ForkRepo:
    Type: Custom::ForkRepo
    DependsOn: [ CopyRepoToCodeCommitFunction, Repository]
    Properties:
      ServiceToken: !GetAtt CopyRepoToCodeCommitFunction.Outputs.FunctionArn
      SourceRepositoryUrl: https://github.com/andyhopp/eShopOnWeb # <-- Your repo URL goes here!
      TargetRepositoryName: !GetAtt Repository.Name
```