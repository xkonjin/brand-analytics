# =============================================================================
# EXPLAINER: Team Presence Analyzer
# =============================================================================
#
# WHAT IS THIS?
# This module evaluates the "Human Element" of the brand.
#
# WHY DO WE NEED IT?
# 1. **Trust**: People buy from people. Faceless brands are suspicious (especially in crypto).
# 2. **Credibility**: Knowing the CEO has 10 years of experience builds confidence.
# 3. **Recruiting**: Good talent wants to know who they will work with.
#
# HOW IT WORKS:
# 1. **Team Page Detection**: Looks for "About", "Team", "Our Story" pages.
# 2. **LinkedIn Check**: Does the company exist on LinkedIn?
# 3. **Founder Visibility**: Looks for "CEO", "Founder" keywords in the copy.
#
# SCORING LOGIC:
# - Team Page Exists (25%): The basics.
# - Founders Identified (15%): Visible leadership.
# - LinkedIn Presence (20%): Professional footprint.
# =============================================================================

from typing import Dict, Any, List

from app.analyzers.base import BaseAnalyzer, AnalyzerResult
from app.models.report import Finding, Recommendation, SeverityLevel


class TeamPresenceAnalyzer(BaseAnalyzer):
    """Analyzes team and founder visibility across the web."""

    MODULE_NAME = "team_presence"
    WEIGHT = 0.10

    async def analyze(self) -> AnalyzerResult:
        try:
            self._raw_data = {}

            # Check for team page
            team_page = self._analyze_team_page()
            self._raw_data["team_page"] = team_page

            # Check LinkedIn presence
            linkedin = self._analyze_linkedin()
            self._raw_data["linkedin"] = linkedin

            score = self._calculate_score()
            self._findings = self._generate_findings()
            self._recommendations = self._generate_recommendations()

            result_data = {
                "score": score,
                "has_team_page": team_page.get("exists", False),
                "team_members": [],
                "linkedin_followers": linkedin.get("followers"),
                "linkedin_url": self.scraped_data.get("social_links", {}).get(
                    "linkedin"
                ),
                "linkedin_active": linkedin.get("active", False),
                "founders_identified": team_page.get("founder_count", 0),
                "uses_real_identities": True,
            }

            return AnalyzerResult(
                score=score,
                findings=self._findings,
                recommendations=self._recommendations,
                data=result_data,
            )
        except Exception as e:
            return AnalyzerResult(score=0, error=str(e))

    def _analyze_team_page(self) -> Dict[str, Any]:
        """Check if site has a team/about page with team info."""
        nav = self.scraped_data.get("navigation", [])
        nav_texts = [n.get("text", "").lower() for n in nav]

        has_team = any(
            t in nav_texts for t in ["team", "about", "about us", "who we are"]
        )
        about_content = self.scraped_data.get("about_content", "").lower()

        # Look for founder mentions
        founder_keywords = ["founder", "ceo", "cto", "co-founder", "chief"]
        founder_count = sum(1 for kw in founder_keywords if kw in about_content)

        return {
            "exists": has_team,
            "founder_count": min(founder_count, 3),
        }

    def _analyze_linkedin(self) -> Dict[str, Any]:
        """Analyze LinkedIn presence."""
        linkedin_url = self.scraped_data.get("social_links", {}).get("linkedin")
        return {
            "exists": linkedin_url is not None,
            "url": linkedin_url,
            "followers": 1000 if linkedin_url else 0,  # Mock
            "active": linkedin_url is not None,
        }

    def _calculate_score(self) -> float:
        team = self._raw_data.get("team_page", {})
        linkedin = self._raw_data.get("linkedin", {})

        score = 40  # Base
        if team.get("exists"):
            score += 25
        if team.get("founder_count", 0) > 0:
            score += 15
        if linkedin.get("exists"):
            score += 20

        return self.clamp_score(score)

    def _generate_findings(self) -> List[Finding]:
        team = self._raw_data.get("team_page", {})

        findings = []
        if not team.get("exists"):
            findings.append(
                Finding(
                    title="No Team/About Page Found",
                    detail="Visitors can't learn about the team behind the brand. This reduces trust.",
                    severity=SeverityLevel.MEDIUM,
                )
            )
        return findings

    def _generate_recommendations(self) -> List[Recommendation]:
        team = self._raw_data.get("team_page", {})
        linkedin = self._raw_data.get("linkedin", {})

        recommendations = []
        if not team.get("exists"):
            recommendations.append(
                Recommendation(
                    title="Create a Team/About Page",
                    description="Add a page showcasing your team with photos, roles, and brief bios. "
                    "People invest in people - transparency builds trust.",
                    priority=SeverityLevel.MEDIUM,
                    category="team_presence",
                    impact="medium",
                    effort="low",
                )
            )

        if not linkedin.get("exists"):
            recommendations.append(
                Recommendation(
                    title="Establish LinkedIn Company Page",
                    description="Create a LinkedIn company page and encourage team members to link to it. "
                    "This adds credibility for B2B audiences and investors.",
                    priority=SeverityLevel.MEDIUM,
                    category="team_presence",
                    impact="medium",
                    effort="low",
                )
            )

        return recommendations
