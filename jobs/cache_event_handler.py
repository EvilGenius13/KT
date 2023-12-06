import asyncio
import axiom
from telemetry.axiom_setup import AxiomHelper

axiom = AxiomHelper()

class BatchCacheEventHandler:
  def __init__(self):
    self.cache_hits = 0
    self.cache_misses = 0
    self.aggregation_interval = 3600

  def increment_cache_hit(self):
    self.cache_hits += 1

  def increment_cache_miss(self):
    self.cache_misses += 1

  async def send_aggregated_event(self):
    if self.cache_hits or self.cache_misses:
        event_data = {
            "type": "cache",
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses
        }
        axiom.send_event([event_data])
        # Reset the counters
        self.cache_hits = 0
        self.cache_misses = 0

  async def aggregation_scheduler(self):
      while True:
          await asyncio.sleep(self.aggregation_interval)
          await self.send_aggregated_event()

  
