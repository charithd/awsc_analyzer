# aws_analyzer
Python (Boto3) tool that analyzes AWS volumes ,snapshots, AMIs, ELBs and generates comprehensive reports with details to AWS Cost Optimization.

## Getting Started

These instructions will get you a copy of the Tool up and running on your local machine.

### Prerequisites

* Install Boto3
* AWS credentials should configure on  ~/.aws/credentials [You need only read permission to aws resources]

Ref: https://boto3.readthedocs.io/en/latest/guide/quickstart.html

```
pip install boto3
```

### Running the Tool

Clone the Tool and run as below

```
./aws_analyzer_v1.1.py [acountid] [region]
```
-Account id is necessary to get snapshots infomation

### Execution and summary output

```
./aws_analyzer_v1.1.py 34534533 us-west-1
``` 
![alt text](https://github.com/charithd/aws_analyzer/blob/master/aws-analyzer_out.png)

### Reports
The tool will generate 4 reports:

```
[acountid]-[region]_vol-[timestamp].csv :- All volumes information
[acountid]-[region]_snap-[timestamp].csv :- All snapshots information
[acountid]-[region]_ami-[timestamp].csv :- All AMIs information
[acountid]-[region]_elb-[timestamp].csv :- All ELBs information
```
