from urllib.parse import urlparse
import bz2
import os
import json
import logging
import numpy
from datetime import datetime, timedelta
import requests
from requests.adapters import HTTPAdapter
from requests import Session
from prometheus_api_client.exceptions import PrometheusApiClientException

from prometheus_api_client.prometheus_connect import PrometheusConnect

# set up logging

_LOGGER = logging.getLogger(__name__)

class PromotionPrometheusConnect(PrometheusConnect):
     
    def get_metric_aggregation_promotion(
        self,
        query: str,
        operations: list,
        start_time: datetime = None,
        end_time: datetime = None,
        step: str = "15",
        params: dict = None,
    ):
        """
        Get aggregations on metric values received from PromQL query.

        This method takes as input a string which will be sent as a query to
        the specified Prometheus Host. This query is a PromQL query. And, a
        list of operations to perform such as- sum, max, min, deviation, etc.
        with start_time, end_time and step.

        The received query is passed to the custom_query_range method which returns
        the result of the query and the values are extracted from the result.

        :param query: (str) This is a PromQL query, a few examples can be found
          at https://prometheus.io/docs/prometheus/latest/querying/examples/
        :param operations: (list) A list of operations to perform on the values.
          Operations are specified in string type.
        :param start_time: (datetime) A datetime object that specifies the query range start time.
        :param end_time: (datetime) A datetime object that specifies the query range end time.
        :param step: (str) Query resolution step width in duration format or float number of seconds
        :param params: (dict) Optional dictionary containing GET parameters to be
          sent along with the API request, such as "timeout"
          Available operations - sum, max, min, variance, nth percentile, deviation
          and average.

        :returns: (dict) A dict of aggregated values received in response to the operations
          performed on the values for the query sent.

        Example output:
          .. code-block:: python

            {
                'sum': 18.05674,
                'max': 6.009373
             }
        """
        if not isinstance(operations, list):
            raise TypeError("Operations can be only of type list")
        if len(operations) == 0:
            _LOGGER.debug("No operations found to perform")
            return None
        aggregated_values = {}
        query_values = []
        if start_time is not None and end_time is not None:
            data = self.custom_query_range_promotion(
                query=query, params=params, start_time=start_time, end_time=end_time, step=step
            )
            for result in data:
                values = result["values"]
                for val in values:
                    query_values.append(float(val[1]))
        else:
            data = self.custom_query_promotion(query, params)
            for result in data:
                val = float(result["value"][1])
                query_values.append(val)

        if len(query_values) == 0:
            _LOGGER.debug("No values found for given query.")
            return None

        np_array = numpy.array(query_values)
        for operation in operations:
            if operation == "sum":
                aggregated_values["sum"] = numpy.sum(np_array)
            elif operation == "max":
                aggregated_values["max"] = numpy.max(np_array)
            elif operation == "min":
                aggregated_values["min"] = numpy.min(np_array)
            elif operation == "average":
                aggregated_values["average"] = numpy.average(np_array)
            elif operation.startswith("percentile"):
                percentile = float(operation.split("_")[1])
                aggregated_values["percentile_" + str(percentile)] = numpy.percentile(
                    query_values, percentile
                )
            elif operation == "deviation":
                aggregated_values["deviation"] = numpy.std(np_array)
            elif operation == "variance":
                aggregated_values["variance"] = numpy.var(np_array)
            else:
                raise TypeError("Invalid operation: " + operation)
        return aggregated_values

    def custom_query_promotion(self, query: str, params: dict = None):
        """
        Send a custom query to a Prometheus Host.

        This method takes as input a string which will be sent as a query to
        the specified Prometheus Host. This query is a PromQL query.

        :param query: (str) This is a PromQL query, a few examples can be found
            at https://prometheus.io/docs/prometheus/latest/querying/examples/
        :param params: (dict) Optional dictionary containing GET parameters to be
            sent along with the API request, such as "time"
        :returns: (list) A list of metric data received in response of the query sent
        :raises:
            (RequestException) Raises an exception in case of a connection error
            (PrometheusApiClientException) Raises in case of non 200 response status code
        """
        params = params or {}
        data = None
        query = str(query)
        # using the query API to get raw data
        response = self._session.get(
            "{0}/api/v1/data/metrics".format(self.url),
            params={**{"query": query}, **params},
            verify=self._session.verify,
            headers=self.headers,
            auth=self.auth,
            cert=self._session.cert
        )
        if response.status_code == 200:
            data = response.json()["data"]["result"]
        else:
            raise PrometheusApiClientException(
                "HTTP Status Code {} ({!r})".format(response.status_code, response.content)
            )

        return data

    def custom_query_range_promotion(
        self, query: str, start_time: datetime, end_time: datetime, step: str, params: dict = None
    ):
        """
        Send a query_range to a Prometheus Host.

        This method takes as input a string which will be sent as a query to
        the specified Prometheus Host. This query is a PromQL query.

        :param query: (str) This is a PromQL query, a few examples can be found
            at https://prometheus.io/docs/prometheus/latest/querying/examples/
        :param start_time: (datetime) A datetime object that specifies the query range start time.
        :param end_time: (datetime) A datetime object that specifies the query range end time.
        :param step: (str) Query resolution step width in duration format or float number of seconds
        :param params: (dict) Optional dictionary containing GET parameters to be
            sent along with the API request, such as "timeout"
        :returns: (dict) A dict of metric data received in response of the query sent
        :raises:
            (RequestException) Raises an exception in case of a connection error
            (PrometheusApiClientException) Raises in case of non 200 response status code
        """
        start = round(start_time.timestamp())
        end = round(end_time.timestamp())
        params = params or {}
        data = None
        query = str(query)
        # using the query_range API to get raw data
        response = self._session.get(
            "{0}/api/v1/data/metrics".format(self.url),
            params={**{"query": query, "start": start, "end": end, "step": step}, **params},
            verify=self._session.verify,
            headers=self.headers,
            auth=self.auth,
            cert=self._session.cert
        )
        if response.status_code == 200:
            data = response.json()["data"]["result"]

        else:
            raise PrometheusApiClientException(
                "HTTP Status Code {} ({!r})".format(response.status_code, response.content)
            )
        return data
