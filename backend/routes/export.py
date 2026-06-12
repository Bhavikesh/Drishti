from fastapi import APIRouter, Response
from pydantic import BaseModel
from typing import List, Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
import io
from datetime import datetime

router = APIRouter()

class ExportRequest(BaseModel):
    chat_history: List[Dict[str, Any]]
    user_id: int
    role: str
    title: str = "Investigation Report"

@router.post("/pdf")
async def generate_pdf(request: ExportRequest):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Colors
    primary = HexColor('#1e40af')
    dark = HexColor('#1f2937')
    accent = HexColor('#3b82f6')
    light_gray = HexColor('#9ca3af')

    # === Page 1: Header ===
    # Header bar
    p.setFillColor(primary)
    p.rect(0, height - 80, width, 80, fill=1, stroke=0)

    p.setFillColor(HexColor('#ffffff'))
    p.setFont("Helvetica-Bold", 22)
    p.drawString(50, height - 45, "CrimeMind AI")
    p.setFont("Helvetica", 11)
    p.drawString(50, height - 65, "Intelligent Crime Investigation Report — Karnataka State Police")

    # Report metadata
    y = height - 110
    p.setFillColor(dark)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, f"Report: {request.title}")
    y -= 20
    p.setFont("Helvetica", 10)
    p.setFillColor(light_gray)
    p.drawString(50, y, f"Generated: {datetime.now().strftime('%d %B %Y, %I:%M %p')}")
    p.drawString(350, y, f"Officer ID: {request.user_id} ({request.role.upper()})")
    y -= 10

    # Divider
    p.setStrokeColor(accent)
    p.setLineWidth(2)
    p.line(50, y, width - 50, y)
    y -= 25

    # === Chat History ===
    p.setFillColor(dark)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "Investigation Conversation")
    y -= 25

    p.setFont("Helvetica", 10)
    for msg in request.chat_history:
        role_label = "🔵 Officer" if msg.get("role") == "user" else "🤖 CrimeMind AI"
        content = msg.get("content", "")

        # Role header
        p.setFont("Helvetica-Bold", 10)
        p.setFillColor(accent if msg.get("role") == "user" else primary)
        p.drawString(50, y, role_label)
        y -= 15

        # Content
        p.setFont("Helvetica", 9)
        p.setFillColor(dark)
        lines = simpleSplit(content, "Helvetica", 9, width - 120)
        for line in lines:
            if y < 60:
                p.showPage()
                y = height - 50
                p.setFont("Helvetica", 9)
                p.setFillColor(dark)
            p.drawString(65, y, line)
            y -= 13

        y -= 10  # Space between messages

    # === Footer ===
    p.setFont("Helvetica", 8)
    p.setFillColor(light_gray)
    p.drawString(50, 30, "CONFIDENTIAL — Karnataka State Police | CrimeMind AI | For Official Use Only")
    p.drawString(width - 150, 30, f"Page 1")

    p.save()
    buffer.seek(0)

    headers = {
        'Content-Disposition': f'attachment; filename="crimemind_report_{datetime.now().strftime("%Y%m%d_%H%M")}.pdf"'
    }

    return Response(content=buffer.getvalue(), headers=headers, media_type="application/pdf")
