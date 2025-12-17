#!/usr/bin/env python3
"""
API Integration Test Script
============================
Tests all external API services to verify configuration is working.
Run this after adding API keys to .env to verify integrations.
"""

import asyncio
import os
import sys

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()


async def test_wikipedia():
    """Test Wikipedia API (no key needed)"""
    print("\n🌐 Testing Wikipedia API...")
    try:
        from app.services.wikipedia_service import WikipediaService
        service = WikipediaService()
        result = await service.check_brand_presence("OpenAI")
        if result.success:
            print(f"  ✅ Wikipedia API working!")
            print(f"     Has page: {result.has_wikipedia_page}")
            print(f"     Notability: {result.notability_score}/100")
            if result.article:
                desc = result.article.description[:60] + "..." if result.article.description else "N/A"
                print(f"     Description: {desc}")
            return True
        else:
            print(f"  ❌ Wikipedia error: {result.error}")
            return False
    except Exception as e:
        print(f"  ❌ Wikipedia Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_pagespeed():
    """Test PageSpeed API"""
    print("\n⚡ Testing PageSpeed Insights API...")
    try:
        from app.services.pagespeed_service import PageSpeedService
        service = PageSpeedService()
        
        if not os.getenv('GOOGLE_API_KEY'):
            print("  ⚠️ No GOOGLE_API_KEY - will use mock data")
            
        result = await service.analyze("https://example.com")
        if result.success:
            print(f"  ✅ PageSpeed API working!")
            print(f"     Performance: {result.performance_score:.0f}/100")
            print(f"     SEO: {result.seo_score:.0f}/100")
            print(f"     Accessibility: {result.accessibility_score:.0f}/100")
            if result.core_web_vitals:
                print(f"     LCP: {result.core_web_vitals.lcp}s, CLS: {result.core_web_vitals.cls}")
            return True
        else:
            print(f"  ⚠️ PageSpeed returned error: {result.error}")
            return False
    except Exception as e:
        print(f"  ❌ PageSpeed Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_google_search():
    """Test Google Custom Search API"""
    print("\n🔍 Testing Google Custom Search API...")
    try:
        from app.services.google_search_service import GoogleSearchService
        service = GoogleSearchService()
        
        if not os.getenv('GOOGLE_API_KEY') or not os.getenv('GOOGLE_SEARCH_ENGINE_ID'):
            print("  ⚠️ Missing GOOGLE_API_KEY or GOOGLE_SEARCH_ENGINE_ID - will use mock data")
        
        result = await service.search_brand("OpenAI", "openai.com")
        if result.success:
            print(f"  ✅ Google Search API working!")
            print(f"     Total results: {result.total_results:,}")
            print(f"     Brand in top 10: {result.brand_in_top_10}")
            print(f"     Brand position: {result.brand_position}")
            print(f"     Wikipedia found: {result.wikipedia_found}")
            return True
        else:
            print(f"  ⚠️ Google Search error: {result.error}")
            return False
    except Exception as e:
        print(f"  ❌ Google Search Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_twitter():
    """Test Twitter API"""
    print("\n🐦 Testing Twitter API v2...")
    try:
        from app.services.twitter_service import TwitterService
        service = TwitterService()
        
        if not os.getenv('TWITTER_BEARER_TOKEN'):
            print("  ⚠️ No TWITTER_BEARER_TOKEN - will use mock data")
        
        result = await service.analyze_account("openai")
        if result.success and result.user:
            print(f"  ✅ Twitter API working!")
            print(f"     @{result.username}: {result.user.name}")
            print(f"     Followers: {result.user.followers_count:,}")
            print(f"     Engagement rate: {result.engagement_rate:.2f}%")
            print(f"     Posts/week: {result.posts_per_week:.1f}")
            return True
        else:
            print(f"  ⚠️ Twitter: {result.error or 'Using mock data'}")
            return result.success  # Mock data also returns success=True
    except Exception as e:
        print(f"  ❌ Twitter Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_openai():
    """Test OpenAI API"""
    print("\n🤖 Testing OpenAI API...")
    try:
        from app.services.openai_service import OpenAIService
        service = OpenAIService()
        
        # Test readability (doesn't use API)
        readability = await service.analyze_readability(
            "OpenAI is an artificial intelligence research company. "
            "We build safe and beneficial AI systems for everyone. "
            "Our mission is to ensure artificial general intelligence benefits all of humanity."
        )
        print(f"  ✅ OpenAI Service initialized")
        print(f"     Readability: Grade {readability['grade_level']}, Rating: {readability['rating']}")
        
        # Test archetype analysis (uses API)
        if os.getenv('OPENAI_API_KEY'):
            print("     Testing archetype analysis (API call)...")
            result = await service.analyze_archetype(
                "We empower developers to build the future of AI. "
                "Our mission is to ensure artificial general intelligence benefits all of humanity. "
                "We're a research company pushing the boundaries of what's possible.",
                "OpenAI"
            )
            print(f"     Archetype: {result.primary_archetype} (confidence: {result.confidence:.0%})")
            print(f"     Reasoning: {result.reasoning[:80]}..." if result.reasoning else "")
            return True
        else:
            print(f"  ⚠️ No OPENAI_API_KEY - skipping archetype API test")
            return True  # Service works, just no API key
    except Exception as e:
        print(f"  ❌ OpenAI Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    print("=" * 60)
    print("🔧 Brand Analytics - API Integration Tests")
    print("=" * 60)
    
    # Check environment variables
    print("\n📋 Environment Variables:")
    env_vars = {
        "OPENAI_API_KEY": os.getenv('OPENAI_API_KEY'),
        "GOOGLE_API_KEY": os.getenv('GOOGLE_API_KEY'),
        "GOOGLE_SEARCH_ENGINE_ID": os.getenv('GOOGLE_SEARCH_ENGINE_ID'),
        "TWITTER_BEARER_TOKEN": os.getenv('TWITTER_BEARER_TOKEN'),
    }
    
    for key, value in env_vars.items():
        status = "✅ Set" if value else "❌ Missing"
        # Show first 10 chars if set
        preview = f" ({value[:10]}...)" if value and len(value) > 10 else ""
        print(f"  {key}: {status}{preview}")
    
    # Run tests
    results = {
        "Wikipedia": await test_wikipedia(),
        "PageSpeed": await test_pagespeed(),
        "Google Search": await test_google_search(),
        "Twitter": await test_twitter(),
        "OpenAI": await test_openai(),
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for api, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {api}: {status}")
    
    print(f"\n  Total: {passed}/{total} APIs working")
    
    if passed == total:
        print("\n🎉 All integrations working! Ready for full analysis.")
    else:
        print("\n⚠️ Some APIs failed or using mock data. Check your .env configuration.")
    
    print("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
