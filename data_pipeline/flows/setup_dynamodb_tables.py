#!/usr/bin/env python3
"""
Script to create DynamoDB tables for LocalGaid application.
Run this script once to set up the required tables before using the production database flow.
"""

import boto3
from botocore.exceptions import ClientError
from prefect_aws import AwsCredentials


def create_places_table(dynamodb, table_name: str = "localgaid-places"):
    """Create the places table with appropriate schema."""
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'name',
                    'AttributeType': 'S'
                }
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'name-index',
                    'KeySchema': [
                        {
                            'AttributeName': 'name',
                            'KeyType': 'HASH'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    },
                    'BillingMode': 'PAY_PER_REQUEST'
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        print(f"Creating table {table_name}...")
        table.wait_until_exists()
        print(f"Table {table_name} created successfully!")
        return table
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"Table {table_name} already exists.")
            return dynamodb.Table(table_name)
        else:
            print(f"Error creating table {table_name}: {e}")
            raise


def create_audio_guides_table(dynamodb, table_name: str = "localgaid-audio-guides"):
    """Create the audio guides table with appropriate schema."""
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'place_id',
                    'AttributeType': 'S'
                }
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'place-id-index',
                    'KeySchema': [
                        {
                            'AttributeName': 'place_id',
                            'KeyType': 'HASH'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    },
                    'BillingMode': 'PAY_PER_REQUEST'
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        print(f"Creating table {table_name}...")
        table.wait_until_exists()
        print(f"Table {table_name} created successfully!")
        return table
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"Table {table_name} already exists.")
            return dynamodb.Table(table_name)
        else:
            print(f"Error creating table {table_name}: {e}")
            raise


def setup_dynamodb_tables(aws_credentials_block_name: str = "localgaid-aws-credentials",
                         places_table_name: str = "localgaid-places",
                         audio_guides_table_name: str = "localgaid-audio-guides"):
    """Set up all required DynamoDB tables for LocalGaid."""
    
    print("Setting up DynamoDB tables for LocalGaid...")
    
    # Load AWS credentials
    aws_credentials = AwsCredentials.load(aws_credentials_block_name)
    
    # Create DynamoDB resource
    dynamodb = boto3.resource(
        'dynamodb',
        aws_access_key_id=aws_credentials.aws_access_key_id,
        aws_secret_access_key=aws_credentials.aws_secret_access_key.get_secret_value(),
        region_name=aws_credentials.region_name or 'us-east-1'
    )
    
    # Create tables
    places_table = create_places_table(dynamodb, places_table_name)
    audio_guides_table = create_audio_guides_table(dynamodb, audio_guides_table_name)
    
    print("\n" + "="*50)
    print("DynamoDB setup completed!")
    print("="*50)
    print(f"Places table: {places_table_name}")
    print(f"Audio guides table: {audio_guides_table_name}")
    print("\nTable schemas:")
    print(f"- {places_table_name}: id (PK), name, latitude, longitude, images, tags, updated_at")
    print(f"- {audio_guides_table_name}: id (PK), place_id (GSI), title, full_subtitle, audio_url, duration_seconds, subtitle_url, created_at")
    print("\nYou can now run your production database flow!")


if __name__ == "__main__":
    setup_dynamodb_tables()
