import logging
from dataclasses import dataclass
from datetime import datetime

@dataclass
class QueryMetrics:
    query: str
    timestamp: datetime
    retrieval_time_ms: float
    num_results: int
    rerank_score: float
    context_length: int

class RAGMonitor:
    def __init__(self):
        self.metrics: List[QueryMetrics] = []
        
    def log_query(self, metrics: QueryMetrics):
        self.metrics.append(metrics)
        
        # Alert on anomalies
        if metrics.retrieval_time_ms > 1000:
            logging.warning(f"Slow query: {metrics.retrieval_time_ms}ms")
        
        if metrics.rerank_score < 0.3:
            logging.warning(f"Low confidence result for: {metrics.query}")
    
    def get_stats(self):
        return {
            'avg_latency': np.mean([m.retrieval_time_ms for m in self.metrics]),
            'p95_latency': np.percentile([m.retrieval_time_ms for m in self.metrics], 95),
            'avg_results': np.mean([m.num_results for m in self.metrics]),
            'avg_score': np.mean([m.rerank_score for m in self.metrics])
        }