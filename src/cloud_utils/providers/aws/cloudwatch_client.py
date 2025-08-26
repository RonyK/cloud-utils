"""
Synchronous CloudWatch Metrics Client Module

This module provides a synchronous client for AWS CloudWatch Metrics.
It supports multiple dimensions and both get_metric_data and get_metric_statistics methods.
"""

import datetime
from typing import Any, Dict, List, Optional, Tuple

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from ..exceptions import CloudProviderError, ConfigurationError
from .cloudwatch_models import MetricDimension, MetricQuery


class CloudWatchMetricsClient:
    """Synchronous CloudWatch Metrics Client"""

    def __init__(
        self,
        region_name: Optional[str] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_session_token: Optional[str] = None,
        profile_name: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize CloudWatch Metrics Client

        Args:
            region_name: AWS region name (e.g., 'ap-northeast-2')
            aws_access_key_id: AWS access key ID
            aws_secret_access_key: AWS secret access key
            aws_session_token: AWS session token
            profile_name: AWS profile name
            **kwargs: Additional arguments passed to boto3 client
        """
        try:
            if profile_name:
                session = boto3.Session(profile_name=profile_name)
                self.client = session.client("cloudwatch", region_name=region_name, **kwargs)
            else:
                self.client = boto3.client(
                    "cloudwatch",
                    region_name=region_name,
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key,
                    aws_session_token=aws_session_token,
                    **kwargs
                )
        except NoCredentialsError:
            raise ConfigurationError("AWS credentials not found.")
        except Exception as e:
            raise ConfigurationError("Failed to initialize CloudWatch client: {0}".format(str(e)))

    def get_metric_data(
        self,
        queries: List[MetricQuery],
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        scan_by: str = "TimestampAscending",
        max_datapoints: Optional[int] = None,
    ) -> Dict[str, List[Tuple[datetime.datetime, float]]]:
        """
        Retrieve multiple metrics in one call (recommended method)

        Args:
            queries: List of metric queries
            start_time: Query start time
            end_time: Query end time
            scan_by: Sort order ("TimestampAscending" or "TimestampDescending")
            max_datapoints: Maximum number of data points

        Returns:
            Dictionary containing (timestamp, value) tuple lists for each query ID

        Raises:
            CloudProviderError: When CloudWatch API call fails
        """
        try:
            # Convert to UTC time
            if start_time.tzinfo is None:
                start_time = start_time.replace(tzinfo=datetime.timezone.utc)
            if end_time.tzinfo is None:
                end_time = end_time.replace(tzinfo=datetime.timezone.utc)

            # Create query ID
            query_id_map = {}
            metric_data_queries = []
            
            for i, query in enumerate(queries):
                query_id = "query_{0}".format(i)
                query_id_map[query_id] = query
                metric_data_queries.append(query.to_metric_stat_query(query_id))

            # Initial API call
            response = self.client.get_metric_data(
                StartTime=start_time,
                EndTime=end_time,
                MetricDataQueries=metric_data_queries,
                ScanBy=scan_by,
                MaxDatapoints=max_datapoints,
            )

            # Initialize results
            series: Dict[str, List[Tuple[datetime.datetime, float]]] = {}
            for query_id in query_id_map.keys():
                series[query_id] = []

            # Process first response
            self._process_metric_data_response(response, series)

            # Repeat calls if NextToken exists
            next_token = response.get("NextToken")
            while next_token:
                response = self.client.get_metric_data(
                    StartTime=start_time,
                    EndTime=end_time,
                    MetricDataQueries=metric_data_queries,
                    ScanBy=scan_by,
                    MaxDatapoints=max_datapoints,
                    NextToken=next_token,
                )
                self._process_metric_data_response(response, series)
                next_token = response.get("NextToken")

            return series

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]
            raise CloudProviderError("CloudWatch API error ({0}): {1}".format(error_code, error_message))
        except Exception as e:
            raise CloudProviderError("Failed to retrieve metric data: {0}".format(str(e)))

    def _process_metric_data_response(
        self, 
        response: Dict[str, Any], 
        series: Dict[str, List[Tuple[datetime.datetime, float]]]
    ) -> None:
        """Process metric data response and add to series"""
        for result in response["MetricDataResults"]:
            query_id = result["Id"]
            if query_id in series:
                timestamps = result.get("Timestamps", [])
                values = result.get("Values", [])
                points = list(zip(timestamps, values))
                series[query_id].extend(points)

    def get_metric_statistics(
        self,
        namespace: str,
        metric_name: str,
        dimensions: List[MetricDimension],
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        period: int = 60,
        statistics: List[str] = None,
        unit: Optional[str] = None,
        extended_statistics: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve statistics for a single metric (legacy method)

        Args:
            namespace: Metric namespace
            metric_name: Metric name
            dimensions: List of metric dimensions
            start_time: Query start time
            end_time: Query end time
            period: Statistics period (seconds)
            statistics: Statistics to retrieve (e.g., ["Sum", "Average", "Maximum", "Minimum"])
            unit: Metric unit
            extended_statistics: Extended statistics (e.g., ["p90", "p95", "p99"])

        Returns:
            List of data points (sorted by time)

        Raises:
            CloudProviderError: When CloudWatch API call fails
        """
        if statistics is None:
            statistics = ["Sum"]

        try:
            # Convert to UTC time
            if start_time.tzinfo is None:
                start_time = start_time.replace(tzinfo=datetime.timezone.utc)
            if end_time.tzinfo is None:
                end_time = end_time.replace(tzinfo=datetime.timezone.utc)

            response = self.client.get_metric_statistics(
                Namespace=namespace,
                MetricName=metric_name,
                Dimensions=[dim.to_dict() for dim in dimensions],
                StartTime=start_time,
                EndTime=end_time,
                Period=period,
                Statistics=statistics,
                Unit=unit,
                ExtendedStatistics=extended_statistics,
            )

            # Sort by time (CloudWatch doesn't guarantee order)
            datapoints = sorted(response["Datapoints"], key=lambda x: x["Timestamp"])
            return datapoints

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]
            raise CloudProviderError("CloudWatch API error ({0}): {1}".format(error_code, error_message))
        except Exception as e:
            raise CloudProviderError("Failed to retrieve metric statistics: {0}".format(str(e)))

    def list_metrics(
        self,
        namespace: Optional[str] = None,
        metric_name: Optional[str] = None,
        dimensions: Optional[List[Dict[str, str]]] = None,
        recently_active: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        List available metrics

        Args:
            namespace: Metric namespace
            metric_name: Metric name
            dimensions: Dimension filters
            recently_active: Recently active status ("PT3H" etc.)

        Returns:
            List of metrics

        Raises:
            CloudProviderError: When CloudWatch API call fails
        """
        try:
            kwargs = {}
            if namespace:
                kwargs["Namespace"] = namespace
            if metric_name:
                kwargs["MetricName"] = metric_name
            if dimensions:
                kwargs["Dimensions"] = dimensions
            if recently_active:
                kwargs["RecentlyActive"] = recently_active

            response = self.client.list_metrics(**kwargs)
            return response["Metrics"]

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]
            raise CloudProviderError("CloudWatch API error ({0}): {1}".format(error_code, error_message))
        except Exception as e:
            raise CloudProviderError("Failed to list metrics: {0}".format(str(e)))

    def put_metric_data(
        self,
        namespace: str,
        metric_data: List[Dict[str, Any]],
    ) -> None:
        """
        Publish custom metric data

        Args:
            namespace: Metric namespace
            metric_data: List of metric data

        Raises:
            CloudProviderError: When CloudWatch API call fails
        """
        try:
            self.client.put_metric_data(
                Namespace=namespace,
                MetricData=metric_data,
            )
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]
            raise CloudProviderError("CloudWatch API error ({0}): {1}".format(error_code, error_message))
        except Exception as e:
            raise CloudProviderError("Failed to publish metric data: {0}".format(str(e)))

    def create_custom_metric(
        self,
        namespace: str,
        metric_name: str,
        dimensions: List[MetricDimension],
        value: float,
        unit: str = "Count",
        timestamp: Optional[datetime.datetime] = None,
    ) -> None:
        """
        Create and publish custom metric

        Args:
            namespace: Metric namespace
            metric_name: Metric name
            dimensions: Metric dimensions
            value: Metric value
            unit: Metric unit
            timestamp: Metric timestamp (None for current time)

        Raises:
            CloudProviderError: When CloudWatch API call fails
        """
        if timestamp is None:
            timestamp = datetime.datetime.now(datetime.timezone.utc)

        metric_data = [{
            "MetricName": metric_name,
            "Dimensions": [dim.to_dict() for dim in dimensions],
            "Value": value,
            "Unit": unit,
            "Timestamp": timestamp,
        }]

        self.put_metric_data(namespace, metric_data)
