import os
import time
import datetime
import calendar
import json



class AppMain():
    """Main script for HTTPStickerChart. Displays the default sticker chart for
    a given user on login."""
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
        try:
            chart_file = open(chartpath)
        except IOError:

        chart = json.load(chart_file)
        status = '200 OK'
        response_headers = [('Content-type', 'text/plain')]
        self.start(status, response_headers)
        yield HELLO_WORLD


    def stock_charts_from_templates(self, chartpath):
        """Create sticker chart(s) for the current year and month from the 
        templates given in charts/templates."""
        chart_file = open(chartpath, "w")
        current_time = datetime.datetime.now()
        days_in_month = calendar.monthrange(current_time.year, 
                                            current_time.month)[1]
        template_directory = os.path.join(
            os.path.split(chartpath), "templates")
        #Broken right now, committing for others to look at
        for day in days_in_month:
            month_rows.append(list())

    def ascend_directory(self, filepath, steps):
        """Return a filepath which would correspond to ascending n <steps> of 
        <filepath>."""
        while steps:
            filepath = os.path.split(filepath)[0]
        return filepath
