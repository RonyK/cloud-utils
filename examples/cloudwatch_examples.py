"""
CloudWatch Metrics 클라이언트 사용 예제

이 파일은 CloudWatch Metrics 동기식 및 비동기식 클라이언트의 사용법을 보여줍니다.
"""

import asyncio
import datetime
from typing import List

# 동기식 클라이언트 사용 예제
def sync_cloudwatch_example():
    """동기식 CloudWatch 클라이언트 사용 예제"""
    from cloud_utils.providers.aws import (
        CloudWatchMetricsClient, 
        MetricDimension, 
        MetricQuery
    )
    
    # 클라이언트 초기화
    client = CloudWatchMetricsClient(region_name="ap-northeast-2")
    
    # 메트릭 차원 정의
    dimensions = [
        MetricDimension("Service", "processor"),
        MetricDimension("Stage", "prod"),
        MetricDimension("Environment", "production")
    ]
    
    # 메트릭 쿼리 생성
    queries = [
        MetricQuery(
            namespace="MyApp/Metrics",
            metric_name="ResourcesProcessed",
            dimensions=dimensions,
            period=60,
            stat="Sum",
            unit="Count"
        ),
        # Metric Math를 사용한 초당 처리율 계산
        MetricQuery(
            namespace="MyApp/Metrics",
            metric_name="ResourcesProcessed",
            dimensions=dimensions,
            period=60,
            stat="Sum",
            expression="query_0 / PERIOD(query_0)",  # 분당합 / 60초 = 초당
            label="ResourcesProcessed per second"
        )
    ]
    
    # 시간 범위 설정
    end_time = datetime.datetime.now(datetime.timezone.utc)
    start_time = end_time - datetime.timedelta(hours=24)
    
    try:
        # 여러 메트릭을 한 번에 조회 (권장 방법)
        print("=== get_metric_data 사용 예제 ===")
        series = client.get_metric_data(queries, start_time, end_time)
        
        for query_id, data_points in series.items():
            print(f"\n{query_id}:")
            for timestamp, value in data_points[:5]:  # 처음 5개만 출력
                print(f"  {timestamp}: {value}")
        
        # 단일 메트릭 통계 조회 (레거시 방법)
        print("\n=== get_metric_statistics 사용 예제 ===")
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
        
        print(f"데이터 포인트 수: {len(datapoints)}")
        for point in datapoints[:3]:  # 처음 3개만 출력
            print(f"  {point['Timestamp']}: Sum={point['Sum']}, Avg={point['Average']}, Max={point['Maximum']}")
        
        # 사용 가능한 메트릭 목록 조회
        print("\n=== list_metrics 사용 예제 ===")
        metrics = client.list_metrics(
            namespace="MyApp/Metrics",
            recently_active="PT3H"
        )
        
        print(f"활성 메트릭 수: {len(metrics)}")
        for metric in metrics[:3]:  # 처음 3개만 출력
            print(f"  {metric['MetricName']}: {metric['Dimensions']}")
        
        # 커스텀 메트릭 발행
        print("\n=== 커스텀 메트릭 발행 예제 ===")
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
        print("커스텀 메트릭 발행 완료")
        
    except Exception as e:
        print(f"오류 발생: {e}")


