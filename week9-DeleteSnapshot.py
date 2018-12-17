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

#begin snapshot deletion function
def lambda_handler(event, context):    
    for snapshot in snapshots['Snapshots']:
        snapshot_start_time = snapshot['StartTime']
        snapshot_ID = snapshot['SnapshotId']
        snapshot_date = snapshot_start_time.strftime('%A, %m/%d/%Y')
        snapshot_time = snapshot_start_time.replace(tzinfo=None)
        snapshot_time_string = snapshot_start_time.strftime('%I:%M:%S %p %Z %z')
        current_time = datetime.datetime.now().replace(tzinfo=None)
        time_difference = current_time - snapshot_time

        #function to get difference of days between current time and snapshot age
        def days_old(date):
            diff = datetime.datetime.now() - snapshot_time
            return diff.days
        
        #current state of volume's snapshots
        print ('***Snapshot exists for Volume ID: %s. The Snapshot ID is %s, and it was created on %s at %s. Current age of snapshot: %s'% (
        volume, snapshot_ID, snapshot_date, snapshot_time_string, time_difference))
        
        if snapshot['VolumeId'] == volume:
            
            #passing start time of snapshot to days_old function
            day_old = days_old(snapshot_start_time)
            
            #comparing age of snapshot with compliance age
            if day_old < compliance_backup_age:
                try:
                    print ('***Snapshot for Volume ID: %s is older than %s day(s). Current age of snapshot: %s '% (
                    volume, compliance_backup_age, time_difference))
                    ec2.delete_snapshot(SnapshotId=snapshot['SnapshotId'])
                    print ('***snapshot ID: %s was deleted'% (snapshot['SnapshotId'])) 
                except:
                    print ('***Snapshot for Volume ID: %s is not older than %s day(s). Current age of snapshot: %s '% (
                    volume, compliance_backup_age, time_difference))
                    print('***snapshot ID: %s was NOT deleted'% (snapshot['SnapshotId'])) 