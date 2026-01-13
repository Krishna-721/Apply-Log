APPLICATION_PHRASES = [
    "thank you for applying",
    "thanks for applying",
    "application received",
    "your application has been submitted",
    "successfully applied",
]

REJECTION_PHRASES = [
    "we regret to inform",
    "unfortunately",
    "not moving forward",
    "application was not successful",
    "we have decided not to proceed",
    "rejected",
]

INTERVIEW_PHRASES = [
    "interview invitation",
    "interview schedule",
    "interview round",
    "next round interview",
    "shortlisted",
    "assessment",
    "coding test",
]


OFFER_PHRASES = [
    "congratulations",
    "offer letter",
    "we are pleased to offer",
    "job offer",
]

SPAM_PHRASES = [
    "matching jobs",
    "hot jobs",
    "job alert",
    "recommended jobs",
    "top jobs",
    "based on your preferences",
    "opportunities waiting",
    "10+",
    "top jobs",
    "matching jobs",
    "hot job",
    "daily jobs"
]

ALLOWED_DOMAINS = [
    "lever.co",
    "greenhouse.io",
    "workday.com",
    "ashbyhq.com",
    "hire.lever.co"
]

def is_spam(subject: str) -> bool:
    subject = subject.lower()
    return any(k in subject for k in SPAM_PHRASES)

def is_allowed_sender(sender: str) -> bool:
    sender = sender.lower()
    return any(domain in sender for domain in ALLOWED_DOMAINS)

def classify_job_event(subject: str, body: str):
    s = subject.lower()
    b = body.lower()

    if "thank you for applying" in s or "application submitted" in s:
        return "applied"
    if "interview" in s or "interview" in b:
        return "interview"
    if "offer" in s or "offer" in b:
        return "offer"
    if "unfortunately" in s or "regret to inform" in b:
        return "rejected"

    return None