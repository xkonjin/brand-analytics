# =============================================================================
# EXPLAINER: Website UX & Conversion Analyzer
# =============================================================================
#
# WHAT IS THIS?
# This module evaluates the website from a Conversion Rate Optimization (CRO) perspective.
#
# WHY DO WE NEED IT?
# 1. **Conversion**: Traffic is useless if it doesn't convert.
# 2. **Clarity**: "Don't Make Me Think" - Steve Krug. Users should know what to do instantly.
# 3. **Trust**: Trust seals (logos, badges) increase conversion by 48% (Baymard Institute).
#
# HOW IT WORKS:
# 1. **Clarity Check**: Does the text above the fold answer "What", "Who", "Why"?
# 2. **CTA Audit**: Is there a button? Is it visible? Is the text actionable?
# 3. **Trust Audit**: Scans for "Testimonials", "Reviews", "Trusted By" sections.
# 4. **Navigation Check**: Is the menu bloated? (Hick's Law: more choices = less action).
#
# SCORING LOGIC (Total 100):
# - First Impression (25%): The 5-second test.
# - CTA Effectiveness (25%): The path to conversion.
# - Trust Signals (20%): Social proof.
# - Navigation (20%): Usability.
# - Mobile (10%): Responsiveness.
# =============================================================================

from typing import Dict, Any, List

from app.config import settings
from app.analyzers.base import BaseAnalyzer, AnalyzerResult
from app.models.report import (
    Finding, Recommendation, SeverityLevel,
    CTAAnalysis,
)


