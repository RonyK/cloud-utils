"""
CloudWatch Metrics Client Usage Examples

This file demonstrates how to use CloudWatch Metrics synchronous and asynchronous clients.
"""

import asyncio
import datetime
from typing import List

# Synchronous client usage example
def sync_cloudwatch_example():
    """Synchronous CloudWatch client usage example"""
    from cloud_utils.providers.aws import (
        CloudWatchMetricsClient, 
        MetricDimension, 
        MetricQuery
    )
    
    # Initialize client
    client = CloudWatchMetricsClient(region_name="ap-northeast-2")
    
    # Define metric dimensions
    dimensions = [
        MetricDimension("Service", "processor"),
        MetricDimension("Stage", "prod"),
        MetricDimension("Environment", "production")
    ]
    
    # Create metric queries
    queries = [
        MetricQuery(
            namespace="MyApp/Metrics",
            metric_name="ResourcesProcessed",
            dimensions=dimensions,
            period=60,
            stat="Sum",
            unit="Count"
        ),
        # Calculate per-second processing rate using Metric Math
        MetricQuery(
            namespace="MyApp/Metrics",
            metric_name="ResourcesProcessed",
            dimensions=dimensions,
            period=60,
            stat="Sum",
            expression="query_0 / PERIOD(query_0)",  # per-minute sum / 60 seconds = per-second
            label="ResourcesProcessed per second"
        )
    ]
    
    # Set time range
    end_time = datetime.datetime.now(datetime.timezone.utc)
    start_time = end_time - datetime.timedelta(hours=24)
    
    try:
        # Retrieve multiple metrics at once (recommended method)
        print("=== get_metric_data usage example ===")
        series = client.get_metric_data(queries, start_time, end_time)
        
        for query_id, data_points in series.items():
            print(f"\n{query_id}:")
            for timestamp, value in data_points[:5]:  # Show first 5 only
                print(f"  {timestamp}: {value}")
        
        # Retrieve single metric statistics (legacy method)
        print("\n=== get_metric_statistics usage example ===")
        datapoints = client.get_metric_statistics(
            namespace="MyApp/Metrics",
            metric_name="ResourcesProcessed",
            dimensions=dimensions,
            start_time=start_time,
            end_time=end_time,
            period=60,
            statistics=["Sum", "Average", "Maximum"],
            unit="Count"
        )
        
        print(f"Number of data points: {len(datapoints)}")
        for point in datapoints[:3]:  # Show first 3 only
            print(f"  {point['Timestamp']}: Sum={point['Sum']}, Avg={point['Average']}, Max={point['Maximum']}")
        
        # List available metrics
        print("\n=== list_metrics usage example ===")
        metrics = client.list_metrics(
            namespace="MyApp/Metrics",
            recently_active="PT3H"
        )
        
        print(f"Number of active metrics: {len(metrics)}")
        for metric in metrics[:3]:  # Show first 3 only
            print(f"  {metric['MetricName']}: {metric['Dimensions']}")
        
        # Publish custom metric
        print("\n=== Custom metric publishing example ===")
        client.create_custom_metric(
            namespace="MyApp/CustomMetrics",
            metric_name="UserLoginCount",
            dimensions=[
                MetricDimension("UserType", "premium"),
                MetricDimension("Region", "ap-northeast-2")
            ],
            value=42,
            unit="Count"
        )
        print("Custom metric published successfully")
        
    except Exception as e:
        print(f"Error occurred: {e}")


