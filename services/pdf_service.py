"""TimeLens — Professional Heritage Intelligence PDF Generation Service.

Generates comprehensive, publication-grade PDF reports for historical
and modern photographic comparisons using ReportLab.
All generation is strictly in-memory (io.BytesIO) to protect user privacy.
"""

import io
import html
import logging
from datetime import datetime, timezone
from PIL import Image as PILImage

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image as RLImage,
    KeepTogether,
    HRFlowable,
)
from reportlab.pdfgen import canvas

logger = logging.getLogger("timelens.pdf_service")

# -----------------------------------------------------------------------------
# PALETTE DEFINITIONS (DIGITAL HERITAGE THEME)
# -----------------------------------------------------------------------------
C_NAVY_DARK = colors.HexColor("#0B1220")
C_NAVY_CARD = colors.HexColor("#172235")
C_NAVY_LIGHT = colors.HexColor("#223147")
C_GOLD = colors.HexColor("#E8B86D")
C_GOLD_LIGHT = colors.HexColor("#FDF8ED")
C_GOLD_BORDER = colors.HexColor("#C99A4E")
C_GREEN = colors.HexColor("#10B981")
C_AMBER = colors.HexColor("#F59E0B")
C_RED = colors.HexColor("#EF4444")
C_TEXT_DARK = colors.HexColor("#0F172A")
C_TEXT_MUTED = colors.HexColor("#64748B")
C_BG_LIGHT = colors.HexColor("#F8FAFC")
C_BORDER_LIGHT = colors.HexColor("#E2E8F0")
C_WHITE = colors.white


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and render total page count (Page X of Y)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count: int):
        self.saveState()
        # Top banner accent line
        self.setStrokeColor(C_GOLD)
        self.setLineWidth(1.5)
        self.line(36, 805, 559, 805)

        # Footer divider line
        self.setStrokeColor(C_BORDER_LIGHT)
        self.setLineWidth(0.75)
        self.line(36, 40, 559, 40)

        # Footer text
        self.setFont("Helvetica", 8)
        self.setFillColor(C_TEXT_MUTED)
        self.drawString(
            36,
            26,
            "TimeLens Heritage Preservation Intelligence • Open-Source Analysis Powered by Gemma 4",
        )
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(559, 26, page_str)
        self.restoreState()


def _escape(text: str) -> str:
    """Safe XML/HTML escaping for ReportLab Paragraph content."""
    if text is None:
        return ""
    return html.escape(str(text))


def _fit_image_bytes(image_bytes: bytes, max_width: float, max_height: float):
    """Load image bytes with PIL to compute proportional bounding box dimensions,

    returning a ReportLab Image flowable or None on failure.
    """
    if not image_bytes:
        return None
    try:
        with PILImage.open(io.BytesIO(image_bytes)) as pil_img:
            orig_w, orig_h = pil_img.size
            if orig_w <= 0 or orig_h <= 0:
                return None
            ratio = min(max_width / orig_w, max_height / orig_h)
            new_w = orig_w * ratio
            new_h = orig_h * ratio
            return RLImage(io.BytesIO(image_bytes), width=new_w, height=new_h)
    except Exception as exc:
        logger.warning(f"Failed to load image for PDF embedding: {exc}")
        return None


def calculate_preservation_scorecard(report: dict) -> dict:
    """Compute transparent, deterministic preservation metrics and reliability rating.

    Returns dictionary with total changes, preserved count, uncertain count,
    qualitative reliability level, and narrative rationale.
    """
    changes = report.get("changes") or []
    preserved = report.get("preserved_elements") or []
    uncertain = report.get("uncertain_findings") or []
    comp_status = str(report.get("comparison_status", "comparable")).lower()

    num_changes = len(changes)
    num_preserved = len(preserved)
    num_uncertain = len(uncertain)

    if comp_status == "not_comparable":
        reliability = "NOT COMPARABLE"
        badge_color = C_RED
        rationale = "The photographs depict distinct locations or perspectives that cannot be reliably compared."
    elif comp_status == "uncertain" or (num_uncertain > 0 and num_uncertain >= num_changes):
        reliability = "LOW"
        badge_color = C_AMBER
        rationale = "High proportion of uncertain observations due to atmospheric, resolution, or perspective limitations."
    elif num_changes > 0 and num_preserved > 0 and num_uncertain <= 1:
        reliability = "HIGH"
        badge_color = C_GREEN
        rationale = "Strong continuity of identifiable structures coupled with definitive observable visual evolutions."
    else:
        reliability = "MEDIUM"
        badge_color = C_GOLD
        rationale = "Standard comparative confidence with satisfactory photographic overlap and baseline evidence."

    return {
        "total_changes": num_changes,
        "preserved_count": num_preserved,
        "uncertain_count": num_uncertain,
        "reliability": reliability,
        "badge_color": badge_color,
        "rationale": rationale,
    }


