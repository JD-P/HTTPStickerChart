import os
import time
import datetime
import calendar
import sqlite3
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
            response_tuple = (open('root/index.html').read(), '200 OK', 
                              [('Content-type', 'text/html')])
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

    # GET API

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
        month_before = (time.strftime("%Y-") + str(int(time.strftime("%m")) - 1) +
                        time.strftime("-%d"))
        month_after = (time.strftime("%Y-") + str(int(time.strftime("%m")) + 1) +
                       time.strftime("-%d"))
        database = self.load_charts_for_user(environ["REMOTE_USER"])
        cursor = database.cursor()
        # Test that chart exists
        cursor.execute("select * from charts where chart=?;", (chartname,))
        charts = cursor.fetchone()
        if not charts:
            return ("Chart not found.", '404 Not Found', [('Content-type', 'text/plain')])
        cursor.execute("select * from chart_entries where chart=? AND ? < date < ? order by date, column;", 
                       (chartname, month_before, month_after))
        entries = cursor.fetchall()
        dates = set()
        for entry in entries:
            entry_date = entry[2]
            dates.add(entry_date)
        rows = []
        for date in dates:
            row = []
            for entry in entries:
                entry_value = entry[3]
                entry_date = entry[2]
                if entry_date == date:
                    row.append(entry_value)
            rows.append(row)
        database.close()
        return (json.dumps(rows), '200 OK', [('Content-type', 'application/json')])

    def do_get_default_chartname(self, environ):
        """Return the name of the chart which should be loaded at application 
        initialization."""
        database = self.load_charts_for_user(environ["REMOTE_USER"])
        cursor = database.cursor()
        cursor.execute("select rowid, chart from charts order by id;")
        charts = cursor.fetchall()
        default_chart = dict(CHARTNAME=charts[0][1])
        return (json.dumps(default_chart), '200 OK', [('Content-type', 'application/json')])

    # POST API

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
        
        content_length = int(environ["CONTENT_LENGTH"]) 
        post_dict_json = environ['wsgi.input'].read(content_length).decode('utf-8') 
        post_dict = json.loads(post_dict_json)
        chartname = post_dict["CHARTNAME"]
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
        database = self.load_charts_for_user(environ["REMOTE_USER"])
        cursor = database.cursor()
        cursor.execute("insert into charts values(?);", (chartname,))
        database.commit()
        database.close()
        return ("Success", "200 OK", [('Content-type', 'text/plain')])
            
    def do_create_column(self, environ):
        """Create a column named by the query parameter columnname in the chart 
        given by the query parameter chartname.

        There is a 25 character limit on the length of a columns name. Only the 
        alphanumeric, dash, and underscore characters should be in a column name."""
        if environ["REQUEST_METHOD"].upper() != "POST":
            return ("Columns cannot be created through a GET request.",
                    "405 Method Not Allowed", [('Content-type', 'text/plain')])
        content_length = int(environ["CONTENT_LENGTH"])
        post_dict_json = environ['wsgi.input'].read(content_length).decode('utf-8')
        post_dict = json.loads(post_dict_json)
        chartname = post_dict["CHARTNAME"]
        column_name = post_dict["COLUMNNAME"]
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
        database = self.load_charts_for_user(environ["REMOTE_USER"])
        cursor = database.cursor()
        # Test to make sure that chartname is in charts table
        cursor.execute("select * from charts where chart=?;", (chartname,))
        charts = cursor.fetchone()
        if not charts:
            return ("Chart not found.", "404 Not Found", [('Content-type', 'text/plain')])
        cursor.execute("insert into templates values(?, ?);", (chartname, column_name))
        database.commit()
        database.close()
        return ("Success", "200 OK", [('Content-type', 'text/plain')])

    def do_update_row(self, environ):
        """Update the row representing todays entry to the sticker chart data.
        
        The row data is given in the query string variable row_data as a comma
        seperated value list. The three valid values are 'white', 'lime' and 
        'red'. These represent null true and false respectively.
        """
        if environ["REQUEST_METHOD"].upper() != "POST":
            return ("Rows cannot be updated through a GET request.",
                    "405 Method Not Allowed", [('Content-type', 'text/plain')])
        content_length = int(environ["CONTENT_LENGTH"])
        post_dict_json = environ['wsgi.input'].read(content_length).decode('utf-8')
        post_dict = json.loads(post_dict_json)
        chartname = post_dict["CHARTNAME"]
        row_data = post_dict["ROW_DATA"].split(",")
        current_date = time.strftime("%Y-%m-%d")
        database = self.load_charts_for_user(environ["REMOTE_USER"])
        cursor = database.cursor()
        cursor.execute("select * from charts where chart=?;", (chartname,))
        charts = cursor.fetchone()
        if not charts:
            return ("Chart not found.", "404 Not Found", [('Content-type', 'text/plain')])
        cursor.execute("select * from chart_entries where date=?;", (current_date,))
        previous = cursor.fetchall()
        if previous:
            cursor.execute("delete from chart_entries where date=?;", (current_date,))
        cursor.execute("select * from templates where chart=?", (chartname,))
        columns = cursor.fetchall()
        for value in enumerate(row_data):
            cursor.execute("insert into chart_entries values(?, ?, ?, ?);", 
                           (chartname, columns[value[0]][1], 
                            time.strftime("%Y-%m-%d"), value[1]))
        database.commit()
        database.close()                 
        return ("Row updated.", "200 OK", [('Content-type', 'text/plain')])
        
        
    def load_charts_for_user(self, username):
        """Load and return the charts file for a given user. Return empty list 
        otherwise."""
        chartpath = self.find_charts_path(username)
        if os.path.exists(chartpath):
            return sqlite3.connect(chartpath)
        else:
            database = sqlite3.connect(chartpath)
            init_cursor = database.cursor()
            init_cursor.execute("CREATE TABLE charts(chart text PRIMARY KEY;")
            init_cursor.execute("CREATE TABLE templates(chart text, column text, " +
                                "FOREIGN KEY(chart) REFERENCES charts(chart), " + 
                                "PRIMARY KEY (chart, column));")
            init_cursor.execute("CREATE TABLE chart_entries(chart text, column " + 
                                "text, date text, value text, FOREIGN KEY(chart)" +
                                "REFERENCES templates(chart), FOREIGN KEY(column)" + 
                                " REFERENCES templates(column), UNIQUE (chart, " + 
                                "column, date));")
            database.commit()
            init_cursor.close()
            return database

    def find_charts_path(self, username):
        """Find and return the path to the charts file for a given username."""
        parent_directory = self.ascend_directory(__file__, 2)
        return os.path.join(parent_directory, "charts", username, "charts.sqlite")
            
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
