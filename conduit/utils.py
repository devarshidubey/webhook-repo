import dateutil.parser
from datetime import timezone

def normalize_timestamp(ts):
    dt = dateutil.parser.parse(ts)
    return dt.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'