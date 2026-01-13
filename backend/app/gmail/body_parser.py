import base64


def extract_email_body(payload: dict) -> str:
    """
    Extracts and decodes the plain text body from Gmail message payload.
    """

    def decode(data):
        return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

    # Case 1: Simple email (no parts)
    if "body" in payload and payload["body"].get("data"):
        return decode(payload["body"]["data"])

    # Case 2: Multipart email
    for part in payload.get("parts", []):
        mime = part.get("mimeType", "")
        if mime == "text/plain" and part["body"].get("data"):
            return decode(part["body"]["data"])

    return ""
