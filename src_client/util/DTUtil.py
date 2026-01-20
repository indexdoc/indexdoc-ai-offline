from datetime import datetime

def str2datetime(dtstr):
    if dtstr is None or dtstr == '':
        return None
    return datetime.strptime(dtstr,'%Y-%m-%d %H:%M:%S')

def nowstr(format = '%Y-%m-%d %H:%M:%S'):
    return datetime.now().strftime(format)

def datetime2str(dt:datetime):
    if not isinstance(dt,datetime):
        return None
    return dt.strptime('%Y-%m-%d %H:%M:%S')
