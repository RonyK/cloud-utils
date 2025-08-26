"""
Common Models for CloudWatch Metrics

This module defines common data classes used in CloudWatch Metrics.
These are shared between synchronous and asynchronous clients.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class MetricDimension:
    """Data class representing CloudWatch Metric Dimension"""
    name: str
    value: str

    def to_dict(self) -> Dict[str, str]:
        """Convert to AWS API format"""
        return {"Name": self.name, "Value": self.value}


@dataclass
class MetricQuery:
    """Data class representing CloudWatch Metric query"""
    namespace: str
    metric_name: str
    dimensions: List[MetricDimension]
    period: int = 60
    stat: str = "Sum"
    unit: Optional[str] = None
    expression: Optional[str] = None
    label: Optional[str] = None

    def to_metric_stat_query(self, query_id: str) -> Dict[str, Any]:
        """Convert to MetricStat query"""
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
    """Data class representing metric data point"""
    timestamp: str
    value: float
    unit: Optional[str] = None
    statistics: Optional[Dict[str, float]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to AWS API format"""
        result = {
            "Timestamp": self.timestamp,
            "Value": self.value,
        }
        if self.unit:
            result["Unit"] = self.unit
        if self.statistics:
            result.update(self.statistics)
        return result


