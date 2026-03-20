"""
PDF Report Generator
Produces a Trust-Scored Land Allocation Report for download.
"""
import io
from datetime import datetime
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from sqlalchemy.orm import Session

from app.models import Proposal, TrustScore, Conflict, AuditLog


# Color palette
NREDCAP_GREEN = colors.HexColor("#1B6B3A")
NREDCAP_BLUE = colors.HexColor("#003580")
GRADE_COLORS = {
    "A": colors.HexColor("#22c55e"),
    "B": colors.HexColor("#3b82f6"),
    "C": colors.HexColor("#f59e0b"),
    "D": colors.HexColor("#ef4444"),
}


def generate_allocation_report(proposal: Proposal, db: Session) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm,
                            leftMargin=2*cm, rightMargin=2*cm)
    styles = getSampleStyleSheet()

    heading1 = ParagraphStyle("h1", parent=styles["Heading1"], textColor=NREDCAP_BLUE, fontSize=16)
    heading2 = ParagraphStyle("h2", parent=styles["Heading2"], textColor=NREDCAP_GREEN, fontSize=12)
    body = ParagraphStyle("body", parent=styles["Normal"], fontSize=9, leading=14)
    center = ParagraphStyle("center", parent=styles["Normal"], alignment=TA_CENTER, fontSize=9)

    story = []

    # Header
    story.append(Paragraph("NREDCAP — Trust-Scored Land Allocation Report", heading1))
    story.append(Paragraph("Ooumph Agentic AI Ecosystem | Government of Andhra Pradesh", center))
    story.append(HRFlowable(width="100%", thickness=2, color=NREDCAP_BLUE))
    story.append(Spacer(1, 0.4*cm))

    # Proposal summary
    story.append(Paragraph("1. Proposal Summary", heading2))
    meta = [
        ["Proposal ID", str(proposal.id)],
        ["Project Type", proposal.project_type.value.upper()],
        ["Capacity (MW)", str(proposal.capacity_mw)],
        ["District", proposal.district],
        ["Submitted", proposal.submitted_at.strftime("%d-%b-%Y %H:%M UTC") if proposal.submitted_at else "—"],
        ["Status", proposal.status.value.upper()],
    ]
    t = Table(meta, colWidths=[5*cm, 12*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f0f4f8")),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.4*cm))

    # Trust Score
    ts: TrustScore | None = proposal.trust_score
    if ts:
        story.append(Paragraph("2. Land Parcel Trust Score", heading2))
        grade_color = GRADE_COLORS.get(ts.grade.value, colors.grey)
        score_data = [
            ["Overall Score", f"{ts.overall_score:.1f} / 100"],
            ["Grade", ts.grade.value],
            ["Computed At", ts.computed_at.strftime("%d-%b-%Y %H:%M UTC")],
        ]
        st = Table(score_data, colWidths=[5*cm, 12*cm])
        st.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f0f4f8")),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("PADDING", (0, 0), (-1, -1), 7),
            ("TEXTCOLOR", (1, 1), (1, 1), grade_color),
        ]))
        story.append(st)
        story.append(Spacer(1, 0.3*cm))

        # Factor breakdown
        story.append(Paragraph("Trust Score Factor Breakdown:", body))
        factors = ts.factor_breakdown or {}
        factor_labels = {
            "clean_title": "Clean Title Verification (max 25)",
            "no_disputes": "No Active Disputes / Litigation (max 20)",
            "environmental_clearance": "Environmental Clearance Status (max 20)",
            "grid_connectivity": "Grid Connectivity Feasibility (max 15)",
            "satellite_characteristics": "Satellite-Verified Land Characteristics (max 10)",
            "historical_allocation": "Historical Allocation Success Rate (max 10)",
        }
        fd_data = [["Factor", "Score"]]
        for key, label in factor_labels.items():
            fd_data.append([label, f"{factors.get(key, 0):.1f}"])
        ft = Table(fd_data, colWidths=[12*cm, 5*cm])
        ft.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), NREDCAP_GREEN),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("PADDING", (0, 0), (-1, -1), 6),
            ("ALIGN", (1, 0), (1, -1), "CENTER"),
        ]))
        story.append(ft)
        story.append(Spacer(1, 0.4*cm))

    # Conflict Matrix
    conflicts: list[Conflict] = proposal.conflicts
    story.append(Paragraph("3. Conflict Matrix", heading2))
    if conflicts:
        conf_data = [["Type", "Severity", "Department", "Description"]]
        for c in conflicts:
            conf_data.append([
                c.conflict_type.replace("_", " ").title(),
                c.severity.value.upper(),
                c.source_department or "—",
                (c.description or "")[:80],
            ])
        ct = Table(conf_data, colWidths=[4*cm, 2.5*cm, 4*cm, 6.5*cm])
        ct.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#7f1d1d")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("PADDING", (0, 0), (-1, -1), 5),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fef2f2")]),
        ]))
        story.append(ct)
    else:
        story.append(Paragraph("✅ No conflicts detected.", body))
    story.append(Spacer(1, 0.4*cm))

    # FTM Council Decision
    council = proposal.council_decision_json or {}
    if council:
        story.append(Paragraph("4. FTM Council Decision", heading2))
        story.append(Paragraph(council.get("council_summary", "No summary available."), body))
        story.append(Spacer(1, 0.2*cm))
        actions = council.get("recommended_actions", [])
        if actions:
            story.append(Paragraph("Recommended Actions:", body))
            for action in actions:
                story.append(Paragraph(f"• {action}", body))
        story.append(Spacer(1, 0.4*cm))

    # Audit Trail (last 5 entries)
    audit_logs: list[AuditLog] = proposal.audit_logs[-5:] if proposal.audit_logs else []
    story.append(Paragraph("5. Audit Trail (Recent Entries)", heading2))
    if audit_logs:
        audit_data = [["Timestamp", "Agent", "Action", "Hash"]]
        for log in audit_logs:
            audit_data.append([
                log.timestamp.strftime("%d-%b-%Y %H:%M"),
                log.agent_name[:20],
                log.action[:30],
                log.chain_hash[:16] + "...",
            ])
        at = Table(audit_data, colWidths=[3.5*cm, 4*cm, 5*cm, 4.5*cm])
        at.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), NREDCAP_BLUE),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
            ("PADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(at)

    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
    story.append(Paragraph(
        f"Generated by Ooumph Agentic AI Ecosystem | {datetime.utcnow().strftime('%d-%b-%Y %H:%M UTC')} | Advisory Only — Final decision authority rests with NREDCAP officers",
        ParagraphStyle("footer", parent=styles["Normal"], fontSize=7, textColor=colors.grey, alignment=TA_CENTER)
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()
