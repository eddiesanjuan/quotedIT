"""
Google Ads Analytics Service (DISC-141 Phase 2).

Integrates with Google Ads API to provide:
- Campaign performance metrics (clicks, impressions, cost, conversions)
- Spend tracking and ROI calculation
- AI-powered recommendations for optimization
- Anomaly detection for ad performance

Setup Required:
1. Google Ads Developer Token (apply at developers.google.com/google-ads/api)
2. OAuth2 credentials (Google Cloud Console)
3. Google Ads Customer ID (your account ID without dashes)

Environment Variables:
- GOOGLE_ADS_DEVELOPER_TOKEN: Your developer token
- GOOGLE_ADS_CLIENT_ID: OAuth client ID
- GOOGLE_ADS_CLIENT_SECRET: OAuth client secret
- GOOGLE_ADS_REFRESH_TOKEN: OAuth refresh token (after auth flow)
- GOOGLE_ADS_CUSTOMER_ID: Your Google Ads account ID (no dashes)

Cost: Minimal (API calls are free, just compute)
"""

import httpx
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from .logging import get_logger
from ..config import settings

logger = get_logger("quoted.google_ads_analytics")


@dataclass
class CampaignMetrics:
    """Metrics for a single campaign."""
    campaign_id: str
    campaign_name: str
    status: str
    impressions: int
    clicks: int
    cost_micros: int  # Cost in micro-units (divide by 1,000,000 for dollars)
    conversions: float
    date: datetime

    @property
    def cost(self) -> float:
        """Cost in dollars."""
        return self.cost_micros / 1_000_000

    @property
    def ctr(self) -> float:
        """Click-through rate as percentage."""
        if self.impressions == 0:
            return 0.0
        return (self.clicks / self.impressions) * 100

    @property
    def cpc(self) -> float:
        """Cost per click in dollars."""
        if self.clicks == 0:
            return 0.0
        return self.cost / self.clicks

    @property
    def cpa(self) -> float:
        """Cost per acquisition in dollars."""
        if self.conversions == 0:
            return float('inf')
        return self.cost / self.conversions


@dataclass
class AccountMetrics:
    """Aggregate metrics for the entire account."""
    date_range_start: datetime
    date_range_end: datetime
    total_impressions: int
    total_clicks: int
    total_cost: float
    total_conversions: float
    campaigns: List[CampaignMetrics]

    @property
    def overall_ctr(self) -> float:
        if self.total_impressions == 0:
            return 0.0
        return (self.total_clicks / self.total_impressions) * 100

    @property
    def overall_cpc(self) -> float:
        if self.total_clicks == 0:
            return 0.0
        return self.total_cost / self.total_clicks

    @property
    def overall_cpa(self) -> float:
        if self.total_conversions == 0:
            return float('inf')
        return self.total_cost / self.total_conversions


