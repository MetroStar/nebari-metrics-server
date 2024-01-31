from typing import Any, Dict, List, Optional, Union
import os

from nebari.schema import Base
from _nebari.stages.base import NebariTerraformStage


class MetricsServerAffinitySelectorConfig(Base):
    default: str


class MetricsServerAffinityConfig(Base):
    enabled: Optional[bool] = True
    selector: Union[MetricsServerAffinitySelectorConfig, str] = "general"

class MetricsServerConfig(Base):
    name: Optional[str] = "metrics-server"
    namespace: Optional[str] = None
    affinity: MetricsServerAffinityConfig = MetricsServerAffinityConfig()
    values: Optional[Dict[str, Any]] = {}


class InputSchema(Base):
    metrics_server: MetricsServerConfig = MetricsServerConfig()


class MetricsServerStage(NebariTerraformStage):
    name = "metrics-server"
    priority = 100

    input_schema = InputSchema

    def input_vars(self, stage_outputs: Dict[str, Dict[str, Any]]):
        chart_ns = self.config.metrics_server.namespace
        create_ns = True
        if chart_ns == None or chart_ns == "" or chart_ns == self.config.namespace:
            chart_ns = self.config.namespace
            create_ns = False

        return {
            "name": self.config.metrics_server.name,
            "create_namespace": create_ns,
            "namespace": chart_ns,
            "affinity": {
                "enabled": self.config.cert_manager.affinity.enabled,
                "selector": self.config.cert_manager.affinity.selector.__dict__
                if isinstance(self.config.cert_manager.affinity.selector, MetricsServerAffinityConfig)
                else self.config.cert_manager.affinity.selector,
            },
            "overrides": self.config.metrics_server.values,
        }