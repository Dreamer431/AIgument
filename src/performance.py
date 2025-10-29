"""
性能监控工具
用于记录和分析 API 请求的性能指标
"""
import time
import functools
from flask import g, request
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def timing_decorator(f):
    """装饰器：记录函数执行时间"""
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = f(*args, **kwargs)
        end_time = time.time()
        duration = (end_time - start_time) * 1000  # 转换为毫秒
        
        # 记录到日志
        logger.info(f"{f.__name__} 执行时间: {duration:.2f}ms")
        
        return result
    return wrapper


def before_request():
    """请求开始前的钩子"""
    g.start_time = time.time()
    g.request_id = f"{int(time.time() * 1000)}"


def after_request(response):
    """请求结束后的钩子"""
    if hasattr(g, 'start_time'):
        elapsed = (time.time() - g.start_time) * 1000  # 毫秒
        
        # 添加性能头
        response.headers['X-Request-ID'] = getattr(g, 'request_id', 'unknown')
        response.headers['X-Response-Time'] = f"{elapsed:.2f}ms"
        
        # 记录慢请求（超过1秒）
        if elapsed > 1000:
            logger.warning(
                f"慢请求警告: {request.method} {request.path} "
                f"耗时 {elapsed:.2f}ms"
            )
        else:
            logger.info(
                f"{request.method} {request.path} "
                f"响应: {response.status_code} "
                f"耗时: {elapsed:.2f}ms"
            )
    
    return response


class PerformanceMonitor:
    """性能监控类"""
    
    def __init__(self):
        self.metrics = {
            'total_requests': 0,
            'total_time': 0,
            'slow_requests': 0,
            'errors': 0
        }
    
    def record_request(self, duration, status_code):
        """记录请求"""
        self.metrics['total_requests'] += 1
        self.metrics['total_time'] += duration
        
        if duration > 1000:  # 超过1秒
            self.metrics['slow_requests'] += 1
        
        if status_code >= 400:
            self.metrics['errors'] += 1
    
    def get_stats(self):
        """获取统计信息"""
        if self.metrics['total_requests'] == 0:
            return {
                'avg_response_time': 0,
                'slow_request_rate': 0,
                'error_rate': 0,
                'total_requests': 0
            }
        
        return {
            'total_requests': self.metrics['total_requests'],
            'avg_response_time': self.metrics['total_time'] / self.metrics['total_requests'],
            'slow_request_rate': self.metrics['slow_requests'] / self.metrics['total_requests'] * 100,
            'error_rate': self.metrics['errors'] / self.metrics['total_requests'] * 100,
            'total_time': self.metrics['total_time']
        }
    
    def reset(self):
        """重置统计"""
        self.metrics = {
            'total_requests': 0,
            'total_time': 0,
            'slow_requests': 0,
            'errors': 0
        }


# 全局性能监控实例
performance_monitor = PerformanceMonitor()