class GoogleAdsAnalyticsService:
    """Service for Google Ads performance tracking and optimization."""

    @staticmethod
    def _is_configured() -> bool:
        """Check if Google Ads API is configured."""
        return all([
            getattr(settings, 'google_ads_developer_token', None),
            getattr(settings, 'google_ads_client_id', None),
            getattr(settings, 'google_ads_client_secret', None),
            getattr(settings, 'google_ads_refresh_token', None),
            getattr(settings, 'google_ads_customer_id', None),
        ])

    @staticmethod
    async def _get_access_token() -> Optional[str]:
        """
        Get OAuth2 access token using refresh token.

        Returns:
            Access token string or None if failed
        """
        if not GoogleAdsAnalyticsService._is_configured():
            logger.debug("Google Ads API not configured")
            return None

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://oauth2.googleapis.com/token",
                    data={
                        "client_id": settings.google_ads_client_id,
                        "client_secret": settings.google_ads_client_secret,
                        "refresh_token": settings.google_ads_refresh_token,
                        "grant_type": "refresh_token",
                    }
                )

                if response.status_code == 200:
                    return response.json().get("access_token")
                else:
                    logger.error(f"Failed to refresh Google Ads token: {response.text}")
                    return None

        except Exception as e:
            logger.error(f"Error getting Google Ads access token: {e}")
            return None

    @staticmethod
    async def get_campaign_metrics(
        days: int = 7
    ) -> Optional[AccountMetrics]:
        """
        Get campaign performance metrics for the specified period.

        Args:
            days: Number of days to analyze (default: 7)

        Returns:
            AccountMetrics with campaign data, or None if API not configured
        """
        if not GoogleAdsAnalyticsService._is_configured():
            logger.info("Google Ads API not configured - skipping metrics fetch")
            return None

        access_token = await GoogleAdsAnalyticsService._get_access_token()
        if not access_token:
            return None

        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Google Ads API query
        query = f"""
            SELECT
                campaign.id,
                campaign.name,
                campaign.status,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.conversions,
                segments.date
            FROM campaign
            WHERE segments.date BETWEEN '{start_date.strftime('%Y-%m-%d')}'
                AND '{end_date.strftime('%Y-%m-%d')}'
            ORDER BY metrics.impressions DESC
        """

        try:
            customer_id = settings.google_ads_customer_id.replace("-", "")
            url = f"https://googleads.googleapis.com/v15/customers/{customer_id}/googleAds:search"

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "developer-token": settings.google_ads_developer_token,
                        "Content-Type": "application/json",
                    },
                    json={"query": query}
                )

                if response.status_code != 200:
                    logger.error(f"Google Ads API error: {response.status_code} - {response.text}")
                    return None

                data = response.json()
                campaigns = []

                for row in data.get("results", []):
                    campaign = row.get("campaign", {})
                    metrics = row.get("metrics", {})
                    segment = row.get("segments", {})

                    campaigns.append(CampaignMetrics(
                        campaign_id=campaign.get("id", ""),
                        campaign_name=campaign.get("name", "Unknown"),
                        status=campaign.get("status", "UNKNOWN"),
                        impressions=int(metrics.get("impressions", 0)),
                        clicks=int(metrics.get("clicks", 0)),
                        cost_micros=int(metrics.get("costMicros", 0)),
                        conversions=float(metrics.get("conversions", 0)),
                        date=datetime.strptime(segment.get("date", start_date.strftime('%Y-%m-%d')), '%Y-%m-%d')
                    ))

                # Aggregate totals
                return AccountMetrics(
                    date_range_start=start_date,
                    date_range_end=end_date,
                    total_impressions=sum(c.impressions for c in campaigns),
                    total_clicks=sum(c.clicks for c in campaigns),
                    total_cost=sum(c.cost for c in campaigns),
                    total_conversions=sum(c.conversions for c in campaigns),
                    campaigns=campaigns
                )

        except Exception as e:
            logger.error(f"Error fetching Google Ads metrics: {e}")
            return None

    @staticmethod
    async def check_ads_anomalies(
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Check for concerning patterns in Google Ads performance.

        Returns list of anomalies that need attention.
        """
        anomalies = []

        metrics = await GoogleAdsAnalyticsService.get_campaign_metrics(days)
        if not metrics:
            return anomalies

        # Check for high CPC (above $5 for a quote generation tool is concerning)
        if metrics.overall_cpc > 5.0:
            anomalies.append({
                "type": "high_cpc",
                "severity": "high",
                "message": f"CPC is ${metrics.overall_cpc:.2f} - consider adjusting bid strategy",
                "value": metrics.overall_cpc,
                "threshold": 5.0
            })

        # Check for low CTR (below 1% suggests ad copy issues)
        if metrics.total_impressions > 100 and metrics.overall_ctr < 1.0:
            anomalies.append({
                "type": "low_ctr",
                "severity": "high",
                "message": f"CTR is {metrics.overall_ctr:.2f}% - ad copy may need improvement",
                "value": metrics.overall_ctr,
                "threshold": 1.0
            })

        # Check for zero conversions with spend
        if metrics.total_cost > 50 and metrics.total_conversions == 0:
            anomalies.append({
                "type": "no_conversions",
                "severity": "critical",
                "message": f"Spent ${metrics.total_cost:.2f} with 0 conversions - check landing page and targeting",
                "value": metrics.total_cost,
                "conversions": 0
            })

        # Check for paused campaigns that should be running
        paused_campaigns = [c for c in metrics.campaigns if c.status == "PAUSED"]
        if paused_campaigns:
            anomalies.append({
                "type": "paused_campaigns",
                "severity": "info",
                "message": f"{len(paused_campaigns)} campaign(s) are paused",
                "campaigns": [c.campaign_name for c in paused_campaigns]
            })

        return anomalies

    @staticmethod
    def generate_recommendations(metrics: AccountMetrics) -> List[str]:
        """
        Generate AI-powered optimization recommendations.

        Args:
            metrics: Current account metrics

        Returns:
            List of actionable recommendations
        """
        recommendations = []

        # CTR recommendations
        if metrics.overall_ctr < 2.0:
            recommendations.append(
                "📝 **Improve Ad Copy**: Your CTR is below 2%. Try:\n"
                "  - Add numbers/stats to headlines\n"
                "  - Include a clear value proposition\n"
                "  - Test 'Free' or 'No Signup' messaging"
            )

        # CPC recommendations
        if metrics.overall_cpc > 3.0:
            recommendations.append(
                "💰 **Reduce CPC**: Your cost per click is high. Consider:\n"
                "  - Switch to 'Maximize Clicks' bid strategy\n"
                "  - Add negative keywords to filter irrelevant searches\n"
                "  - Focus on long-tail keywords with less competition"
            )

        # Conversion recommendations
        if metrics.total_clicks > 50 and metrics.total_conversions < 1:
            recommendations.append(
                "🎯 **Fix Conversion Path**: Clicks aren't converting. Check:\n"
                "  - Landing page load speed (try PageSpeed Insights)\n"
                "  - Mobile experience (most clicks are mobile)\n"
                "  - Clear CTA above the fold\n"
                "  - Conversion tracking is working"
            )

        # Budget recommendations
        if metrics.total_impressions < 1000:
            recommendations.append(
                "📈 **Increase Visibility**: Low impression volume. Try:\n"
                "  - Increase daily budget\n"
                "  - Broaden keyword match types\n"
                "  - Expand geographic targeting"
            )

        return recommendations


# Convenience function for reports
async def get_google_ads_summary() -> Dict[str, Any]:
    """
    Get a summary of Google Ads performance for reports.

    Returns dict with metrics, anomalies, and recommendations.
    """
    result = {
        "configured": GoogleAdsAnalyticsService._is_configured(),
        "metrics": None,
        "anomalies": [],
        "recommendations": []
    }

    if not result["configured"]:
        result["message"] = "Google Ads API not configured. Add credentials to enable."
        return result

    metrics = await GoogleAdsAnalyticsService.get_campaign_metrics(days=7)
    if metrics:
        result["metrics"] = {
            "impressions": metrics.total_impressions,
            "clicks": metrics.total_clicks,
            "cost": round(metrics.total_cost, 2),
            "conversions": metrics.total_conversions,
            "ctr": round(metrics.overall_ctr, 2),
            "cpc": round(metrics.overall_cpc, 2),
            "cpa": round(metrics.overall_cpa, 2) if metrics.overall_cpa != float('inf') else None
        }
        result["anomalies"] = await GoogleAdsAnalyticsService.check_ads_anomalies()
        result["recommendations"] = GoogleAdsAnalyticsService.generate_recommendations(metrics)

    return result
