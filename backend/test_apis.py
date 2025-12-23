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
from pathlib import Path

# Force load from .env in current directory
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)


async def test_wikipedia():
    """Test Wikipedia API (no key needed)"""
    print("\n🌐 Testing Wikipedia API...")
    try:
        from app.services.wikipedia_service import WikipediaService

        service = WikipediaService()
        result = await service.check_brand_presence("OpenAI")
        if result.success:
            print("  ✅ Wikipedia API working!")
            print(f"     Has page: {result.has_wikipedia_page}")
            print(f"     Notability: {result.notability_score}/100")
            return True
        else:
            print(f"  ❌ Wikipedia error: {result.error}")
            return False
    except Exception as e:
        print(f"  ❌ Wikipedia Error: {e}")
        return False


async def test_pagespeed():
    """Test PageSpeed API"""
    print("\n⚡ Testing PageSpeed Insights API...")
    try:
        from app.services.pagespeed_service import PageSpeedService

        service = PageSpeedService()

        if not os.getenv("GOOGLE_API_KEY"):
            print("  ⚠️ No GOOGLE_API_KEY - will use mock data")

        result = await service.analyze("https://example.com")
        if result.success:
            print("  ✅ PageSpeed API working!")
            print(f"     Performance: {result.performance_score:.0f}/100")
            print(f"     SEO: {result.seo_score:.0f}/100")
            return True
        else:
            print(f"  ⚠️ PageSpeed returned error: {result.error}")
            return False
    except Exception as e:
        print(f"  ❌ PageSpeed Error: {e}")
        return False


async def test_google_search():
    """Test Google Custom Search API"""
    print("\n🔍 Testing Google Custom Search API...")
    try:
        from app.services.google_search_service import GoogleSearchService

        service = GoogleSearchService()

        if not os.getenv("GOOGLE_API_KEY"):
            print("  ⚠️ No GOOGLE_API_KEY - will use mock data")

        result = await service.search_brand("OpenAI", "openai.com")
        if result.success:
            print("  ✅ Google Search API working!")
            print(f"     Total results: {result.total_results:,}")
            return True
        else:
            print(f"  ⚠️ Google Search error: {result.error}")
            return False
    except Exception as e:
        print(f"  ❌ Google Search Error: {e}")
        return False


async def test_twitter():
    """Test Twitter API"""
    print("\n🐦 Testing Twitter API v2...")
    try:
        from app.services.twitter_service import TwitterService

        service = TwitterService()

        if not os.getenv("TWITTER_BEARER_TOKEN"):
            print("  ⚠️ No TWITTER_BEARER_TOKEN - will use mock data")

        result = await service.analyze_account("openai")
        if result.success and result.user:
            print("  ✅ Twitter API working!")
            print(f"     @{result.username}: {result.user.name}")
            print(f"     Followers: {result.user.followers_count:,}")
            return True
        else:
            print(f"  ⚠️ Twitter: {result.error or 'Using mock data'}")
            return result.success
    except Exception as e:
        print(f"  ❌ Twitter Error: {e}")
        return False


async def test_apify():
    """Test Apify Service (Instagram, YouTube, Reddit)"""
    print("\n🕷️ Testing Apify Service...")
    try:
        from app.services.apify_service import ApifyService

        service = ApifyService()
        if not service.is_configured():
            print("  ⚠️ Apify API not configured - skipping")
            return True

        # Test Instagram Scrape
        print("  📸 Testing Instagram scrape (@openai)...")
        insta_result = await service.scrape_instagram_profile("openai")
        if insta_result.success:
            print(
                f"     ✅ Instagram: Found {insta_result.username}, {insta_result.followers_count:,} followers"
            )
        else:
            print(f"     ❌ Instagram failed: {insta_result.error}")

        # Test YouTube Scrape
        print("  📹 Testing YouTube scrape (@openai)...")
        yt_result = await service.scrape_youtube_channel("@openai")
        if yt_result.success:
            print(
                f"     ✅ YouTube: Found {yt_result.channel_name}, {yt_result.subscribers_count:,} subscribers"
            )
        else:
            print(f"     ❌ YouTube failed: {yt_result.error}")

        return insta_result.success or yt_result.success

    except Exception as e:
        print(f"  ❌ Apify Error: {e}")
        return False


async def test_firecrawl():
    """Test Firecrawl Service"""
    print("\n🔥 Testing Firecrawl Service...")
    try:
        from app.services.firecrawl_service import FirecrawlService

        service = FirecrawlService()
        if not service.is_configured:
            print("  ⚠️ Firecrawl API not configured - skipping")
            return True

        result = await service.scrape_url("https://example.com")
        if result:
            print("  ✅ Firecrawl working!")
            print(f"     HTML length: {len(result.get('html', ''))}")
            return True
        else:
            print("  ❌ Firecrawl failed to scrape")
            return False

    except Exception as e:
        print(f"  ❌ Firecrawl Error: {e}")
        return False


async def test_perplexity():
    """Test Perplexity Service"""
    print("\n🧠 Testing Perplexity Service...")
    try:
        from app.services.perplexity_service import PerplexityService

        service = PerplexityService()
        if not service.is_configured():
            print("  ⚠️ Perplexity API not configured - skipping")
            return True

        result = await service.research_brand("openai.com", "OpenAI")
        if result.success:
            print("  ✅ Perplexity working!")
            print(f"     Company: {result.company_name}")
            print(f"     Social Profiles: {len(result.social_profiles)}")
            return True
        else:
            print(f"  ❌ Perplexity failed: {result.error}")
            return False

    except Exception as e:
        print(f"  ❌ Perplexity Error: {e}")
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
        )
        print("  ✅ OpenAI Service initialized")

        # Test archetype analysis (uses API)
        if os.getenv("OPENAI_API_KEY"):
            print("     Testing archetype analysis (API call)...")
            result = await service.analyze_archetype(
                "We empower developers to build the future of AI.",
                "OpenAI",
            )
            print(
                f"     Archetype: {result.primary_archetype} (confidence: {result.confidence:.0%})"
            )
            return True
        else:
            print("  ⚠️ No OPENAI_API_KEY - skipping archetype API test")
            return True
    except Exception as e:
        print(f"  ❌ OpenAI Error: {e}")
        return False


async def main():
    print("=" * 60)
    print("🔧 Brand Analytics - API Integration Tests")
    print("=" * 60)

    # Check environment variables
    print("\n📋 Environment Variables:")
    env_vars = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
        "TWITTER_BEARER_TOKEN": os.getenv("TWITTER_BEARER_TOKEN"),
        "APIFY_API_TOKEN": os.getenv("APIFY_API_TOKEN"),
        "FIRECRAWL_API_KEY": os.getenv("FIRECRAWL_API_KEY"),
        "PERPLEXITY_API_KEY": os.getenv("PERPLEXITY_API_KEY"),
        "MOZ_API_KEY": os.getenv("MOZ_API_KEY"),
    }

    for key, value in env_vars.items():
        status = "✅ Set" if value else "❌ Missing"
        preview = f" ({value[:10]}...)" if value and len(value) > 10 else ""
        print(f"  {key}: {status}{preview}")

    # Run tests
    results = {
        "Wikipedia": await test_wikipedia(),
        "PageSpeed": await test_pagespeed(),
        "Google Search": await test_google_search(),
        "Twitter": await test_twitter(),
        "Apify": await test_apify(),
        "Firecrawl": await test_firecrawl(),
        "Perplexity": await test_perplexity(),
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
