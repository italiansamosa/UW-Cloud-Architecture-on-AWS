import boto3
import collections
import datetime
from datetime import timedelta  

#environment variables
region = 'us-east-1'
ownerID = '569173828921'
#the volume & instance below will have a back up created and deleted based on the compliance back up age variable.
volume = 'vol-04eafdc077430c639'
instance = 'i-06e50b8d03062f533'
compliance_backup_age = 1 

ec2 = boto3.client('ec2', region_name=region) 
snapshots = ec2.describe_snapshots(OwnerIds=[ownerID])

Reservations = ec2.describe_instances().get('Reservations', [])
Instances = sum(
        [
            [i for i in r['Instances']]
            for r in Reservations
        ], [])

#begin function
def lambda_handler(event, context):
    #looping through instances in instance variable
    for instance in Instances:
        #looping through storage in each instance in ebs variable
        for ebs in instance['BlockDeviceMappings']:
            #variable for instance ebs volume id
            volume_id = ebs['Ebs']['VolumeId']
            #If statement to check if ebs volume id matches the volume variable in the variables section. 
            #If the condition is true function creates a snapshot and prints information
            #If condition is not met, function will print information saying so
            if volume_id == volume:
                ec2.create_snapshot(VolumeId=volume)
                print('***Creating snapshot for EBS volume ID: %s, attached to instance %s'% (
                volume_id, instance['InstanceId']))
            else:
                print('***NO snapshot will be created for EBS volume ID: %s, attached to instance %s due to no match'% (
                volume_id, instance['InstanceId']))


