import asyncio
import axiom
from initializers.axiom_setup import AxiomHelper
from initializers.redis import r

axiom = AxiomHelper()

class BatchCacheEventHandler:
  def __init__(self):
    self.aggregation_interval = 3600

  def increment_cache_hit(self):
    r.incr("cache_hits")

  def increment_cache_miss(self):
    r.incr("cache_misses")

  async def send_aggregated_event(self):
    cache_hits = int(r.get("cache_hits") or 0)
    cache_misses = int(r.get("cache_misses") or 0)
    
    if cache_hits or cache_misses:
        event_data = {
            "type": "cache",
            "cache_hits": cache_hits,
            "cache_misses": cache_misses
        }
        axiom.send_event([event_data])
        
        # Reset the counters
        r.set("cache_hits", 0)
        r.set("cache_misses", 0)

  async def aggregation_scheduler(self):
      while True:
          await asyncio.sleep(self.aggregation_interval)
          await self.send_aggregated_event()

  
