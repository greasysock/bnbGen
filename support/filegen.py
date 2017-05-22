from . import version

__author__ = version.get_author()
__version__ = version.get_version()

def months_con(month):
    months = [
        'Jan',
        'Feb',
        'Mar',
        'Apr',
        'May',
        'Jun',
        'Jul',
        'Aug',
        'Sep',
        'Oct',
        'Nov',
        'Dec'
    ]
    return months[month-1]
def year_trun(year):
    return str(year)[2:]
def filerec(client, month, year):
    return '{} ({}-{}).xlsx'.format(client, months_con(month), year_trun(year))