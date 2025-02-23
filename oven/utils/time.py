import time


def get_current_timestamp() -> int:
    return int(time.time())


def timestamp_to_readable(timestamp: int) -> str:
    readable_time = time.strftime(
        '%a %d %b %Y %I:%M:%S %p %Z', time.localtime(timestamp)
    )
    return readable_time


s_per_m, m_per_h, h_per_d = 60, 60, 24


def seconds_to_adaptive_time_cost(seconds: int) -> str:
    # Calculate the time cost in each units.
    minutes = seconds // s_per_m
    hours = minutes // m_per_h
    days = hours // h_per_d
    # Calculate remaining cost in each level.
    seconds %= s_per_m
    minutes %= m_per_h
    hours %= h_per_d
    # Format the time cost.
    parts = []
    if days > 0:
        parts.append(f'{days}d')
    if hours > 0:
        parts.append(f'{hours}h')
    if minutes > 0:
        parts.append(f'{minutes}m')
    if seconds > 0:
        parts.append(f'{seconds}s')
    # Concatenate the parts.
    if len(parts > 0):
        time_cost = ' '.join(parts)
    else:
        time_cost = '<1s'
    return time_cost
