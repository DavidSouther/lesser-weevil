#!/usr/bin/python
#
# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from opencensus.trace.ext.grpc import client_interceptor
from opencensus.trace.exporters import stackdriver_exporter
from opencensus.trace.tracer import Tracer
import grpc
import time
import demo_pb2
import demo_pb2_grpc

from logger import getJSONLogger
logger = getJSONLogger('emailservice-client')


try:
    exporter = stackdriver_exporter.StackdriverExporter()
    tracer = Tracer(exporter=exporter)
    tracer_interceptor = client_interceptor.OpenCensusClientInterceptor(
        tracer, host_port='0.0.0.0:8080')
except:
    tracer_interceptor = client_interceptor.OpenCensusClientInterceptor()


class BurstyException(Exception):
    pass


def bursty_crash():
    """Emit an error if called in the first five minutes of odd-number hours."""
    now = time.localtime()
    if (now.tm_hour % 2) & (now.tm_min < 5):
        raise BurstyException('A bursty crash.')


def send_confirmation_email(email, order):
    channel = grpc.insecure_channel('0.0.0.0:8080')
    channel = grpc.intercept_channel(channel, tracer_interceptor)
    stub = demo_pb2_grpc.EmailServiceStub(channel)
    try:
        bursty_crash()
        stub.SendOrderConfirmation(demo_pb2.SendOrderConfirmationRequest(
            email=email,
            order=order
        ))
        logger.info('Request sent.')
    except grpc.RpcError as err:
        logger.error(err.details())
        logger.error('{}, {}'.format(err.code().name, err.code().value))


if __name__ == '__main__':
    logger.info('Client for email service.')
