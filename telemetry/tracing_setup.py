from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
import os

from dotenv import load_dotenv
load_dotenv()

AXIOM_TRACE_KEY = os.getenv("AXIOM_TRACE_KEY")

resource = Resource(attributes={"service.name": "kt-service"})

# Create a TracerProvider and configure it to use the OTLP exporter
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

# Set the OTLP exporter to use HTTP and point it to the Axiom URL
otlp_exporter = OTLPSpanExporter(
    endpoint="https://api.axiom.co/v1/traces",
    headers={
        "Authorization": AXIOM_TRACE_KEY,
        "X-Axiom-Dataset": "kt"  # Add your dataset here
    }
)

# Configure the tracer to use the BatchSpanProcessor with the OTLP exporter
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

tracer = trace.get_tracer(__name__)

# Example usage:
# Now you can create spans
# with tracer.start_as_current_span("foo"):
#     print("Axiom, tracing!")

# Clean up before exit
# span_processor.shutdown()