# 비동기식 클라이언트 사용 예제
async def async_cloudwatch_example():
    """비동기식 CloudWatch 클라이언트 사용 예제"""
    from cloud_utils.providers.aws import (
        AsyncCloudWatchMetricsClient, 
        MetricDimension, 
        MetricQuery
    )
    
    # 클라이언트 초기화
    client = AsyncCloudWatchMetricsClient(region_name="ap-northeast-2")
    
    # 메트릭 차원 정의
    dimensions = [
        MetricDimension("Service", "api-gateway"),
        MetricDimension("Stage", "prod"),
        MetricDimension("Method", "GET")
    ]
    
    # 메트릭 쿼리 생성
    queries = [
        MetricQuery(
            namespace="AWS/ApiGateway",
            metric_name="Count",
            dimensions=dimensions,
            period=300,  # 5분
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
    
    # 시간 범위 설정
    end_time = datetime.datetime.now(datetime.timezone.utc)
    start_time = end_time - datetime.timedelta(hours=6)
    
    try:
        # 여러 메트릭을 비동기로 조회
        print("=== 비동기 get_metric_data 사용 예제 ===")
        series = await client.get_metric_data(queries, start_time, end_time)
        
        for query_id, data_points in series.items():
            print(f"\n{query_id}:")
            for timestamp, value in data_points[:5]:  # 처음 5개만 출력
                print(f"  {timestamp}: {value}")
        
        # 단일 메트릭 통계를 비동기로 조회
        print("\n=== 비동기 get_metric_statistics 사용 예제 ===")
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
        
        print(f"데이터 포인트 수: {len(datapoints)}")
        for point in datapoints[:3]:  # 처음 3개만 출력
            print(f"  {point['Timestamp']}: Sum={point['Sum']}, Avg={point['Average']}")
        
        # 사용 가능한 메트릭 목록을 비동기로 조회
        print("\n=== 비동기 list_metrics 사용 예제 ===")
        metrics = await client.list_metrics(
            namespace="AWS/ApiGateway",
            recently_active="PT1H"
        )
        
        print(f"활성 메트릭 수: {len(metrics)}")
        for metric in metrics[:3]:  # 처음 3개만 출력
            print(f"  {metric['MetricName']}: {metric['Dimensions']}")
        
        # 커스텀 메트릭을 비동기로 발행
        print("\n=== 비동기 커스텀 메트릭 발행 예제 ===")
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
        print("비동기 커스텀 메트릭 발행 완료")
        
    except Exception as e:
        print(f"오류 발생: {e}")


# 고급 사용 예제: 여러 서비스의 메트릭을 동시에 조회
async def advanced_metrics_example():
    """고급 메트릭 조회 예제: 여러 서비스의 메트릭을 동시에 조회"""
    from cloud_utils.providers.aws import (
        AsyncCloudWatchMetricsClient, 
        MetricDimension, 
        MetricQuery
    )
    
    client = AsyncCloudWatchMetricsClient(region_name="ap-northeast-2")
    
    # 여러 서비스의 메트릭을 동시에 조회
    queries = [
        # EC2 CPU 사용률
        MetricQuery(
            namespace="AWS/EC2",
            metric_name="CPUUtilization",
            dimensions=[MetricDimension("InstanceId", "i-1234567890abcdef0")],
            period=300,
            stat="Average",
            unit="Percent"
        ),
        # RDS 연결 수
        MetricQuery(
            namespace="AWS/RDS",
            metric_name="DatabaseConnections",
            dimensions=[MetricDimension("DBInstanceIdentifier", "my-db-instance")],
            period=300,
            stat="Average",
            unit="Count"
        ),
        # S3 버킷 크기
        MetricQuery(
            namespace="AWS/S3",
            metric_name="BucketSizeBytes",
            dimensions=[
                MetricDimension("BucketName", "my-bucket"),
                MetricDimension("StorageType", "StandardStorage")
            ],
            period=86400,  # 24시간
            stat="Average",
            unit="Bytes"
        ),
        # Lambda 실행 시간
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
        print("=== 다중 서비스 메트릭 동시 조회 예제 ===")
        series = await client.get_metric_data(queries, start_time, end_time)
        
        for query_id, data_points in series.items():
            if data_points:
                print(f"\n{query_id}:")
                print(f"  데이터 포인트 수: {len(data_points)}")
                print(f"  첫 번째 값: {data_points[0]}")
                print(f"  마지막 값: {data_points[-1]}")
            else:
                print(f"\n{query_id}: 데이터 없음")
                
    except Exception as e:
        print(f"오류 발생: {e}")


def main():
    """메인 함수"""
    print("CloudWatch Metrics 클라이언트 사용 예제")
    print("=" * 50)
    
    # 동기식 예제 실행
    print("\n1. 동기식 클라이언트 예제")
    sync_cloudwatch_example()
    
    # 비동기식 예제 실행
    print("\n\n2. 비동기식 클라이언트 예제")
    asyncio.run(async_cloudwatch_example())
    
    # 고급 예제 실행
    print("\n\n3. 고급 메트릭 조회 예제")
    asyncio.run(advanced_metrics_example())


if __name__ == "__main__":
    main()