# Asynchronous client usage example
async def async_cloudwatch_example():
    """Asynchronous CloudWatch client usage example"""
    from cloud_utils.providers.aws import (
        AsyncCloudWatchMetricsClient, 
        MetricDimension, 
        MetricQuery
    )
    
    # Initialize client
    client = AsyncCloudWatchMetricsClient(region_name="ap-northeast-2")
    
    # Define metric dimensions
    dimensions = [
        MetricDimension("Service", "api-gateway"),
        MetricDimension("Stage", "prod"),
        MetricDimension("Method", "GET")
    ]
    
    # Create metric queries
    queries = [
        MetricQuery(
            namespace="AWS/ApiGateway",
            metric_name="Count",
            dimensions=dimensions,
            period=300,  # 5 minutes
            stat="Sum",
            unit="Count"
        ),
        MetricQuery(
            namespace="AWS/ApiGateway",
            metric_name="Latency",
            dimensions=dimensions,
            period=300,
            stat="Average",
            unit="Milliseconds"
        )
    ]
    
    # Set time range
    end_time = datetime.datetime.now(datetime.timezone.utc)
    start_time = end_time - datetime.timedelta(hours=6)
    
    try:
        # Retrieve multiple metrics asynchronously
        print("=== Asynchronous get_metric_data usage example ===")
        series = await client.get_metric_data(queries, start_time, end_time)
        
        for query_id, data_points in series.items():
            print(f"\n{query_id}:")
            for timestamp, value in data_points[:5]:  # Show first 5 only
                print(f"  {timestamp}: {value}")
        
        # Retrieve single metric statistics asynchronously
        print("\n=== Asynchronous get_metric_statistics usage example ===")
        datapoints = await client.get_metric_statistics(
            namespace="AWS/ApiGateway",
            metric_name="Count",
            dimensions=dimensions,
            start_time=start_time,
            end_time=end_time,
            period=300,
            statistics=["Sum", "Average"],
            unit="Count"
        )
        
        print(f"Number of data points: {len(datapoints)}")
        for point in datapoints[:3]:  # Show first 3 only
            print(f"  {point['Timestamp']}: Sum={point['Sum']}, Avg={point['Average']}")
        
        # List available metrics asynchronously
        print("\n=== Asynchronous list_metrics usage example ===")
        metrics = await client.list_metrics(
            namespace="AWS/ApiGateway",
            recently_active="PT1H"
        )
        
        print(f"Number of active metrics: {len(metrics)}")
        for metric in metrics[:3]:  # Show first 3 only
            print(f"  {metric['MetricName']}: {metric['Dimensions']}")
        
        # Publish custom metric asynchronously
        print("\n=== Asynchronous custom metric publishing example ===")
        await client.create_custom_metric(
            namespace="MyApp/AsyncMetrics",
            metric_name="AsyncOperationCount",
            dimensions=[
                MetricDimension("OperationType", "database"),
                MetricDimension("Status", "success")
            ],
            value=100,
            unit="Count"
        )
        print("Asynchronous custom metric published successfully")
        
    except Exception as e:
        print(f"Error occurred: {e}")


# Advanced usage example: Retrieve metrics from multiple services simultaneously
async def advanced_metrics_example():
    """Advanced metrics retrieval example: Retrieve metrics from multiple services simultaneously"""
    from cloud_utils.providers.aws import (
        AsyncCloudWatchMetricsClient, 
        MetricDimension, 
        MetricQuery
    )
    
    client = AsyncCloudWatchMetricsClient(region_name="ap-northeast-2")
    
    # Retrieve metrics from multiple services simultaneously
    queries = [
        # EC2 CPU utilization
        MetricQuery(
            namespace="AWS/EC2",
            metric_name="CPUUtilization",
            dimensions=[MetricDimension("InstanceId", "i-1234567890abcdef0")],
            period=300,
            stat="Average",
            unit="Percent"
        ),
        # RDS connection count
        MetricQuery(
            namespace="AWS/RDS",
            metric_name="DatabaseConnections",
            dimensions=[MetricDimension("DBInstanceIdentifier", "my-db-instance")],
            period=300,
            stat="Average",
            unit="Count"
        ),
        # S3 bucket size
        MetricQuery(
            namespace="AWS/S3",
            metric_name="BucketSizeBytes",
            dimensions=[
                MetricDimension("BucketName", "my-bucket"),
                MetricDimension("StorageType", "StandardStorage")
            ],
            period=86400,  # 24 hours
            stat="Average",
            unit="Bytes"
        ),
        # Lambda execution time
        MetricQuery(
            namespace="AWS/Lambda",
            metric_name="Duration",
            dimensions=[MetricDimension("FunctionName", "my-lambda-function")],
            period=300,
            stat="Average",
            unit="Milliseconds"
        )
    ]
    
    end_time = datetime.datetime.now(datetime.timezone.utc)
    start_time = end_time - datetime.timedelta(hours=12)
    
    try:
        print("=== Multi-service metrics simultaneous retrieval example ===")
        series = await client.get_metric_data(queries, start_time, end_time)
        
        for query_id, data_points in series.items():
            if data_points:
                print(f"\n{query_id}:")
                print(f"  Number of data points: {len(data_points)}")
                print(f"  First value: {data_points[0]}")
                print(f"  Last value: {data_points[-1]}")
            else:
                print(f"\n{query_id}: No data")
                
    except Exception as e:
        print(f"Error occurred: {e}")


def main():
    """Main function"""
    print("CloudWatch Metrics Client Usage Examples")
    print("=" * 50)
    
    # Run synchronous examples
    print("\n1. Synchronous client examples")
    sync_cloudwatch_example()
    
    # Run asynchronous examples
    print("\n\n2. Asynchronous client examples")
    asyncio.run(async_cloudwatch_example())
    
    # Run advanced examples
    print("\n\n3. Advanced metrics retrieval examples")
    asyncio.run(advanced_metrics_example())


if __name__ == "__main__":
    main()


