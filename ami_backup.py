import boto3
import yaml
import datetime

# Load config
with open("config.yaml") as f:
    config = yaml.safe_load(f)

REGION = config["aws_region"]
INSTANCES = config["instances"]
RETENTION = config["retention_days"]
BACKUP_TAG = config["backup_tag"]

ec2 = boto3.client("ec2", region_name=REGION)

def create_ami(instance_id):
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d-%H-%M")
    ami_name = f"{BACKUP_TAG}-{instance_id}-{timestamp}"

    print(f"Creating AMI for {instance_id}...")
    response = ec2.create_image(
        InstanceId=instance_id,
        Name=ami_name,
        NoReboot=True
    )

    ami_id = response["ImageId"]

    ec2.create_tags(
        Resources=[ami_id],
        Tags=[
            {"Key": "CreatedBy", "Value": BACKUP_TAG},
            {"Key": "InstanceId", "Value": instance_id}
        ]
    )

    print(f"AMI created: {ami_id}")

def cleanup_old_amis():
    print("Checking for old AMIs...")

    images = ec2.describe_images(
        Owners=["self"],
        Filters=[
            {"Name": "tag:CreatedBy", "Values": [BACKUP_TAG]}
        ]
    )["Images"]

    cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=RETENTION)

    for image in images:
        creation_date = datetime.datetime.strptime(
            image["CreationDate"], "%Y-%m-%dT%H:%M:%S.%fZ"
        )

        if creation_date < cutoff:
            ami_id = image["ImageId"]
            print(f"Deleting old AMI: {ami_id}")

            # Delete snapshots linked to AMI
            for bd in image.get("BlockDeviceMappings", []):
                if "Ebs" in bd:
                    snap_id = bd["Ebs"]["SnapshotId"]
                    ec2.delete_snapshot(SnapshotId=snap_id)
                    print(f"Deleted snapshot: {snap_id}")

            ec2.deregister_image(ImageId=ami_id)
            print(f"Deregistered AMI: {ami_id}")

def main():
    for instance in INSTANCES:
        create_ami(instance)

    cleanup_old_amis()

if __name__ == "__main__":
    main()
