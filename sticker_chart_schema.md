CREATE TABLE chart_entries(chart text, column text, date text, value text, FOREIGN KEY(chart)
REFERENCES templates(chart), FOREIGN KEY(column) REFERENCES templates(column), 
UNIQUE (chart, column, date));

chart	column	date	value

test	test1	2015-11-18	green
test	test2	2015-11-18	red
test	test3	2015-11-18	white

CREATE TABLE templates(chart text, column text, FOREIGN KEY(chart) REFERENCES 
charts(chart), PRIMARY KEY (chart, column));

chart	column
test	test1
test	test2
test	test3

CREATE TABLE charts(chart text PRIMARY KEY);

chart
test
