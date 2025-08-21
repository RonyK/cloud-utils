"""
CloudWatch Metrics 동기식 클라이언트 모듈

이 모듈은 AWS CloudWatch Metrics를 조회하기 위한 동기식 클라이언트를 제공합니다.
여러 dimension을 지원하며, get_metric_data와 get_metric_statistics를 모두 지원합니다.
"""

import datetime
from typing import Any, Dict, List, Optional, Tuple

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from ..exceptions import CloudProviderError, ConfigurationError
from .cloudwatch_models import MetricDimension, MetricQuery


class CloudWatchMetricsClient:
    """CloudWatch Metrics 동기식 클라이언트"""

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
        CloudWatch Metrics 클라이언트 초기화

        Args:
            region_name: AWS 리전명 (예: 'ap-northeast-2')
            aws_access_key_id: AWS 액세스 키 ID
            aws_secret_access_key: AWS 시크릿 액세스 키
            aws_session_token: AWS 세션 토큰
            profile_name: AWS 프로파일명
            **kwargs: boto3 클라이언트에 전달할 추가 인자
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
            raise ConfigurationError("AWS 자격 증명을 찾을 수 없습니다.")
        except Exception as e:
            raise ConfigurationError(f"CloudWatch 클라이언트 초기화 실패: {str(e)}")

    def get_metric_data(
        self,
        queries: List[MetricQuery],
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        scan_by: str = "TimestampAscending",
        max_datapoints: Optional[int] = None,
    ) -> Dict[str, List[Tuple[datetime.datetime, float]]]:
        """
        여러 메트릭을 한 번에 조회 (권장 방법)

        Args:
            queries: 메트릭 쿼리 목록
            start_time: 조회 시작 시간
            end_time: 조회 종료 시간
            scan_by: 정렬 방식 ("TimestampAscending" 또는 "TimestampDescending")
            max_datapoints: 최대 데이터 포인트 수

        Returns:
            쿼리 ID별로 (timestamp, value) 튜플의 리스트를 포함하는 딕셔너리

        Raises:
            CloudProviderError: CloudWatch API 호출 실패 시
        """
        try:
            # UTC 시간으로 변환
            if start_time.tzinfo is None:
                start_time = start_time.replace(tzinfo=datetime.timezone.utc)
            if end_time.tzinfo is None:
                end_time = end_time.replace(tzinfo=datetime.timezone.utc)

            # 쿼리 ID 생성
            query_id_map = {}
            metric_data_queries = []
            
            for i, query in enumerate(queries):
                query_id = f"query_{i}"
                query_id_map[query_id] = query
                metric_data_queries.append(query.to_metric_stat_query(query_id))

            # 초기 API 호출
            response = self.client.get_metric_data(
                StartTime=start_time,
                EndTime=end_time,
                MetricDataQueries=metric_data_queries,
                ScanBy=scan_by,
                MaxDatapoints=max_datapoints,
            )

            # 결과 초기화
            series: Dict[str, List[Tuple[datetime.datetime, float]]] = {}
            for query_id in query_id_map.keys():
                series[query_id] = []

            # 첫 번째 응답 처리
            self._process_metric_data_response(response, series)

            # NextToken이 있으면 반복 호출
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
            raise CloudProviderError(f"CloudWatch API 오류 ({error_code}): {error_message}")
        except Exception as e:
            raise CloudProviderError(f"메트릭 데이터 조회 실패: {str(e)}")

    def _process_metric_data_response(
        self, 
        response: Dict[str, Any], 
        series: Dict[str, List[Tuple[datetime.datetime, float]]]
    ) -> None:
        """메트릭 데이터 응답을 처리하여 series에 추가"""
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
        단일 메트릭의 통계 조회 (레거시 방법)

        Args:
            namespace: 메트릭 네임스페이스
            metric_name: 메트릭명
            dimensions: 메트릭 차원 목록
            start_time: 조회 시작 시간
            end_time: 조회 종료 시간
            period: 통계 기간 (초)
            statistics: 조회할 통계 (예: ["Sum", "Average", "Maximum", "Minimum"])
            unit: 메트릭 단위
            extended_statistics: 확장 통계 (예: ["p90", "p95", "p99"])

        Returns:
            데이터 포인트 목록 (시간순으로 정렬됨)

        Raises:
            CloudProviderError: CloudWatch API 호출 실패 시
        """
        if statistics is None:
            statistics = ["Sum"]

        try:
            # UTC 시간으로 변환
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

            # 시간순으로 정렬 (CloudWatch는 순서를 보장하지 않음)
            datapoints = sorted(response["Datapoints"], key=lambda x: x["Timestamp"])
            return datapoints

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]
            raise CloudProviderError(f"CloudWatch API 오류 ({error_code}): {error_message}")
        except Exception as e:
            raise CloudProviderError(f"메트릭 통계 조회 실패: {str(e)}")

    def list_metrics(
        self,
        namespace: Optional[str] = None,
        metric_name: Optional[str] = None,
        dimensions: Optional[List[Dict[str, str]]] = None,
        recently_active: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        사용 가능한 메트릭 목록 조회

        Args:
            namespace: 메트릭 네임스페이스
            metric_name: 메트릭명
            dimensions: 차원 필터
            recently_active: 최근 활성 상태 ("PT3H" 등)

        Returns:
            메트릭 목록

        Raises:
            CloudProviderError: CloudWatch API 호출 실패 시
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
            raise CloudProviderError(f"CloudWatch API 오류 ({error_code}): {error_message}")
        except Exception as e:
            raise CloudProviderError(f"메트릭 목록 조회 실패: {str(e)}")

    def put_metric_data(
        self,
        namespace: str,
        metric_data: List[Dict[str, Any]],
    ) -> None:
        """
        커스텀 메트릭 데이터 발행

        Args:
            namespace: 메트릭 네임스페이스
            metric_data: 메트릭 데이터 목록

        Raises:
            CloudProviderError: CloudWatch API 호출 실패 시
        """
        try:
            self.client.put_metric_data(
                Namespace=namespace,
                MetricData=metric_data,
            )
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]
            raise CloudProviderError(f"CloudWatch API 오류 ({error_code}): {error_message}")
        except Exception as e:
            raise CloudProviderError(f"메트릭 데이터 발행 실패: {str(e)}")

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
        커스텀 메트릭 생성 및 발행

        Args:
            namespace: 메트릭 네임스페이스
            metric_name: 메트릭명
            dimensions: 메트릭 차원
            value: 메트릭 값
            unit: 메트릭 단위
            timestamp: 메트릭 시간 (None이면 현재 시간)

        Raises:
            CloudProviderError: CloudWatch API 호출 실패 시
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