def generate_heritage_pdf(
    report: dict,
    before_image_bytes: bytes,
    after_image_bytes: bytes,
    location_name: str = "",
    model_name: str = "gemma-4-26b-a4b-it",
    is_cached: bool = False,
) -> bytes:
    """Generate a high-resolution, multi-page professional PDF heritage intelligence report.

    Parameters:
        report: Validated comparison intelligence schema dict
        before_image_bytes: In-memory raw JPEG/PNG bytes of historical photo
        after_image_bytes: In-memory raw JPEG/PNG bytes of modern photo
        location_name: User-provided or detected location identifier
        model_name: Model identifier used for analysis
        is_cached: Whether analysis originates from benchmark demonstration

    Returns:
        bytes: Complete binary PDF document
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=46,
        bottomMargin=50,
    )

    styles = getSampleStyleSheet()

    # Custom typography styles
    style_header_title = ParagraphStyle(
        "ReportHeaderTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=C_NAVY_DARK,
    )

    style_header_sub = ParagraphStyle(
        "ReportHeaderSub",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=C_TEXT_MUTED,
    )

    style_meta_label = ParagraphStyle(
        "MetaLabel",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        textColor=C_NAVY_CARD,
    )

    style_meta_val = ParagraphStyle(
        "MetaValue",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=C_TEXT_DARK,
    )

    style_section_h1 = ParagraphStyle(
        "SectionH1",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=C_NAVY_DARK,
        spaceBefore=10,
        spaceAfter=4,
    )

    style_body = ParagraphStyle(
        "BodyTextCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12.5,
        textColor=C_TEXT_DARK,
    )

    style_body_muted = ParagraphStyle(
        "BodyMuted",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11.5,
        textColor=C_TEXT_MUTED,
    )

    style_table_header = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=C_WHITE,
    )

    style_table_cell = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=10.5,
        textColor=C_TEXT_DARK,
    )

    style_table_cell_bold = ParagraphStyle(
        "TableCellBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=10.5,
        textColor=C_NAVY_CARD,
    )

    style_caption = ParagraphStyle(
        "ImageCaption",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        alignment=1,  # Centered
        textColor=C_NAVY_CARD,
    )

    story = []

    # -------------------------------------------------------------------------
    # 1. HEADER SECTION
    # -------------------------------------------------------------------------
    title_text = "<b>TIMELENS</b> • HERITAGE PRESERVATION REPORT"
    sub_text = "Automated Multimodal Comparative Intelligence & Architectural Evolution Assessment"

    hdr_data = [
        [
            Paragraph(title_text, style_header_title),
            Paragraph(
                f"<b>Document ID:</b> TL-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M')}<br/>"
                f"<b>Standard:</b> Archival Intelligence v1.1",
                ParagraphStyle("HdrRight", parent=style_header_sub, alignment=2),
            ),
        ],
        [
            Paragraph(sub_text, style_header_sub),
            Paragraph(
                f"<b>Generated:</b> {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
                ParagraphStyle("HdrRightDate", parent=style_header_sub, alignment=2),
            ),
        ],
    ]
    hdr_table = Table(hdr_data, colWidths=[350, 173])
    hdr_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    story.append(hdr_table)
    story.append(Spacer(1, 8))

    # -------------------------------------------------------------------------
    # 2. METADATA & EXECUTIVE SUMMARY CARD
    # -------------------------------------------------------------------------
    loc_display = location_name or report.get("location_name") or "Unspecified Heritage Site"
    comp_status = str(report.get("comparison_status", "comparable")).upper().replace("_", " ")
    same_loc = str(report.get("same_location_assessment", "likely_same")).upper().replace("_", " ")
    mode_display = "Verified Benchmark Archive (Cached)" if is_cached else "Live Gemma 4 Multimodal Inference"

    scorecard = calculate_preservation_scorecard(report)

    meta_content = [
        [
            Paragraph("<b>Target Site:</b>", style_meta_label),
            Paragraph(_escape(loc_display), style_meta_val),
            Paragraph("<b>AI Model:</b>", style_meta_label),
            Paragraph(_escape(model_name), style_meta_val),
        ],
        [
            Paragraph("<b>Status:</b>", style_meta_label),
            Paragraph(f"<b>{_escape(comp_status)}</b>", style_meta_val),
            Paragraph("<b>Assessment:</b>", style_meta_label),
            Paragraph(_escape(same_loc), style_meta_val),
        ],
        [
            Paragraph("<b>Runtime Mode:</b>", style_meta_label),
            Paragraph(_escape(mode_display), style_meta_val),
            Paragraph("<b>Overall Reliability:</b>", style_meta_label),
            Paragraph(f"<b>{scorecard['reliability']}</b>", style_meta_val),
        ],
    ]
    meta_table = Table(meta_content, colWidths=[80, 180, 95, 168])
    meta_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), C_BG_LIGHT),
                ("BOX", (0, 0), (-1, -1), 0.75, C_BORDER_LIGHT),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, C_BORDER_LIGHT),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    story.append(meta_table)
    story.append(Spacer(1, 8))

    # -------------------------------------------------------------------------
    # 3. PRESERVATION SCORECARD DASHBOARD BAR
    # -------------------------------------------------------------------------
    score_data = [
        [
            Paragraph("<b>EVIDENT CHANGES</b>", ParagraphStyle("SC1", parent=style_caption, textColor=C_GOLD_BORDER)),
            Paragraph("<b>PRESERVED STRUCTURES</b>", ParagraphStyle("SC2", parent=style_caption, textColor=C_GREEN)),
            Paragraph("<b>UNCERTAIN FINDINGS</b>", ParagraphStyle("SC3", parent=style_caption, textColor=C_AMBER)),
            Paragraph("<b>PRESERVATION RELIABILITY</b>", ParagraphStyle("SC4", parent=style_caption, textColor=C_NAVY_DARK)),
        ],
        [
            Paragraph(f"<font size=14><b>{scorecard['total_changes']}</b></font>", style_caption),
            Paragraph(f"<font size=14><b>{scorecard['preserved_count']}</b></font>", style_caption),
            Paragraph(f"<font size=14><b>{scorecard['uncertain_count']}</b></font>", style_caption),
            Paragraph(f"<font size=12><b>{scorecard['reliability']}</b></font>", style_caption),
        ],
    ]
    score_table = Table(score_data, colWidths=[130, 131, 131, 131])
    score_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
                ("BOX", (0, 0), (-1, -1), 1, C_BORDER_LIGHT),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, C_BORDER_LIGHT),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ]
        )
    )
    story.append(score_table)
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------------------
    # 4. PHOTOGRAPHIC EVIDENCE PAIR (SIDE-BY-SIDE EMBEDDED)
    # -------------------------------------------------------------------------
    story.append(Paragraph("Photographic Visual Evidence", style_section_h1))

    img_before_flowable = _fit_image_bytes(before_image_bytes, max_width=250, max_height=150)
    img_after_flowable = _fit_image_bytes(after_image_bytes, max_width=250, max_height=150)

    cell_before = img_before_flowable or Paragraph("<i>Historical image unavailable</i>", style_body_muted)
    cell_after = img_after_flowable or Paragraph("<i>Modern image unavailable</i>", style_body_muted)

    photo_grid = [
        [cell_before, cell_after],
        [
            Paragraph("<b>PLATE A: Historical Reference Photograph</b>", style_caption),
            Paragraph("<b>PLATE B: Contemporary Modern Photograph</b>", style_caption),
        ],
    ]
    photo_table = Table(photo_grid, colWidths=[261, 262])
    photo_table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 2),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )
    story.append(photo_table)
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------------------
    # 5. EXECUTIVE SUMMARY
    # -------------------------------------------------------------------------
    summary_text = report.get("summary") or "No comparative summary provided."
    summary_card = [
        [
            Paragraph(
                f"<b>Executive Summary:</b> {_escape(summary_text)}",
                style_body,
            )
        ]
    ]
    summary_table = Table(summary_card, colWidths=[523])
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), C_GOLD_LIGHT),
                ("BOX", (0, 0), (-1, -1), 1, C_GOLD_BORDER),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(summary_table)
    story.append(Spacer(1, 8))

    # -------------------------------------------------------------------------
    # 6. HISTORICAL & MODERN ERA DESCRIPTIONS
    # -------------------------------------------------------------------------
    desc_data = [
        [
            Paragraph(
                f"<b>Historical Setting:</b><br/>{_escape(report.get('before_description', 'N/A'))}",
                style_body,
            ),
            Paragraph(
                f"<b>Modern Evolution:</b><br/>{_escape(report.get('after_description', 'N/A'))}",
                style_body,
            ),
        ]
    ]
    desc_table = Table(desc_data, colWidths=[256, 257])
    desc_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), C_BG_LIGHT),
                ("BOX", (0, 0), (-1, -1), 0.5, C_BORDER_LIGHT),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, C_BORDER_LIGHT),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.append(desc_table)
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------------------
    # 7. OBSERVABLE VISUAL & ARCHITECTURAL CHANGES TABLE
    # -------------------------------------------------------------------------
    changes = report.get("changes") or []
    story.append(
        Paragraph(f"Observable Structural & Environmental Changes ({len(changes)})", style_section_h1)
    )

    if changes:
        changes_rows = [
            [
                Paragraph("<b>Category</b>", style_table_header),
                Paragraph("<b>Observed Evolution</b>", style_table_header),
                Paragraph("<b>Historical Evidence</b>", style_table_header),
                Paragraph("<b>Modern Evidence</b>", style_table_header),
                Paragraph("<b>Certainty</b>", style_table_header),
            ]
        ]
        for c in changes:
            cert_val = str(c.get("certainty", "medium")).upper()
            changes_rows.append(
                [
                    Paragraph(_escape(str(c.get("category", "General"))), style_table_cell_bold),
                    Paragraph(_escape(str(c.get("observation", ""))), style_table_cell),
                    Paragraph(_escape(str(c.get("before_evidence", ""))), style_table_cell),
                    Paragraph(_escape(str(c.get("after_evidence", ""))), style_table_cell),
                    Paragraph(f"<b>{_escape(cert_val)}</b>", style_table_cell),
                ]
            )

        changes_table = Table(changes_rows, colWidths=[70, 138, 125, 130, 60], repeatRows=1)
        changes_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), C_NAVY_DARK),
                    ("BOX", (0, 0), (-1, -1), 0.5, C_BORDER_LIGHT),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, C_BORDER_LIGHT),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        story.append(changes_table)
    else:
        story.append(Paragraph("<i>No structural modifications detected between photographs.</i>", style_body_muted))

    story.append(Spacer(1, 10))

    # -------------------------------------------------------------------------
    # 8. PRESERVED STRUCTURES & UNCERTAIN FINDINGS
    # -------------------------------------------------------------------------
    preserved = report.get("preserved_elements") or []
    uncertain = report.get("uncertain_findings") or []

    pres_paragraphs = [Paragraph("<b>Continuous Preserved Heritage Elements:</b>", style_meta_label)]
    if preserved:
        for p in preserved:
            cert_str = str(p.get("certainty", "high")).upper()
            pres_paragraphs.append(
                Paragraph(
                    f"• <b>{_escape(p.get('element', ''))}</b> [{cert_str}]: {_escape(p.get('observation', ''))}",
                    style_body,
                )
            )
    else:
        pres_paragraphs.append(Paragraph("<i>None documented.</i>", style_body_muted))

    unc_paragraphs = [Paragraph("<b>Documented Uncertainties & Visual Ambiguities:</b>", style_meta_label)]
    if uncertain:
        for u in uncertain:
            unc_paragraphs.append(
                Paragraph(
                    f"• <b>{_escape(u.get('claim', ''))}</b><br/><i>Reason:</i> {_escape(u.get('reason', ''))}",
                    style_body,
                )
            )
    else:
        unc_paragraphs.append(Paragraph("<i>None documented.</i>", style_body_muted))

    two_col_data = [[pres_paragraphs, unc_paragraphs]]
    two_col_table = Table(two_col_data, colWidths=[256, 257])
    two_col_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#F0FDF4")),
                ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#FFFBEB")),
                ("BOX", (0, 0), (0, 0), 0.5, colors.HexColor("#BBF7D0")),
                ("BOX", (1, 0), (1, 0), 0.5, colors.HexColor("#FDE68A")),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.append(two_col_table)
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------------------
    # 9. PRESERVATION INSIGHT & METHODOLOGY NOTICE
    # -------------------------------------------------------------------------
    insight_text = report.get("preservation_insight") or "Continuous monitoring and physical documentation recommended."
    insight_block = [
        [
            Paragraph(
                f"<b>Preservation Specialist Insight:</b><br/>{_escape(insight_text)}",
                style_body,
            )
        ]
    ]
    insight_table = Table(insight_block, colWidths=[523])
    insight_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), C_BG_LIGHT),
                ("BOX", (0, 0), (-1, -1), 0.5, C_BORDER_LIGHT),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(insight_table)
    story.append(Spacer(1, 6))

    methodology_text = (
        "<b>Methodology & Archival Disclaimer:</b> Observations are extracted via Google Gemma 4 "
        "(gemma-4-26b-a4b-it) multimodal comparative reasoning. AI-assisted analysis should be verified "
        "by qualified architectural historians and archival records prior to conservation interventions."
    )
    story.append(Paragraph(methodology_text, style_body_muted))

    # Build PDF with dynamic multi-pass page numbering
    doc.build(story, canvasmaker=NumberedCanvas)

    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
