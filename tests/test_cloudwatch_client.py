"""
CloudWatch Metrics 클라이언트 테스트

이 파일은 CloudWatch Metrics 클라이언트의 기본 기능을 테스트합니다.
"""

import pytest
import datetime
from unittest.mock import Mock, patch

from cloud_utils.providers.aws.cloudwatch_models import MetricDimension, MetricQuery
from cloud_utils.providers.aws.cloudwatch_client import CloudWatchMetricsClient


class TestMetricDimension:
    """MetricDimension 클래스 테스트"""
    
    def test_metric_dimension_creation(self):
        """MetricDimension 생성 테스트"""
        dim = MetricDimension("Service", "processor")
        assert dim.name == "Service"
        assert dim.value == "processor"
    
    def test_metric_dimension_to_dict(self):
        """MetricDimension to_dict 메서드 테스트"""
        dim = MetricDimension("Environment", "production")
        result = dim.to_dict()
        assert result == {"Name": "Environment", "Value": "production"}


class TestMetricQuery:
    """MetricQuery 클래스 테스트"""
    
    def test_metric_query_creation(self):
        """MetricQuery 생성 테스트"""
        dimensions = [MetricDimension("Service", "processor")]
        query = MetricQuery(
            namespace="MyApp/Metrics",
            metric_name="ResourcesProcessed",
            dimensions=dimensions,
            period=60,
            stat="Sum"
        )
        assert query.namespace == "MyApp/Metrics"
        assert query.metric_name == "ResourcesProcessed"
        assert len(query.dimensions) == 1
        assert query.period == 60
        assert query.stat == "Sum"
    
    def test_metric_query_to_metric_stat_query(self):
        """MetricQuery to_metric_stat_query 메서드 테스트"""
        dimensions = [MetricDimension("Service", "processor")]
        query = MetricQuery(
            namespace="MyApp/Metrics",
            metric_name="ResourcesProcessed",
            dimensions=dimensions,
            period=60,
            stat="Sum",
            unit="Count"
        )
        
        result = query.to_metric_stat_query("test_id")
        assert result["Id"] == "test_id"
        assert result["ReturnData"] is True
        assert "MetricStat" in result
        assert result["MetricStat"]["Metric"]["Namespace"] == "MyApp/Metrics"
        assert result["MetricStat"]["Metric"]["MetricName"] == "ResourcesProcessed"
        assert result["MetricStat"]["Period"] == 60
        assert result["MetricStat"]["Stat"] == "Sum"
        assert result["MetricStat"]["Unit"] == "Count"
    
    def test_metric_query_with_expression(self):
        """MetricQuery with expression 테스트"""
        query = MetricQuery(
            namespace="MyApp/Metrics",
            metric_name="ResourcesProcessed",
            dimensions=[],
            expression="query_0 / 60",
            label="Per Second Rate"
        )
        
        result = query.to_metric_stat_query("test_id")
        assert result["Id"] == "test_id"
        assert result["Expression"] == "query_0 / 60"
        assert result["Label"] == "Per Second Rate"
        assert result["ReturnData"] is True
        assert "MetricStat" not in result


class TestCloudWatchMetricsClient:
    """CloudWatchMetricsClient 클래스 테스트"""
    
    @patch('boto3.client')
    def test_client_initialization(self, mock_boto3_client):
        """클라이언트 초기화 테스트"""
        mock_client = Mock()
        mock_boto3_client.return_value = mock_client
        
        client = CloudWatchMetricsClient(region_name="ap-northeast-2")
        assert client.client == mock_client
        mock_boto3_client.assert_called_once_with(
            "cloudwatch",
            region_name="ap-northeast-2",
            aws_access_key_id=None,
            aws_secret_access_key=None,
            aws_session_token=None,
            profile_name=None
        )
    
    @patch('boto3.Session')
    def test_client_initialization_with_profile(self, mock_session):
        """프로파일을 사용한 클라이언트 초기화 테스트"""
        mock_session_instance = Mock()
        mock_client = Mock()
        mock_session_instance.client.return_value = mock_client
        mock_session.return_value = mock_session_instance
        
        client = CloudWatchMetricsClient(profile_name="test-profile")
        assert client.client == mock_client
        mock_session.assert_called_once_with(profile_name="test-profile")
    
    def test_process_metric_data_response(self):
        """_process_metric_data_response 메서드 테스트"""
        client = CloudWatchMetricsClient()
        
        # 테스트 데이터 준비
        response = {
            "MetricDataResults": [
                {
                    "Id": "query_0",
                    "Timestamps": ["2024-01-01T00:00:00Z", "2024-01-01T00:01:00Z"],
                    "Values": [10.0, 20.0]
                },
                {
                    "Id": "query_1",
                    "Timestamps": ["2024-01-01T00:00:00Z"],
                    "Values": [5.0]
                }
            ]
        }
        
        series = {"query_0": [], "query_1": []}
        
        # 메서드 실행
        client._process_metric_data_response(response, series)
        
        # 결과 검증
        assert len(series["query_0"]) == 2
        assert len(series["query_1"]) == 1
        assert series["query_0"][0] == ("2024-01-01T00:00:00Z", 10.0)
        assert series["query_0"][1] == ("2024-01-01T00:01:00Z", 20.0)
        assert series["query_1"][0] == ("2024-01-01T00:00:00Z", 5.0)


if __name__ == "__main__":
    pytest.main([__file__])

