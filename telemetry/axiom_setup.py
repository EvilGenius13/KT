import axiom
import os
from dotenv import load_dotenv
load_dotenv()

AXIOM_DATASET = os.getenv("AXIOM_DATASET")

class AxiomHelper:
    def __init__(self):
        self.client = axiom.Client(os.getenv("AXIOM_KEY"), AXIOM_DATASET)

    def send_event(self, event_data):
        self.client.ingest_events(AXIOM_DATASET, event_data)

# You can then use it in other files like this:
# from axiom_helper import AxiomHelper
# axiom = AxiomHelper()
# axiom.send_event({"event": "some_event", "data": "some_data"})
