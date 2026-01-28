from django.http import JsonResponse
from django.db import connection
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta

from .models import Paste
from .serializer import PasteCreateSerializer
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Paste
import os
from django.utils import timezone
from datetime import datetime
from django.shortcuts import render


@api_view(["GET"])
def fetch_paste(request, id):
    paste = get_object_or_404(Paste, id=id)

    now = get_now(request)

    #  TTL expired
    if paste.expires_at and now >= paste.expires_at:
        return Response(
            {"error": "Paste expired"},
            status=status.HTTP_404_NOT_FOUND
        )

    #  View limit exceeded
    if paste.max_views is not None and paste.current_views >= paste.max_views:
        return Response(
            {"error": "View limit exceeded"},
            status=status.HTTP_404_NOT_FOUND
        )

    # ✅ Paste is valid → increment views
    paste.current_views += 1
    paste.save(update_fields=["current_views"])

    remaining_views = None
    if paste.max_views is not None:
        remaining_views = paste.max_views - paste.current_views

    return Response(
        {
            "content": paste.content,
            "remaining_views": remaining_views,
            "expires_at": paste.expires_at
        },
        status=status.HTTP_200_OK
    )


@api_view(["POST"])
def create_paste(request):
    serializer = PasteCreateSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            {"error": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    content = serializer.validated_data["content"]
    ttl_seconds = serializer.validated_data.get("ttl_seconds")
    max_views = serializer.validated_data.get("max_views")

    expires_at = None
    if ttl_seconds:
        expires_at = timezone.now() + timedelta(seconds=ttl_seconds)

    paste = Paste.objects.create(
        content=content,
        expires_at=expires_at,
        max_views=max_views
    )

    return Response(
        {
            "id": str(paste.id),
            "url": request.build_absolute_uri(f"/p/{paste.id}")
        },
        status=status.HTTP_201_CREATED
    )


def get_now(request):
    """
    Returns current time.
    Uses test time if TEST_MODE=1
    """
    if os.getenv("TEST_MODE") == "1":
        test_now_ms = request.headers.get("x-test-now-ms")
        if test_now_ms:
            return datetime.fromtimestamp(int(test_now_ms) / 1000, tz=timezone.utc)
    return timezone.now()



def health_check(request):
    try:
        # simple DB check
        connection.ensure_connection()
        return JsonResponse({"ok": True}, status=200)
    except Exception:
        return JsonResponse({"ok": False}, status=500)
    

def view_paste_html(request, id):
    try:
        paste = Paste.objects.get(id=id)
    except Paste.DoesNotExist:
        return render(request, "pastes/paste_404.html", status=404)

    now = get_now(request)

    # TTL expired
    if paste.expires_at and now >= paste.expires_at:
        return render(request, "pastes/paste_404.html", status=404)

    # View limit exceeded
    if paste.max_views is not None and paste.current_views >= paste.max_views:
        return render(request, "pastes/paste_404.html", status=404)

    # Valid view → increment
    paste.current_views += 1
    paste.save(update_fields=["current_views"])

    remaining_views = None
    if paste.max_views is not None:
        remaining_views = paste.max_views - paste.current_views

    context = {
        "content": paste.content,
        "remaining_views": remaining_views,
        "expires_at": paste.expires_at,
    }

    return render(request, "pastes/paste_view.html", context)
def create_paste_ui(request):
    context = {}

    if request.method == "POST":
        content = request.POST.get("content")
        ttl_seconds = request.POST.get("ttl_seconds")
        max_views = request.POST.get("max_views")

        if not content:
            context["error"] = "Content is required"
            return render(request, "pastes/create_paste.html", context)

        expires_at = None
        if ttl_seconds:
            expires_at = timezone.now() + timedelta(seconds=int(ttl_seconds))

        paste = Paste.objects.create(
            content=content,
            expires_at=expires_at,
            max_views=int(max_views) if max_views else None
        )

        context["paste_url"] = request.build_absolute_uri(f"/p/{paste.id}")

    return render(request, "pastes/create_paste.html", context)


# Create your views here.
