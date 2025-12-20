# =============================================================================
# PDF Report Generator
# =============================================================================
# This module generates professional PDF reports from analysis data.
# Uses WeasyPrint for HTML-to-PDF conversion with custom templates.
# =============================================================================

from typing import Dict, Any, Optional
from datetime import datetime

from jinja2 import Environment, BaseLoader


# =============================================================================
# PDF Report Template (HTML/CSS)
# =============================================================================
REPORT_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Brand Analysis Report - {{ url }}</title>
    <style>
        /* Base Styles */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #fff;
            padding: 40px;
        }
        
        /* Header */
        .header {
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 3px solid #2563eb;
        }
        
        .header h1 {
            font-size: 28px;
            color: #1e40af;
            margin-bottom: 10px;
        }
        
        .header .url {
            font-size: 14px;
            color: #6b7280;
        }
        
        .header .date {
            font-size: 12px;
            color: #9ca3af;
            margin-top: 5px;
        }
        
        /* Overall Score */
        .overall-score {
            text-align: center;
            margin: 40px 0;
            padding: 30px;
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            border-radius: 16px;
            color: white;
        }
        
        .overall-score .score-value {
            font-size: 72px;
            font-weight: bold;
        }
        
        .overall-score .score-label {
            font-size: 18px;
            opacity: 0.9;
        }
        
        .overall-score .grade {
            display: inline-block;
            margin-top: 10px;
            padding: 8px 24px;
            background: rgba(255,255,255,0.2);
            border-radius: 20px;
            font-size: 24px;
            font-weight: bold;
        }
        
        /* Score Grid */
        .scores-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin: 30px 0;
        }
        
        .score-card {
            padding: 20px;
            background: #f8fafc;
            border-radius: 12px;
            text-align: center;
            border: 1px solid #e2e8f0;
        }
        
        .score-card .name {
            font-size: 12px;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }
        
        .score-card .value {
            font-size: 32px;
            font-weight: bold;
            color: #1e293b;
        }
        
        .score-card .value.high { color: #16a34a; }
        .score-card .value.medium { color: #ca8a04; }
        .score-card .value.low { color: #dc2626; }
        
        /* Sections */
        .section {
            margin: 40px 0;
            page-break-inside: avoid;
        }
        
        .section h2 {
            font-size: 20px;
            color: #1e40af;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e2e8f0;
        }
        
        .section h3 {
            font-size: 16px;
            color: #374151;
            margin: 20px 0 10px;
        }
        
        /* Findings */
        .findings {
            margin: 20px 0;
        }
        
        .finding {
            padding: 15px;
            margin: 10px 0;
            background: #f8fafc;
            border-left: 4px solid #3b82f6;
            border-radius: 0 8px 8px 0;
        }
        
        .finding.critical { border-left-color: #dc2626; }
        .finding.high { border-left-color: #f97316; }
        .finding.medium { border-left-color: #eab308; }
        .finding.low { border-left-color: #22c55e; }
        
        .finding .title {
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .finding .detail {
            font-size: 14px;
            color: #4b5563;
        }
        
        /* Recommendations */
        .recommendations {
            margin: 30px 0;
        }
        
        .recommendation {
            padding: 20px;
            margin: 15px 0;
            background: linear-gradient(135deg, #eff6ff 0%, #f0fdf4 100%);
            border-radius: 12px;
            border: 1px solid #bfdbfe;
        }
        
        .recommendation .title {
            font-weight: bold;
            color: #1e40af;
            margin-bottom: 8px;
        }
        
        .recommendation .description {
            font-size: 14px;
            color: #374151;
        }
        
        .recommendation .meta {
            margin-top: 10px;
            font-size: 12px;
            color: #6b7280;
        }
        
        .recommendation .meta span {
            margin-right: 15px;
        }
        
        /* Strengths & Weaknesses */
        .strengths-weaknesses {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 20px 0;
        }
        
        .strengths, .weaknesses {
            padding: 20px;
            border-radius: 12px;
        }
        
        .strengths {
            background: #f0fdf4;
            border: 1px solid #86efac;
        }
        
        .weaknesses {
            background: #fef2f2;
            border: 1px solid #fca5a5;
        }
        
        .strengths h4 { color: #16a34a; }
        .weaknesses h4 { color: #dc2626; }
        
        .strengths ul, .weaknesses ul {
            list-style: none;
            margin-top: 10px;
        }
        
        .strengths li::before {
            content: "✓ ";
            color: #16a34a;
        }
        
        .weaknesses li::before {
            content: "✗ ";
            color: #dc2626;
        }
        
        /* Footer */
        .footer {
            margin-top: 60px;
            padding-top: 20px;
            border-top: 1px solid #e2e8f0;
            text-align: center;
            font-size: 12px;
            color: #9ca3af;
        }
        
        /* Page Break */
        .page-break {
            page-break-after: always;
        }
        
        /* Print Styles */
        @media print {
            body {
                padding: 20px;
            }
            
            .section {
                page-break-inside: avoid;
            }
        }
    </style>
</head>
<body>
    <!-- Header -->
    <div class="header">
        <h1>Brand Analysis Report</h1>
        <div class="url">{{ url }}</div>
        <div class="date">Generated on {{ generated_at }}</div>
    </div>
    
    <!-- Overall Score -->
    <div class="overall-score">
        <div class="score-value">{{ overall_score | round }}</div>
        <div class="score-label">Overall Brand Score</div>
        <div class="grade">Grade: {{ grade }}</div>
    </div>
    
    <!-- Scores Grid -->
    <div class="scores-grid">
        {% for name, score in scores.items() %}
        <div class="score-card">
            <div class="name">{{ name | replace('_', ' ') }}</div>
            <div class="value {% if score >= 80 %}high{% elif score >= 60 %}medium{% else %}low{% endif %}">
                {{ score | round }}
            </div>
        </div>
        {% endfor %}
    </div>
    
    <!-- Executive Summary -->
    <div class="section">
        <h2>Executive Summary</h2>
        <p>{{ summary }}</p>
        
        <div class="strengths-weaknesses">
            <div class="strengths">
                <h4>Key Strengths</h4>
                <ul>
                    {% for strength in strengths[:5] %}
                    <li>{{ strength }}</li>
                    {% endfor %}
                </ul>
            </div>
            <div class="weaknesses">
                <h4>Areas for Improvement</h4>
                <ul>
                    {% for weakness in weaknesses[:5] %}
                    <li>{{ weakness }}</li>
                    {% endfor %}
                </ul>
            </div>
        </div>
    </div>
    
    <!-- Top Recommendations -->
    <div class="section">
        <h2>Top Recommendations</h2>
        <div class="recommendations">
            {% for rec in top_recommendations[:5] %}
            <div class="recommendation">
                <div class="title">{{ loop.index }}. {{ rec.title }}</div>
                <div class="description">{{ rec.description }}</div>
                <div class="meta">
                    <span>Impact: {{ rec.impact | upper }}</span>
                    <span>Effort: {{ rec.effort | upper }}</span>
                    <span>Category: {{ rec.category | replace('_', ' ') | title }}</span>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    
    <div class="page-break"></div>
    
    <!-- Detailed Sections -->
    {% for section_name, section_data in sections.items() %}
    <div class="section">
        <h2>{{ section_name | replace('_', ' ') | title }}</h2>
        
        <div class="score-card" style="display: inline-block; min-width: 150px;">
            <div class="name">Score</div>
            <div class="value {% if section_data.score >= 80 %}high{% elif section_data.score >= 60 %}medium{% else %}low{% endif %}">
                {{ section_data.score | round }}
            </div>
        </div>
        
        {% if section_data.findings %}
        <h3>Key Findings</h3>
        <div class="findings">
            {% for finding in section_data.findings[:5] %}
            <div class="finding {{ finding.severity | lower }}">
                <div class="title">{{ finding.title }}</div>
                <div class="detail">{{ finding.detail }}</div>
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        {% if section_data.recommendations %}
        <h3>Recommendations</h3>
        <div class="recommendations">
            {% for rec in section_data.recommendations[:3] %}
            <div class="recommendation">
                <div class="title">{{ rec.title }}</div>
                <div class="description">{{ rec.description }}</div>
            </div>
            {% endfor %}
        </div>
        {% endif %}
    </div>
    {% endfor %}
    
    <!-- Footer -->
    <div class="footer">
        <p>Generated by Brand Analytics Tool</p>
        <p>Report ID: {{ analysis_id }}</p>
    </div>
</body>
</html>
"""


# =============================================================================
# PDF Generation Function
# =============================================================================
async def generate_pdf_report(
    analysis_id: str,
    url: str,
    report: Dict[str, Any],
    scores: Dict[str, float],
    overall_score: float,
) -> bytes:
    """
    Generate a PDF report from analysis data.

    This function:
    1. Prepares the data for the template
    2. Renders the HTML template
    3. Converts HTML to PDF using WeasyPrint

    Args:
        analysis_id: UUID of the analysis
        url: The analyzed URL
        report: Complete report data dictionary
        scores: Individual module scores
        overall_score: Overall weighted score

    Returns:
        bytes: PDF file content
    """
    try:
        from weasyprint import HTML  # noqa: F401
    except ImportError:
        raise RuntimeError(
            "WeasyPrint is not installed. Install it with: pip install weasyprint"
        )

    # -------------------------------------------------------------------------
    # Calculate Grade
    # -------------------------------------------------------------------------
    def get_grade(score: float) -> str:
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    # -------------------------------------------------------------------------
    # Prepare Template Data
    # -------------------------------------------------------------------------
    scorecard = report.get("scorecard", {})

    # Prepare sections data
    sections = {}
    section_keys = [
        "seo",
        "social_media",
        "brand_messaging",
        "website_ux",
        "ai_discoverability",
        "content",
        "team_presence",
        "channel_fit",
    ]

    for key in section_keys:
        if key in report:
            sections[key] = report[key]

    template_data = {
        "analysis_id": analysis_id,
        "url": url,
        "generated_at": datetime.utcnow().strftime("%B %d, %Y at %H:%M UTC"),
        "overall_score": overall_score,
        "grade": get_grade(overall_score),
        "scores": scores,
        "summary": scorecard.get("summary", "Analysis complete."),
        "strengths": scorecard.get("strengths", []),
        "weaknesses": scorecard.get("weaknesses", []),
        "top_recommendations": scorecard.get("top_recommendations", []),
        "sections": sections,
    }

    # -------------------------------------------------------------------------
    # Render Template
    # -------------------------------------------------------------------------
    env = Environment(loader=BaseLoader(), autoescape=True)
    template = env.from_string(REPORT_TEMPLATE)
    html_content = template.render(**template_data)

    # -------------------------------------------------------------------------
    # Generate PDF
    # -------------------------------------------------------------------------
    html = HTML(string=html_content)
    pdf_bytes = html.write_pdf()

    return pdf_bytes


# =============================================================================
# Upload PDF to Storage (Optional)
# =============================================================================
async def upload_pdf_to_storage(
    pdf_bytes: bytes,
    analysis_id: str,
) -> Optional[str]:
    """
    Upload the generated PDF to cloud storage.

    Args:
        pdf_bytes: PDF file content
        analysis_id: UUID of the analysis

    Returns:
        Optional[str]: URL of the uploaded PDF, or None if storage not configured
    """
    from app.config import settings

    if not settings.S3_BUCKET_NAME:
        return None

    try:
        import boto3
        from botocore.config import Config

        # Configure S3 client
        s3_config = Config(
            signature_version="s3v4",
            s3={"addressing_style": "path"},
        )

        s3_client = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
            config=s3_config,
        )

        # Upload file
        key = f"reports/{analysis_id}.pdf"
        s3_client.put_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=key,
            Body=pdf_bytes,
            ContentType="application/pdf",
        )

        # Generate URL
        if settings.S3_ENDPOINT_URL:
            url = f"{settings.S3_ENDPOINT_URL}/{settings.S3_BUCKET_NAME}/{key}"
        else:
            url = f"https://{settings.S3_BUCKET_NAME}.s3.amazonaws.com/{key}"

        return url

    except Exception as e:
        print(f"Failed to upload PDF to storage: {e}")
        return None
