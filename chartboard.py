import os
import time
import datetime
import json



class AppMain():
    def __init__(self, environ, start_response):
        self.environ = environ
        self.start = start_response

    def __iter__(self):
        # Access current sticker charts
        parent_directory = self.ascend_directory(__file__, 2)
        charts_directory = os.path.join(parent_directory, "charts")
        charts = os.listdir(charts_directory)
        current_chart = time.strftime("%Y-%m")
        chartpath = os.path.join(charts_directory, current_chart)
        chart_file = open(chartpath)
        chart = json.load(chart_file)
        status = '200 OK'
        response_headers = [('Content-type', 'text/plain')]
        self.start(status, response_headers)
        yield HELLO_WORLD

    def ascend_directory(self, filepath, steps):
        """Return a filepath which would correspond to ascending n <steps> of 
        <filepath>."""
        while steps:
            filepath = os.path.split(filepath)[0]
        return filepath
