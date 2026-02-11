from fastapi import Request


def extract_client_ip(request: Request) -> str | None:
    forwarded_for = request.headers.get("x-forwarded-for", "")
    if forwarded_for:
        first_forwarded_ip = forwarded_for.split(",")[0].strip()
        if first_forwarded_ip:
            return first_forwarded_ip

    real_ip = request.headers.get("x-real-ip", "").strip()
    if real_ip:
        return real_ip

    if request.client:
        return request.client.host

    return None


def extract_user_agent(request: Request) -> str | None:
    user_agent = request.headers.get("user-agent", "").strip()
    return user_agent or None
