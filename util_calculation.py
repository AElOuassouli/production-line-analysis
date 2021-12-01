from statistics import mean


# compute cycle duration. 
# return a tuple (cycle, first_timestamp) 
# first timestamp corresponds to the first endpoint of a cycle
def compute_cycle_times(exit_timestamps):
    if not exit_timestamps:
        return None, None
    last_exit = exit_timestamps[0][0]
    cycles = []
    timestamps = []
    for t in exit_timestamps[1:]:
        cycles.append(t[0] - last_exit)
        timestamps.append(last_exit)
        last_exit = t[0]
    return cycles, timestamps

### Mean instantaneous cycle time
def compute_avg_instantaneous_cycle_time(exit_timestamps, event_timestamps):
    if len(exit_timestamps) == 0:
        return None
    last_exit = exit_timestamps[0][0]
    cycle_times_overlapping = []
    
    for t in exit_timestamps[1:]:
        if not is_event_overlapping(event_timestamps, last_exit, t[0]):
            cycle_times_overlapping.append(t[0]-last_exit)
        last_exit = t[0]
    return mean(cycle_times_overlapping)


def compute_mean_time_to_fail(cycle_time, nb_parts, nb_blocking_events):
    if cycle_time and nb_parts and nb_blocking_events : 
        return (cycle_time * nb_parts) / (nb_blocking_events - 1)
    else: 
        return None


def get_event_cost_on_cycle_from_overlapping_event(cycle_begin, cycle_end, event_begin, event_end):
    if cycle_begin <= event_begin and cycle_end >= event_end:
        return event_end - event_begin
    elif cycle_begin <= event_begin and cycle_end < event_end:
        return cycle_end - event_begin
    elif cycle_begin > event_begin and cycle_end >= event_end:
        return event_end - cycle_begin
    elif cycle_begin > event_begin and cycle_end < event_end:
        return cycle_end - cycle_begin
    else:
        raise ValueError("Problem in parameters. Should verify time order of cycle or event endpoints.")
    
    

## TODO : operation may be optimized
def is_event_between(event_ordered_timestamps, t_last_exit, t_exit):
    for i in range(len(event_ordered_timestamps)):
        if t_exit < event_ordered_timestamps[i][0]:
            return False 
        if event_ordered_timestamps[i][0] >= t_last_exit and event_ordered_timestamps[i][1] <= t_exit:
            return True
    return False   

## TODO : operation may be optimized
def is_event_overlapping(event_ordered_timestamps, t_last_exit, t_exit):
    for i in range(len(event_ordered_timestamps)):
        if t_exit < event_ordered_timestamps[i][0]:
            return False 
        if (event_ordered_timestamps[i][0] >= t_last_exit and event_ordered_timestamps[i][0] < t_exit) or (event_ordered_timestamps[i][1] > t_last_exit and event_ordered_timestamps[i][1] <= t_exit):
            return True
    return False 

