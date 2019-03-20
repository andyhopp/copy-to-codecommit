# CopyRepoToCodeCommit

This Lambda is designed to copy the contents from a publicly-accessible Git repository to a CodeCommit repo. In practice, it's very similar to a fork of the repo to CodeCommit.

This version is intended to be used as a CloudFormation Custom Resource and will look for two properties:
* SourceRepositoryUrl - the https URL to the repo that contains the source code.
* TargetRepositoryName - the name of a CodeCommit repository
