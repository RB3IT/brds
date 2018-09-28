import calendar

EXPORTHEADERS  = ["itemid","date","unitsize","include","itemindex","item",
                  "description","cost","price","quantity"]

## This is the date format that Django Uses, and therefore we work off of
DATEFORMAT = "%Y-%m-%d"

MONTHLIST = list(calendar.month_name)