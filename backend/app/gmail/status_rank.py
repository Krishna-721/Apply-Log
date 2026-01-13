STATUS_RANK={
    "applied":1,
    "interview":2,
    "offer":3,
    "rejected":4
}

def should_update_status(current_status:str, incoming: str) -> bool:
    if current_status is None:
        return True
    if current_status not in STATUS_RANK:
        return True
    if incoming not in STATUS_RANK:
        return False
    
    return STATUS_RANK[incoming] > STATUS_RANK[current_status]