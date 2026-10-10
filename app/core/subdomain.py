from fastapi import Request

def get_subdomain(request: Request) -> str:
    host = request.headers.get("host", "") or ""
    # agung.otopadang.com -> agung
    if "." in host:
        parts = host.split(".")
        if len(parts) >= 3 and parts[0] not in ["www", "api"]:
            return parts[0]
    return "www"

def get_showroom_slug(subdomain: str):
    if subdomain in ["www", "api", "localhost"]:
        return None
    return subdomain
