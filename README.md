# AWS EC2 AMI Backup Automation

Automates AMI creation and cleanup of old backups.

## Features
- Creates AMIs for configured EC2 instances
- Tags backups automatically
- Retains only last N days backups
- Deletes old AMIs and snapshots

## Tech Stack
- Python
- Boto3
- AWS EC2
- Cron / Lambda

## Usage
1. Configure AWS CLI
2. Edit config.yaml
3. Install requirements
4. Run python ami_backup.py

## Automation
Can be scheduled using Cron or AWS EventBridge.
