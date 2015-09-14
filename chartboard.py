import os
import time
import datetime
import calendar
import json



class application():
    """Main script for HTTPStickerChart. Displays the default sticker chart for
    a given user on login."""
    def __init__(self, environ, start_response):
        self.environ = environ
        self.start = start_response

    def __iter__(self):
        """Parse query string and take an action based on the action parameter
        of the string.

        Each method which can be taken as an action is prepended with the prefix
        do_ and the name of the action appended to it. For example if the query 
        string is ?action=default then the method do_default would be executed.
        """
        query_string = self.environ["QUERY_STRING"]
        if query_string == '':
            self.do_default(self.environ)
        else:
            query_dict = self.parse_query_string(query_string)
            try:
                action = query_dict["ACTION"]
            except KeyError:
                return self.no_action_specified()
            html_gen = getattr(self, "do_" + action)
            page_html = html_gen(self.environ)
        status = '200 OK'
        response_headers = [('Content-type', 'text/plain')]
        self.start(status, response_headers)
        return page_html

    def do_default(self, environ):
        # Access current sticker charts
        parent_directory = self.ascend_directory(__file__, 2)
        charts_directory = os.path.join(parent_directory, "charts")
        user_directory = os.path.join(charts_directory, environ["REMOTE_USER"])
        current_chart = time.strftime("%Y-%m")
        chartpath = os.path.join(user_directory, current_chart)
        try:
            chart_file = open(chartpath)
        except IOError:
            #os.makedirs(os.path.split(chartpath)[0], exist_ok=True)
            with open(chartpath, "w") as chart_file:
                try:
                    charts = self.stock_charts_from_templates(chartpath)
                except NonexistentTemplateFile:
                    with open(templatepath, "w") as templates_file:
                        json.dump(list(), templates_file)
                    charts = self.stock_charts_from_templates(chartpath)
                if charts == list(): # If no charts returned
                    return FUNCTION_CALL # Return message to user asking to make one
                json_charts = json.dump(charts, chart_file)
            chart_file = open(chartpath)
        charts = json.load(chart_file)
        chart = charts[0]
        x_y_table = self.x_to_y(chart["table"])
        return self.format_table(x_y_table)

    def stock_charts_from_templates(self, chartpath):
        """Create sticker chart(s) for the current year and month from the 
        templates given in /charts/templates."""
        charts = []
        current_time = datetime.datetime.now()
        days_in_month = calendar.monthrange(current_time.year, 
                                            current_time.month)[1]
        templatepath = os.path.join(os.path.split(chartpath)[0], "templates")
        try:
            with open(templatepath) as templates_file:
                templates = json.load(templates_file)
        except IOError:
            raise NonexistentTemplateFile(templatepath)
        if templates == list(): # Can't return a chart if there are no templates.
            return templates
        for template in templates:
            chart = {}
            chart["name"] = template["name"]
            chart["table"] = []
            for column_name in template["columns"]:
                column = self.create_column(column_name, days_in_month)
                chart["table"].append(column)
            charts.append(chart)
        return charts

    def create_column(self, column_name, days_in_month):
        """Create a column given the name of the column and the days in the month
        for the chart in which che column goes."""
        column = []
        column[0] = column_name
        for day in days_in_month:
            column.append(None)
        return column

    def format_table(self, y_x_table):
        """Format a table whose first coordinate is the Y axis into HTML for 
        page display."""
        table_head = "<table>\n"
        for row in y_x_table:
            for mark in enumerate(row):
                if mark[1]:
                    row[mark[0]] = '\u263A'
                elif mark[1] is False:
                    row[mark[0]] = '\\'
                else:
                    row[mark[0]] = ' '
        table_data = "".join(
            ["<tr>" + "".join(["<td>" + str(mark) + "</td>" for mark in row]) + "</tr>\n" 
             for row in y_x_table])
        table_tail = "</table>\n"
        return table_head + table_data + table_tail

    def x_to_y(self, table):
        """Convert a two dimensional array whose first coordinate is the X axis
        to one whose first coordinate is the Y axis."""
        days_in_month = len(table[0])
        return [[column[day] for column in table] for day in days_in_month]
            
    def no_charts_to_read(self):
        """HTML page response generated when there are no user created charts to
        read from their accounts chart directory."""
        pass
        # page_html = 

    def no_action_specified(self):
        """Error method called to return a web page when no action is given
        in the query string."""
        page_html = """<html> 
                       <head> 
                       <meta charset='utf-8'> 
                       <title> Error: No Action Given </title>
                       </head>
                       <body>
                       <p> ERROR: No action was given in the query string. </p>
                       </body>
                       </html>"""
        return page_html

    def parse_query_string(self, query_string):
        query_dict = {}
        tokens = query_string.split("&")
        for token in tokens:
            tsplit = token.split("=")
            variable = tsplit[0].upper()
            value = tsplit[1]
            query_dict[variable] = value
        return query_dict

    def ascend_directory(self, filepath, steps):
        """Return a filepath which would correspond to ascending n <steps> of 
        <filepath>."""
        while steps:
            filepath = os.path.split(filepath)[0]
            steps -= 1
        return filepath

class NonexistentTemplateFile(Exception):
    """Error raised when the program attempts to open the template file and it
    does not exist."""
    def __init__(self, filepath="No filepath given."):
        self.filepath = filepath

    def __str__(self):
        return repr(self.filepath)
