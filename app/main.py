from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from app import setup_otel
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from app.tracing import traced_operation
import time

# Setup OpenTelemetry
trace_provider = setup_otel()

# Create FastAPI application
app = FastAPI(title="Hello World API")

# Auto-instrument FastAPI
FastAPIInstrumentor.instrument_app(app)


# Global exception handler for HTTPException
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    span = trace.get_current_span()
    span.set_status(trace.Status(trace.StatusCode.ERROR, str(exc)))
    span.record_exception(exc)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.get("/")
async def read_root():
    # Get a tracer
    tracer = trace.get_tracer(__name__)

    # Start a custom span
    with tracer.start_as_current_span("hello-world-operation") as span:
        # Add custom attributes to the span
        span.set_attribute("custom.attribute", "hello-world-request")

        # Add some business logic (or simulated processing)
        import time

        time.sleep(0.1)  # Simulate some processing time

        # Record an event in the span
        span.add_event("Completed hello world request")

        # Return the response
        return {"message": "Hello World"}


@app.get("/complex")
async def complex_operation():
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("complex-operation") as parent_span:
        parent_span.set_attribute("operation.type", "complex")

        # First sub-operation
        with tracer.start_as_current_span("sub-operation-1") as child_span1:
            child_span1.set_attribute("sub-operation", "first")
            import time

            time.sleep(0.2)  # Simulate processing
            child_span1.add_event("First sub-operation completed")

        # Second sub-operation
        with tracer.start_as_current_span("sub-operation-2") as child_span2:
            child_span2.set_attribute("sub-operation", "second")
            time.sleep(0.1)  # Simulate processing

            # Even more nested span
            with tracer.start_as_current_span("nested-operation") as nested_span:
                nested_span.set_attribute("depth", "nested")
                time.sleep(0.05)

            child_span2.add_event("Second sub-operation completed")

        return {"message": "Complex operation completed", "steps": 2}


@app.get("/example")
async def example_endpoint():
    with traced_operation("example-operation", {"context": "api-call"}):
        # Your code here
        result = perform_work()
        return {"result": result}



# Add an endpoint that demonstrates error handling
@app.get("/error/{status_code}")
async def error_endpoint(status_code: int):
    """
    Endpoint that generates an HTTP error with the specified status code.
    This demonstrates how the exception handler records errors in traces.
    """
    tracer = trace.get_tracer(__name__)

    with tracer.start_as_current_span("error-operation") as span:
        span.set_attribute("requested_status_code", status_code)

        # Simulate some processing before error
        time.sleep(0.1)

        # Raise an HTTP exception with the requested status code
        if status_code >= 400:
            raise HTTPException(
                status_code=status_code,
                detail=f"Example error with status code {status_code}",
            )

        return {"message": "This should not be returned", "status_code": status_code}


def perform_work():
    """
    Adds two Unix timestamps and returns the result.

    Returns:
        dict: The result of adding two timestamps
    """
    # Get current timestamp
    timestamp1 = time.time()

    # Get another timestamp
    timestamp2 = time.time()

    # Add the timestamps
    result = timestamp1 + timestamp2

    return {"timestamp1": timestamp1, "timestamp2": timestamp2, "sum": result}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
