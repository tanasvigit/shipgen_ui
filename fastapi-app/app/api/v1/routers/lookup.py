from typing import List, Optional, Any
import pytz
import whois
import feedparser
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.routers.auth import _get_current_user
from app.core.database import get_db
from app.core.cache import get_redis
from app.models.user import User

router = APIRouter(prefix="/int/v1/lookup", tags=["lookup"])


@router.get("/timezones", response_model=List[dict])
def get_timezones(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    """Get all available timezones using pytz."""
    timezones = []
    for tz_name in pytz.all_timezones:
        try:
            tz = pytz.timezone(tz_name)
            # Get offset
            now = datetime.now(tz)
            offset = now.strftime("%z")
            offset_formatted = f"{offset[:3]}:{offset[3:]}" if len(offset) == 5 else offset
            
            # Create label
            label = tz_name.replace("_", " ").title()
            timezones.append({
                "value": tz_name,
                "label": f"{label} (UTC{offset_formatted})",
                "offset": offset_formatted
            })
        except Exception:
            continue
    
    # Sort by offset
    timezones.sort(key=lambda x: x.get("offset", ""))
    return timezones


@router.get("/whois", response_model=dict)
def get_whois(
    domain: str = Query(..., description="Domain to lookup"),
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    """Perform WHOIS lookup on a domain."""
    try:
        w = whois.whois(domain)
        result = {
            "domain": domain,
            "registered": w.registered if hasattr(w, 'registered') else None,
            "expires": w.expires if hasattr(w, 'expires') else None,
            "registrar": w.registrar if hasattr(w, 'registrar') else None,
            "name_servers": w.name_servers if hasattr(w, 'name_servers') else [],
            "status": w.status if hasattr(w, 'status') else None,
        }
        return result
    except Exception as e:
        return {
            "domain": domain,
            "error": str(e),
            "message": "WHOIS lookup failed"
        }


@router.get("/currencies", response_model=List[dict])
def get_currencies(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    # Return common currencies
    currencies = [
        {"code": "USD", "name": "US Dollar", "symbol": "$"},
        {"code": "EUR", "name": "Euro", "symbol": "€"},
        {"code": "GBP", "name": "British Pound", "symbol": "£"},
        {"code": "JPY", "name": "Japanese Yen", "symbol": "¥"},
        {"code": "AUD", "name": "Australian Dollar", "symbol": "A$"},
        {"code": "CAD", "name": "Canadian Dollar", "symbol": "C$"},
        {"code": "CHF", "name": "Swiss Franc", "symbol": "CHF"},
        {"code": "CNY", "name": "Chinese Yuan", "symbol": "¥"},
        {"code": "INR", "name": "Indian Rupee", "symbol": "₹"},
    ]
    return currencies


@router.get("/countries", response_model=List[dict])
def get_countries(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    # Return common countries
    countries = [
        {"code": "US", "name": "United States"},
        {"code": "GB", "name": "United Kingdom"},
        {"code": "CA", "name": "Canada"},
        {"code": "AU", "name": "Australia"},
        {"code": "DE", "name": "Germany"},
        {"code": "FR", "name": "France"},
        {"code": "IT", "name": "Italy"},
        {"code": "ES", "name": "Spain"},
        {"code": "NL", "name": "Netherlands"},
        {"code": "BE", "name": "Belgium"},
        {"code": "CH", "name": "Switzerland"},
        {"code": "AT", "name": "Austria"},
        {"code": "SE", "name": "Sweden"},
        {"code": "NO", "name": "Norway"},
        {"code": "DK", "name": "Denmark"},
        {"code": "FI", "name": "Finland"},
        {"code": "PL", "name": "Poland"},
        {"code": "IE", "name": "Ireland"},
        {"code": "PT", "name": "Portugal"},
        {"code": "GR", "name": "Greece"},
        {"code": "CZ", "name": "Czech Republic"},
        {"code": "HU", "name": "Hungary"},
        {"code": "RO", "name": "Romania"},
        {"code": "BG", "name": "Bulgaria"},
        {"code": "HR", "name": "Croatia"},
        {"code": "SK", "name": "Slovakia"},
        {"code": "SI", "name": "Slovenia"},
        {"code": "EE", "name": "Estonia"},
        {"code": "LV", "name": "Latvia"},
        {"code": "LT", "name": "Lithuania"},
        {"code": "LU", "name": "Luxembourg"},
        {"code": "MT", "name": "Malta"},
        {"code": "CY", "name": "Cyprus"},
        {"code": "JP", "name": "Japan"},
        {"code": "CN", "name": "China"},
        {"code": "IN", "name": "India"},
        {"code": "KR", "name": "South Korea"},
        {"code": "SG", "name": "Singapore"},
        {"code": "MY", "name": "Malaysia"},
        {"code": "TH", "name": "Thailand"},
        {"code": "ID", "name": "Indonesia"},
        {"code": "PH", "name": "Philippines"},
        {"code": "VN", "name": "Vietnam"},
        {"code": "NZ", "name": "New Zealand"},
        {"code": "ZA", "name": "South Africa"},
        {"code": "EG", "name": "Egypt"},
        {"code": "NG", "name": "Nigeria"},
        {"code": "KE", "name": "Kenya"},
        {"code": "GH", "name": "Ghana"},
        {"code": "BR", "name": "Brazil"},
        {"code": "MX", "name": "Mexico"},
        {"code": "AR", "name": "Argentina"},
        {"code": "CL", "name": "Chile"},
        {"code": "CO", "name": "Colombia"},
        {"code": "PE", "name": "Peru"},
        {"code": "AE", "name": "United Arab Emirates"},
        {"code": "SA", "name": "Saudi Arabia"},
        {"code": "IL", "name": "Israel"},
        {"code": "TR", "name": "Turkey"},
        {"code": "RU", "name": "Russia"},
    ]
    return countries


@router.get("/country/{code}", response_model=dict)
def get_country(
    code: str,
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    # Return country details
    countries = {
        "US": {"code": "US", "name": "United States", "currency": "USD", "phone_code": "+1"},
        "GB": {"code": "GB", "name": "United Kingdom", "currency": "GBP", "phone_code": "+44"},
        "CA": {"code": "CA", "name": "Canada", "currency": "CAD", "phone_code": "+1"},
        "AU": {"code": "AU", "name": "Australia", "currency": "AUD", "phone_code": "+61"},
    }
    country = countries.get(code.upper())
    if not country:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Country not found")
    return country


@router.get("/shipgen-blog", response_model=List[dict])
def get_shipgen_blog(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
    limit: int = Query(10, ge=1, le=50),
):
    """Fetch blog posts from ShipGen blog RSS feed."""
    blog_url = "https://shipgen.net/blog/feed"  # Update with actual blog URL
    redis_client = get_redis()
    cache_key = "shipgen_blog_feed"
    
    # Try to get from cache first
    try:
        cached = redis_client.get(cache_key)
        if cached:
            import json
            return json.loads(cached)[:limit]
    except Exception:
        pass
    
    try:
        feed = feedparser.parse(blog_url)
        posts = []
        for entry in feed.entries[:limit]:
            posts.append({
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "published": entry.get("published", ""),
                "summary": entry.get("summary", ""),
                "author": entry.get("author", ""),
            })
        
        # Cache for 1 hour
        try:
            import json
            redis_client.setex(cache_key, 3600, json.dumps(posts))
        except Exception:
            pass
        
        return posts
    except Exception as e:
        return []


@router.get("/font-awesome-icons", response_model=List[str])
def get_font_awesome_icons(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    # Return common Font Awesome icons
    icons = [
        "fa-home", "fa-user", "fa-users", "fa-cog", "fa-envelope", "fa-phone",
        "fa-map-marker", "fa-calendar", "fa-clock", "fa-check", "fa-times",
        "fa-plus", "fa-minus", "fa-edit", "fa-trash", "fa-search", "fa-filter",
        "fa-download", "fa-upload", "fa-file", "fa-folder", "fa-image", "fa-video",
        "fa-music", "fa-star", "fa-heart", "fa-thumbs-up", "fa-thumbs-down",
        "fa-share", "fa-comment", "fa-bell", "fa-lock", "fa-unlock", "fa-key",
        "fa-shield", "fa-warning", "fa-info", "fa-question", "fa-exclamation",
    ]
    return icons


@router.post("/refresh-blog-cache", response_model=dict)
def refresh_blog_cache(
    db: Session = Depends(get_db),
    current: User = Depends(_get_current_user),
):
    """Refresh the blog feed cache."""
    redis_client = get_redis()
    cache_key = "shipgen_blog_feed"
    
    try:
        # Delete cache
        redis_client.delete(cache_key)
        
        # Force refresh by fetching
        blog_url = "https://shipgen.net/blog/feed"
        feed = feedparser.parse(blog_url)
        posts = []
        for entry in feed.entries[:50]:
            posts.append({
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "published": entry.get("published", ""),
                "summary": entry.get("summary", ""),
                "author": entry.get("author", ""),
            })
        
        # Cache for 1 hour
        import json
        redis_client.setex(cache_key, 3600, json.dumps(posts))
        
        return {"status": "ok", "message": "Blog cache refreshed", "posts_count": len(posts)}
    except Exception as e:
        return {"status": "error", "message": f"Failed to refresh cache: {str(e)}"}

