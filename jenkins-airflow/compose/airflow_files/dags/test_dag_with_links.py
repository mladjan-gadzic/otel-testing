from airflow.decorators import dag, task
from airflow.traces import otel_tracer
from airflow.traces.tracer import Trace

from opentelemetry.trace import Link, NonRecordingSpan

import pendulum

import logging
from pprint import pformat, pprint

# get the airflow.task logger
task_logger = logging.getLogger("airflow.task")

# get the Open Telemetry hook
otel_airflow_tracer = otel_tracer.get_otel_tracer_for_task(Trace)


@task(task_id="alpha")
def alpha_impl(**context):
    task_logger.info("Starting alpha_impl")
    pprint(context)

    root_carrier = None
    with otel_airflow_tracer.start_root_span(span_name="root") as root_s:
        root_carrier = otel_airflow_tracer.inject()
        print("hi_root")

    root_ctx = otel_airflow_tracer.extract(root_carrier)

    start_carrier = None
    with otel_airflow_tracer.start_child_span(span_name="start", parent_context=root_ctx) as start_s:
        start_carrier = otel_airflow_tracer.inject()
        print("hi_root")

    start_ctx = otel_airflow_tracer.extract(start_carrier)

    with otel_airflow_tracer.start_child_span(span_name="task1", parent_context=start_ctx) as task1_s:
        for i in range(3):
            print("Task_1, iteration '%d'.", i)
        print("hi_task1")

    with otel_airflow_tracer.start_child_span(span_name="task2", parent_context=start_ctx) as task2_s:
        for i in range(5):
            print("Task_2, iteration '%d'.", i)
        print("hi_task2")

    context_val = next(iter(start_ctx.values()))
    child_span_context = None
    if isinstance(context_val, NonRecordingSpan):
        child_span_context = context_val.get_span_context()

    links = []
    link = Link(context=child_span_context)
    links.append(link)
    with otel_airflow_tracer.start_child_span(span_name="end", parent_context=root_ctx, links=links) as end_s:
        print("hi_end")


@task(task_id="beta")
def beta_impl(**context):
    import requests

    task_logger.info("Starting beta_impl")
    pprint(context)

    # Get the task instance from the dag context.
    ti = context["ti"]
    # Get the carrier from the task instance.
    context_carrier = ti.context_carrier

    # Check if the context has a value.
    # It won't have a value if otel isn't configured.
    # if context_carrier is not None:

    # Extract the task instance span context from the carrier.
    ti_span_context = Trace.extract(context_carrier)

    with otel_airflow_tracer.start_child_span(span_name="beta_impl", parent_context=ti_span_context) as s:
        task_logger.info("Starting beta_impl inner")

        # If we don't set the parent context, it will get it like so
        # trace.get_current_span().get_span_context()
        # and then start_as_current_span()
        # tracer.start_as_current_span(name="")
        with otel_airflow_tracer.start_child_span(span_name="get_version") as ss:
            response = requests.get("https://api.github.com/users/xBis7/repos")
            task_logger.info("Response: %s", response.json())

            ss.set_attribute("test.version_response", pformat(response.json()))


@dag(
    schedule=None,
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    catchup=False,
    tags=["test"],
)
def test_dag_with_links():
    alpha_task = alpha_impl()
    beta_task = beta_impl()

    alpha_task >> beta_task


test_dag_with_links()
