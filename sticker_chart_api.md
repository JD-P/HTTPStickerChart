GET API:

Variables in this API are given in the query string. Eg. ?action=load_chart&chartname=example

load_chart(chartname) - Load a sticker chart into the chart editors buffer.

get_default_chartname() - Return the default chartname for the application should
                          load initially.

sign_action(action, timeout, username) - Use HMAC to sign a token authorizing the
client to take a specific action (API call) until a timeout given in minutes 
(eg. the argument "15" would mean fifteen minutes from now the token expires) for
the user given by username.

POST API:

Variables in this API are given as key:value pairs in a JSON dictionary in the post
data for the request. All keys are uppercase. eg. For create_chart, {"CHARTNAME":"example"}

create_chart(chartname) - Create a new sticker chart with the name chartname.

rename_chart(oldname, newname) - Rename the chart oldname to newname.

delete_chart(chartname, hmac) - After confirmation of the HMAC, delete the chart
named chartname for session user.

create_column(chartname, columnname) - Add a column named columnname to the sticker 
chart chartname.

delete_column(chartname, columnname, hmac) - After confirmation, delete a column 
named columnname from the sticker chart chartname.

update_row(chartname, row_data) - Update the row representing todays entry to the sticker 
chart to the data given in the array row_data. For example if you have a chart
which tracks three things you would give an array three items long. Each item
must be one of the three strings "white", "lime" or "red". White represents
a neutral/unupdated item, lime represents a completed item, and red represents
an uncompleted/failed item.

refresh_api_key() - Refresh the API key associated with the session user.