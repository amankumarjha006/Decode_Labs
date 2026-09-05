"""Pipelines package for real-time and bulk processing."""

from app.pipelines.realtime import RealtimePipeline
from app.pipelines.bulk import LocalAsyncBulkProcessor, BatchProvider

__all__ = ["RealtimePipeline", "LocalAsyncBulkProcessor", "BatchProvider"]
