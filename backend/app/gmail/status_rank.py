STATUS_RANK={
    "applied":1,
    "interview":2,
    "offer":3,
    "rejected":4
}

def should_update_status(current:str, incoming: str) -> bool:
    if current is None:
        return True
    return STATUS_RANK.get(incoming,0)>=STATUS_RANK.get(current,0)