class UXAnalyzer(BaseAnalyzer):
    """
    Analyzes Website UX & Conversion Optimization.
    """
    
    MODULE_NAME = "website_ux"
    WEIGHT = 0.15
    
    async def analyze(self) -> AnalyzerResult:
        try:
            self._raw_data = {}
            
            # ----------------------------------------------------------------
            # 1. Analyze first impression/clarity
            # ----------------------------------------------------------------
            clarity = self._analyze_first_impression()
            self._raw_data["clarity"] = clarity
            
            # ----------------------------------------------------------------
            # 2. Analyze CTAs
            # ----------------------------------------------------------------
            cta_analysis = self._analyze_ctas()
            self._raw_data["cta"] = cta_analysis
            
            # ----------------------------------------------------------------
            # 3. Analyze navigation
            # ----------------------------------------------------------------
            navigation = self._analyze_navigation()
            self._raw_data["navigation"] = navigation
            
            # ----------------------------------------------------------------
            # 4. Analyze trust signals
            # ----------------------------------------------------------------
            trust = self._analyze_trust_signals()
            self._raw_data["trust"] = trust
            
            # ----------------------------------------------------------------
            # 5. Analyze mobile/accessibility
            # ----------------------------------------------------------------
            mobile = self._analyze_mobile_accessibility()
            self._raw_data["mobile"] = mobile
            
            # ----------------------------------------------------------------
            # 6. Calculate score
            # ----------------------------------------------------------------
            score = self._calculate_score()
            
            # ----------------------------------------------------------------
            # 7. Generate findings and recommendations
            # ----------------------------------------------------------------
            self._findings = self._generate_findings()
            self._recommendations = self._generate_recommendations()
            
            result_data = {
                "score": score,
                "first_impression_clarity": clarity.get("score", 5),
                "answers_what": clarity.get("answers_what", False),
                "answers_who": clarity.get("answers_who", False),
                "answers_why": clarity.get("answers_why", False),
                "cta_analysis": cta_analysis,
                "menu_items_count": navigation.get("item_count", 0),
                "has_clear_navigation": navigation.get("is_clear", False),
                "has_search": navigation.get("has_search", False),
                "has_testimonials": trust.get("has_testimonials", False),
                "has_client_logos": trust.get("has_logos", False),
                "has_case_studies": trust.get("has_case_studies", False),
                "has_security_badges": trust.get("has_security", False),
                "has_social_proof_numbers": trust.get("has_numbers", False),
                "trust_signals_count": trust.get("count", 0),
                "mobile_responsive": mobile.get("responsive", False),
                "has_privacy_policy": navigation.get("has_privacy", False),
                "has_terms_of_service": navigation.get("has_terms", False),
            }
            
            return AnalyzerResult(
                score=score,
                findings=self._findings,
                recommendations=self._recommendations,
                data=result_data,
            )
            
        except Exception as e:
            return AnalyzerResult(
                score=0,
                error=f"UX analysis failed: {str(e)}",
            )
    
    def _analyze_first_impression(self) -> Dict[str, Any]:
        """
        Analyze if the homepage clearly answers the key questions.
        """
        h1s = self.scraped_data.get("headings", {}).get("h1", [])
        h2s = self.scraped_data.get("headings", {}).get("h2", [])
        paragraphs = self.scraped_data.get("paragraphs", [])
        
        # Check for "what" - product description
        what_keywords = ["platform", "app", "tool", "software", "service", "solution", "helps"]
        answers_what = any(
            any(kw in text.lower() for kw in what_keywords)
            for text in h1s + h2s + paragraphs[:3]
        )
        
        # Check for "who" - target audience
        who_keywords = ["for", "teams", "businesses", "developers", "creators", "professionals"]
        answers_who = any(
            any(kw in text.lower() for kw in who_keywords)
            for text in h1s + h2s + paragraphs[:3]
        )
        
        # Check for "why" - benefit/value
        why_keywords = ["save", "faster", "easier", "better", "simple", "powerful", "free"]
        answers_why = any(
            any(kw in text.lower() for kw in why_keywords)
            for text in h1s + h2s + paragraphs[:3]
        )
        
        # Calculate clarity score
        clarity_score = sum([
            3 if answers_what else 0,
            3 if answers_who else 0,
            4 if answers_why else 0,
        ])
        
        return {
            "score": clarity_score,
            "answers_what": answers_what,
            "answers_who": answers_who,
            "answers_why": answers_why,
        }
    
    def _analyze_ctas(self) -> Dict[str, Any]:
        """Analyze call-to-action buttons and their effectiveness."""
        ctas = self.scraped_data.get("ctas", [])
        
        has_primary_cta = len(ctas) > 0
        
        # Check for common effective CTA patterns
        cta_texts = [cta.get("text", "").lower() for cta in ctas]
        
        has_action_cta = any(
            word in text for text in cta_texts
            for word in ["get started", "try", "start", "sign up", "demo"]
        )
        
        # Check visibility (would need more context in production)
        is_visible_above_fold = has_primary_cta  # Assume visible if present
        
        # CTA count - too many can be confusing
        cta_count = len(ctas)
        
        return {
            "cta_text": ctas[0].get("text") if ctas else None,
            "is_visible_above_fold": is_visible_above_fold,
            "has_contrast": True,  # Would need color analysis
            "cta_count": cta_count,
            "primary_cta_present": has_primary_cta,
            "has_action_cta": has_action_cta,
        }
    
    def _analyze_navigation(self) -> Dict[str, Any]:
        """Analyze navigation structure and usability."""
        nav_items = self.scraped_data.get("navigation", [])
        
        item_count = len(nav_items)
        
        # Check if navigation is clear (5-7 items is ideal)
        is_clear = 3 <= item_count <= 8
        
        # Check for important links
        nav_texts = [item.get("text", "").lower() for item in nav_items]
        
        has_contact = any("contact" in text for text in nav_texts)
        has_pricing = any("pricing" in text or "price" in text for text in nav_texts)
        has_about = any("about" in text for text in nav_texts)
        has_search = self._check_for_search()
        
        # Check for legal pages
        all_links = [item.get("href", "").lower() for item in nav_items]
        html = self.scraped_data.get("html", "").lower()
        
        has_privacy = "privacy" in html
        has_terms = "terms" in html or "tos" in html
        
        return {
            "item_count": item_count,
            "is_clear": is_clear,
            "has_contact": has_contact,
            "has_pricing": has_pricing,
            "has_about": has_about,
            "has_search": has_search,
            "has_privacy": has_privacy,
            "has_terms": has_terms,
        }
    
    def _check_for_search(self) -> bool:
        """Check if the site has a search function."""
        forms = self.scraped_data.get("forms", [])
        html = self.scraped_data.get("html", "").lower()
        
        # Check for search form
        has_search_form = any(
            any("search" in str(field) for field in form.get("fields", []))
            for form in forms
        )
        
        # Check for search in HTML
        has_search_element = "search" in html and ("input" in html or "form" in html)
        
        return has_search_form or has_search_element
    
    def _analyze_trust_signals(self) -> Dict[str, Any]:
        """Analyze trust signals on the page."""
        html = self.scraped_data.get("html", "").lower()
        text = self.scraped_data.get("text_content", "").lower()
        
        # Check for testimonials
        has_testimonials = any(word in html for word in [
            "testimonial", "review", "customer said", "what our",
            '"', "quote", "rating"
        ])
        
        # Check for client logos
        has_logos = any(word in html for word in [
            "trusted by", "used by", "partners", "clients",
            "featured in", "as seen"
        ])
        
        # Check for case studies
        has_case_studies = any(word in html for word in [
            "case study", "case-study", "success story"
        ])
        
        # Check for security badges
        has_security = any(word in html for word in [
            "secure", "ssl", "encrypted", "gdpr", "compliant",
            "certified", "soc 2", "iso"
        ])
        
        # Check for social proof numbers
        import re
        number_patterns = re.findall(r'(\d+[,\.]?\d*)\s*(users|customers|downloads|companies)', text)
        has_numbers = len(number_patterns) > 0
        
        # Count total signals
        count = sum([
            has_testimonials, has_logos, has_case_studies,
            has_security, has_numbers
        ])
        
        return {
            "has_testimonials": has_testimonials,
            "has_logos": has_logos,
            "has_case_studies": has_case_studies,
            "has_security": has_security,
            "has_numbers": has_numbers,
            "count": count,
        }
    
    def _analyze_mobile_accessibility(self) -> Dict[str, Any]:
        """Analyze mobile responsiveness and accessibility."""
        html = self.scraped_data.get("html", "").lower()
        
        # Check for viewport meta tag (basic mobile support)
        has_viewport = "viewport" in html
        
        # Check for responsive CSS keywords
        has_responsive_css = any(word in html for word in [
            "@media", "responsive", "mobile", "flex", "grid"
        ])
        
        responsive = has_viewport and has_responsive_css
        
        return {
            "responsive": responsive,
            "has_viewport": has_viewport,
        }
    
    def _calculate_score(self) -> float:
        """Calculate the UX/conversion score."""
        score = 0.0
        
        # First impression (25%)
        clarity = self._raw_data.get("clarity", {})
        clarity_score = clarity.get("score", 5) * 10
        score += clarity_score * 0.25
        
        # CTA effectiveness (25%)
        cta = self._raw_data.get("cta", {})
        cta_score = 0
        if cta.get("primary_cta_present"):
            cta_score += 40
        if cta.get("has_action_cta"):
            cta_score += 30
        if cta.get("is_visible_above_fold"):
            cta_score += 30
        score += cta_score * 0.25
        
        # Navigation (20%)
        nav = self._raw_data.get("navigation", {})
        nav_score = 0
        if nav.get("is_clear"):
            nav_score += 40
        if nav.get("has_contact"):
            nav_score += 20
        if nav.get("has_pricing"):
            nav_score += 20
        if nav.get("has_privacy") and nav.get("has_terms"):
            nav_score += 20
        score += nav_score * 0.20
        
        # Trust signals (20%)
        trust = self._raw_data.get("trust", {})
        trust_count = trust.get("count", 0)
        trust_score = min(100, trust_count * 25)  # Each signal adds 25, max 100
        score += trust_score * 0.20
        
        # Mobile/accessibility (10%)
        mobile = self._raw_data.get("mobile", {})
        mobile_score = 100 if mobile.get("responsive") else 40
        score += mobile_score * 0.10
        
        return self.clamp_score(score)
    
    def _generate_findings(self) -> List[Finding]:
        """Generate findings based on the analysis."""
        findings = []
        
        # Clarity findings
        clarity = self._raw_data.get("clarity", {})
        if clarity.get("score", 0) >= 8:
            findings.append(Finding(
                title="Clear Value Proposition",
                detail="The homepage clearly communicates what the product is, who it's for, "
                       "and why visitors should care.",
                severity=SeverityLevel.INFO,
            ))
        elif clarity.get("score", 0) < 5:
            findings.append(Finding(
                title="Unclear Value Proposition",
                detail="Visitors may not quickly understand what you offer. The homepage should "
                       "immediately answer: What is it? Who is it for? Why should I care?",
                severity=SeverityLevel.HIGH,
            ))
        
        # CTA findings
        cta = self._raw_data.get("cta", {})
        if not cta.get("primary_cta_present"):
            findings.append(Finding(
                title="No Clear Call-to-Action",
                detail="No prominent CTA button found on the homepage. Visitors don't know what "
                       "action to take next, which hurts conversion.",
                severity=SeverityLevel.CRITICAL,
            ))
        elif cta.get("cta_count", 0) > 5:
            findings.append(Finding(
                title="Too Many CTAs",
                detail=f"Found {cta['cta_count']} call-to-action elements. Too many choices can "
                       "paralyze visitors (choice overload). Focus on 1-2 primary actions.",
                severity=SeverityLevel.MEDIUM,
            ))
        
        # Trust signals
        trust = self._raw_data.get("trust", {})
        if trust.get("count", 0) == 0:
            findings.append(Finding(
                title="No Trust Signals Found",
                detail="No testimonials, client logos, or social proof detected. Trust signals "
                       "are crucial for converting first-time visitors.",
                severity=SeverityLevel.HIGH,
            ))
        elif trust.get("count", 0) >= 3:
            findings.append(Finding(
                title="Good Trust Signals Present",
                detail="Multiple trust signals found including testimonials and/or client logos. "
                       "This helps build credibility with visitors.",
                severity=SeverityLevel.INFO,
            ))
        
        # Navigation findings
        nav = self._raw_data.get("navigation", {})
        if not nav.get("has_privacy") or not nav.get("has_terms"):
            findings.append(Finding(
                title="Missing Legal Pages",
                detail="Privacy policy and/or terms of service not found. These are required for "
                       "legal compliance and user trust.",
                severity=SeverityLevel.HIGH,
            ))
        
        return findings
    
    def _generate_recommendations(self) -> List[Recommendation]:
        """Generate recommendations based on findings."""
        recommendations = []
        
        # Clarity recommendations
        clarity = self._raw_data.get("clarity", {})
        if clarity.get("score", 0) < 7:
            recommendations.append(Recommendation(
                title="Improve Homepage Clarity",
                description="Restructure your homepage to clearly answer three questions in the "
                           "first 5 seconds: What do you offer? Who is it for? What's the main "
                           "benefit? Use a clear headline + subheadline format.",
                priority=SeverityLevel.HIGH,
                category="website_ux",
                impact="high",
                effort="medium",
            ))
        
        # CTA recommendations
        cta = self._raw_data.get("cta", {})
        if not cta.get("primary_cta_present"):
            recommendations.append(Recommendation(
                title="Add a Clear Primary CTA",
                description="Add a prominent call-to-action button above the fold. Use action-oriented "
                           "text like 'Get Started Free' or 'Try It Now'. Make it stand out with "
                           "a contrasting color.",
                priority=SeverityLevel.CRITICAL,
                category="website_ux",
                impact="high",
                effort="low",
            ))
        
        # Trust signal recommendations
        trust = self._raw_data.get("trust", {})
        if trust.get("count", 0) < 2:
            recommendations.append(Recommendation(
                title="Add Social Proof Elements",
                description="Include at least 2-3 trust signals: customer testimonials with photos, "
                           "client logos, user counts (e.g., 'Trusted by 10,000+ users'), or media "
                           "mentions. Social proof dramatically improves conversion rates.",
                priority=SeverityLevel.HIGH,
                category="website_ux",
                impact="high",
                effort="medium",
            ))
        
        # Navigation recommendations
        nav = self._raw_data.get("navigation", {})
        if nav.get("item_count", 0) > 8:
            recommendations.append(Recommendation(
                title="Simplify Navigation",
                description="Reduce navigation menu to 5-7 items maximum. Group related pages under "
                           "dropdown menus. Simplified navigation reduces cognitive load and helps "
                           "visitors find what they need faster.",
                priority=SeverityLevel.MEDIUM,
                category="website_ux",
                impact="medium",
                effort="low",
            ))
        
        if not nav.get("has_pricing"):
            recommendations.append(Recommendation(
                title="Make Pricing Accessible",
                description="Add a visible 'Pricing' link in the main navigation. Visitors often "
                           "want to see pricing early in their evaluation. Hiding it can cause "
                           "frustration and increased bounce rates.",
                priority=SeverityLevel.MEDIUM,
                category="website_ux",
                impact="medium",
                effort="low",
            ))
        
        return recommendations
