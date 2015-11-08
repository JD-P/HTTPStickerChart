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
            response_tuple = self.do_default(self.environ)
        else:
            query_dict = self.parse_query_string(query_string)
            try:
                action = query_dict["ACTION"]
            except KeyError:
                yield self.no_action_specified().encode('utf-8')
            html_gen = getattr(self, "do_" + action)
            response_tuple = html_gen(self.environ)
        page_html = response_tuple[0]
        if response_tuple[1]:
            status = response_tuple[1]
        else:
            status = '200 OK'
        if response_tuple[2]:
            response_headers = response_tuple[2]
        else:
            response_headers = [('Content-type', 'text/plain')]
        self.start(status, response_headers)
        yield page_html.encode('utf-8')

    def do_default(self, environ):
        """Display to the user the default view consisting of accessing the first
        sticker chart in the list of sticker charts and displaying it to the user."""
        try:
            username = environ["REMOTE_USER"]
        except KeyError:
            raise UnauthenticatedError
        charts = self.load_charts_for_user(username)
        # If no charts returned, return message to user asking to make one
        if charts == list(): 
            return (self.get_html_chunk("generic_header") + 
                    self.no_chart_could_be_read(), 
                    '200 OK', 
                    [('Content-type', 'text/html')]) 
        chart = charts[0]
        x_y_table = self.x_to_y(chart["table"])
        return (self.format_table(x_y_table), '200 OK', [('Content-type', 'text/html')])

    def do_load_chart(self, environ):
        """Return the chart given by the query string parameter chartname.

        The chart is returned as JSON of the following form:

        {name:<CHARTNAME>,
         table:<TWO DIMENSIONAL ARRAY, WIDTH THEN HEIGHT.>}

         The two dimensional array has columns as its first index and the cells
         for each column-row as its second. The first cell always contains the
         columns name, which is no more than 25 alphanumeric dash and underscore
         characters."""
        query_dict = self.parse_query_string(environ["QUERY_STRING"])
        chartname = query_dict["CHARTNAME"]
        charts = self.load_charts_for_user(environ["REMOTE_USER"])
        for chart in charts:
            if chart["name"] == chartname:
                return (chart, '200 OK', [('Content-type', 'application/json')])
        return ("Chart not found.", '404 Not Found', [('Content-type', 'text/plain')])

    def do_create_chart(self, environ):
        """Create a chart with the name given by the query string parameter 
        chartname.

        create_chart adds a template to the templates and then creates a chart
        instance in the charts file. Before performing this action it checks to
        make sure that no chart with the same name already exists.

        Only alphanumeric, space, dash, and underscore characters are allowed
        inside a chart name. Chartnames have a further 75 character length limit."""
        if environ["REQUEST_METHOD"].upper() != "POST":
            return ("Charts cannot be created through a GET request.",
                    "405 Method Not Allowed", [('Content-type', 'text/plain')])
        query_dict = self.parse_query_string(environ["QUERY_STRING"])
        chartname = query_dict["CHARTNAME"]
        if len(chartname) > 75:
            return ("Chart names cannot be longer than 75 characters.",
                    "400 Bad Request", [('Content-type', 'text/plain')])
        for character in chartname:
            if character not in ("ABCDEFGHIJKLMNOPQRSTUVWXYZ" +
                                 "abcdefghijklmnopqrstuvwxyz" + 
                                 "0123456789 -_"):
                return ("Chart names may only have alphanumeric, space, dash, " + 
                        "and underscore characters.",
                        '400 Bad Request', [('Content-type', 'text/plain')])
        charts = self.load_charts_for_user(environ["REMOTE_USER"])
        for chart in charts:
            if chart["name"] == chartname:
                return ("A chart with this name already exists.", '409 Conflict',
                        [('Content-type', 'text/plain')])
        templates_path = self.find_templates_path(environ["REMOTE_USER"])
        with open(templates_path) as templates_file:
            templates = json.load(templates_file)    
        templates.append({"name":chartname, "columns":[]})
        with open(templates_path, "w") as templates_file:
            json.dump(templates, templates_file)
        chart_path = self.find_charts_path(environ["REMOTE_USER"])
        with open(chart_path) as charts_file:
            charts = json.load(charts_file)
        charts.append({"name":chartname, "table":[]})
        with open(chart_path, "w") as charts_file:
            json.dump(charts, charts_file)
        return ("Success", "200 OK", [('Content-type', 'text/plain')])
            
    def do_create_column(self, environ):
        """Create a column named by the query parameter columnname in the chart 
        given by the query parameter chartname.

        There is a 25 character limit on the length of a columns name. Only the 
        alphanumeric, dash, and underscore characters should be in a column name."""
        query_dict = self.parse_query_string(environ["QUERY_STRING"])
        chartname = query_dict["CHARTNAME"]
        column_name = query_dict["COLUMNNAME"]
        if len(chartname) > 25:
            return ("Column names cannot be longer than 25 characters.",
                    "400 Bad Request", [('Content-type', 'text/plain')])
        for character in chartname:
            if character not in ("ABCDEFGHIJKLMNOPQRSTUVWXYZ" +
                                 "abcdefghijklmnopqrstuvwxyz" + 
                                 "0123456789-_"):
                return ("Column names may only have alphanumeric, dash, " + 
                        "and underscore characters.",
                        '400 Bad Request', [('Content-type', 'text/plain')])
        templates_path = self.find_templates_path(environ["REMOTE_USER"])
        chart_path = self.find_templates_path(environ["REMOTE_USER"])
        with open(templates_path) as templates_file:
            templates = json.load(templates_file)
        with open(chart_path) as charts_file:
            charts = json.load(charts_file)
        for chart_template in templates:
            if chart_template["name"] == chartname:
                chart_template["columns"].append(column_name)
                break
        for chart in charts:
            if chart["name"] == chartname:
                chart["table"].append([column_name])
                break
        with open(templates_path) as templates_file:
            json.dump(templates, templates_file)
        with open(chart_path) as charts_file:
            json.dump(charts, charts_file)
        return ("Success", "200 OK", [('Content-type', 'text/plain')])
        
    def load_charts_for_user(self, username):
        """Load and return the charts file for a given user. Return empty list 
        otherwise."""
        chartpath = self.find_charts_path(username)
        try:
            chart_file = open(chartpath)
        except IOError:
            # If chart file nonexistent try creating default file
            # Start by creating the directory tree for charts
            os.makedirs(os.path.split(chartpath)[0], exist_ok=True)
            # Open the file at the node of the tree we want and write default file
            with open(chartpath, "w") as chart_file:
                try:
                    charts = self.stock_charts_from_templates(chartpath)
                except NonexistentTemplateFile:
                    # If no templates exist, create default templates and retry
                    templatepath = os.path.join(os.path.split(chartpath)[0], "templates")
                    with open(templatepath, "w") as templates_file:
                        json.dump(list(), templates_file)
                    charts = self.stock_charts_from_templates(chartpath)
                json.dump(charts, chart_file) # Dump empty charts for future use
                return charts
        charts = json.load(chart_file)
        return charts

    def find_templates_path(self, username):
        """Find and return the path to the templates file for a given username."""
        parent_directory = self.ascend_directory(__file__, 2)
        return os.path.join(parent_directory, "charts", username, "templates")

    def find_charts_path(self, username):
        """Find and return the path to the charts file for a given username."""
        parent_directory = self.ascend_directory(__file__, 2)
        current_chart = time.strftime("%Y-%m")
        return os.path.join(parent_directory, "charts", username, current_chart)

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
            
    def no_chart_could_be_read(self):
        """HTML page response generated when there are no user created charts to
        read from their accounts chart directory."""
        static_response_html = "  <body>\n<p> You haven't made any charts yet, click "
        dynamic_response_html = "<a href='/cgi/chartboard.py?action=create_chart'>here</a>"
        static_response_tail = " to create one.</p></body>\n</html>"
        return static_response_html + dynamic_response_html + static_response_tail

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

    def get_html_chunk(self, chunk_name, html_directory="default"):
        """
        Get an html chunk from the top level 'html' directory.

        An html chunk is stored under the name <chunk_name>.html and retrieved
        through this function by giving the <chunk_name> as an argument. For
        example if you wanted to get the chunk:

        generic_header.html

        You would pass the string 'generic header' as an argument to 
        get_html_chunk().

        Note: The optional parameter html_directory has a default string of 
        'default' which means that you cannot use a local directory with this
        name as the html_directory.
        """
        if html_directory == 'default':
            html_directory = os.path.join(self.ascend_directory(__file__, 2), "html")
        chunkpath = os.path.join(html_directory, chunk_name + ".html")
        try:
            html_chunk_file = open(chunkpath)
        except IOError:
            raise HTMLChunkNonexistent(chunkpath)
        html_chunk = html_chunk_file.read()
        return html_chunk
        

    def ascend_directory(self, filepath, steps):
        """Return a filepath which would correspond to ascending n <steps> of 
        <filepath>."""
        while steps:
            filepath = os.path.split(filepath)[0]
            steps -= 1
        return filepath

class NonexistentFile(Exception):
    """Error raised when the program attempts to open the template file and it
    does not exist."""
    def __init__(self, filepath="No filepath given."):
        self.filepath = filepath

    def __str__(self):
        return repr(self.filepath)

class NonexistentTemplateFile(NonexistentFile):
    pass

class HTMLChunkNonexistent(NonexistentFile):
    pass

class UnauthenticatedError(Exception):
    """Error raised when a user tries to access a sticker chart but hasn't 
    authenticated with the server."""
    def __init__(self):
        pass

    def __str__(self):
        return "User did not authenticate with the web server."
