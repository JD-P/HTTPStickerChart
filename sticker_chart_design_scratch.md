Flat file design.

The sticker chart should be a two dimensional array of true/false values that is 
stored in a JSON file that is named the current year and month in YYYY/MM format.
Inside the JSON file is a dictionary of which the keys are names of sticker charts
and the values are two dimensional arrays representing the charts. Sticker chart 
names are case sensitive. Only alphanumeric characters, space dash and underscore
are allowed inside a chart name. Column names do not allow space and are limited 
to 25 characters.

Sticker charts can have columns added and removed from them. Sticker charts 
themselves can be added and removed. (Each of these features should require a 
confirmation prompt to use.)

Declare | Confirm | Action

Scripts needed:

Sticker Table: Add/Remove

Sticker Table Column: Add/Remove

Displaying the chart:

The default chart displayed should be the first in the master list of charts.
A drop down menu should allow one to pick different charts to look at and 
interact with. The chart and the input should be seperated by a horizontal rule.

How to input data:

There should be a drop down menu allowing one to choose which row they would like 
to edit. Since a row can only hold True/False values (keep in mind that each row 
holds the answer to a question formulated as "Did you do X today?" which can only
be answered 'no' conclusively once the day is over, so you only need two values
rather than three.) each column in the row should be filled in by a clearly labelled
(the name of the column it fills in should be on top of) radio button set with Y
or N. The system should update the entire row at once so that incorrectly filled 
in values may be corrected on further entries. However the system should also 
use the already-stored values to 'remember' the user's previous choices in the 
interface so that the user does not need to fill in every field each time one of
them changes.

Confirmation prompt:

Whenever an action is taken to delete an item with the sticker chart API it is 
signed as a HMAC consisting of three things concatenated together as follows:

The Action To Be Taken | A Timeout For The Action | The User For Which Action Is
Taken

These three things are concatenated together with the vertical bar "|" as a
seperator.

The HMAC verifies that:

You were authorized to take this action within this timeframe for this user.

Which prevents:
1. Somebody from just pointing to a delete link, because it won't have a verified action for that user.
2. Somebody from replaying a previous action of that user, since there's a timeout.
3. Somebody from generating a delete link for a different user and then using it for The User because it's authorized by user.

Directory structure:

Installation directory
  - cgi
    - *scripts
  - charts
    - user_account
      - api_key.bin
      - templates
      - *YYYY-MM
  - docs
    - *documentation files
  usernames_passwords

Chart data:

There is a master list of charts which preserves the order of charts. Each actual
chart is a dictionary with the following keys:

name: The name of the sticker chart that distinguishes it from other sticker
charts.

table: The two dimensional array representing the chart.

Charts are a two dimensional array with the first index representing width and
the second index representing height. That is each data structure added to the
first index is a column representing an item being kept track of by the chart.

The first item in each column is the 'title' of the item being kept track of.
These should only include the alphanumeric characters, dash and underscore. There
is a further limit of 25 characters for the title.

Template Data:

Templates are created so that the meta-structure of the sticker chart is preserved 
and used to populate new sticker charts at the end of the month. Templates are 
stored in a JSON file called 'templates' inside of the charts directory. Each
template is stored inside a master list which preserves the order of templates
and thus the order of sticker charts.

name: The name of the sticker chart that distinguishes it from other sticker 
charts.

columns: A list of column names for this chart. These are just strings 
representing the names of columns.