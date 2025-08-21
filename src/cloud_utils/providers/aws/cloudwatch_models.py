"""
CloudWatch Metrics 공통 모델

이 모듈은 CloudWatch Metrics에서 사용하는 공통 데이터 클래스들을 정의합니다.
동기식과 비동기식 클라이언트에서 공통으로 사용됩니다.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class MetricDimension:
    """CloudWatch Metric Dimension을 나타내는 데이터 클래스"""
    name: str
    value: str

    def to_dict(self) -> Dict[str, str]:
        """AWS API 형식으로 변환"""
        return {"Name": self.name, "Value": self.value}


@dataclass
class MetricQuery:
    """CloudWatch Metric 쿼리를 나타내는 데이터 클래스"""
    namespace: str
    metric_name: str
    dimensions: List[MetricDimension]
    period: int = 60
    stat: str = "Sum"
    unit: Optional[str] = None
    expression: Optional[str] = None
    label: Optional[str] = None

    def to_metric_stat_query(self, query_id: str) -> Dict[str, Any]:
        """MetricStat 쿼리로 변환"""
        if self.expression:
            return {
                "Id": query_id,
                "Expression": self.expression,
                "Label": self.label,
                "ReturnData": True,
            }
        
        return {
            "Id": query_id,
            "MetricStat": {
                "Metric": {
                    "Namespace": self.namespace,
                    "MetricName": self.metric_name,
                    "Dimensions": [dim.to_dict() for dim in self.dimensions],
                },
                "Period": self.period,
                "Stat": self.stat,
                "Unit": self.unit,
            },
            "ReturnData": True,
        }


@dataclass
class MetricDataPoint:
    """메트릭 데이터 포인트를 나타내는 데이터 클래스"""
    timestamp: str
    value: float
    unit: Optional[str] = None
    statistics: Optional[Dict[str, float]] = None

    def to_dict(self) -> Dict[str, Any]:
        """AWS API 형식으로 변환"""
        result = {
            "Timestamp": self.timestamp,
            "Value": self.value,
        }
        if self.unit:
            result["Unit"] = self.unit
        if self.statistics:
            result.update(self.statistics)
        return result

