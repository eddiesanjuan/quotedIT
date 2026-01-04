"""
Google Ads Scripts Integration (DISC-141 Phase 2 - Alternative).

Instead of Google Ads API (requires approval), this uses Google Ads Scripts
which run inside the Google Ads account and push data to our webhook.

Setup:
1. Go to Google Ads → Tools & Settings → Scripts
2. Create new script, paste the provided JavaScript
3. Authorize and run on schedule (daily)

The script sends campaign data to POST /api/analytics/google-ads-webhook
which we store and use for alerts/reports.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
import json

from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from .logging import get_logger
from ..config import settings

logger = get_logger("quoted.google_ads_scripts")


# We'll store the data in a simple table
# For now, let's use a JSON file approach that doesn't require migrations


@dataclass
class CampaignSnapshot:
    """Snapshot of campaign data from Google Ads Scripts."""
    timestamp: datetime
    account_id: str
    campaign_id: str
    campaign_name: str
    status: str
    impressions: int
    clicks: int
    cost: float  # In account currency
    conversions: float
    ctr: float
    avg_cpc: float
    date: str  # YYYY-MM-DD


@dataclass
class GoogleAdsSnapshot:
    """Complete snapshot from Google Ads Scripts webhook."""
    received_at: datetime
    account_id: str
    account_name: str
    currency: str
    date_range: str
    total_impressions: int
    total_clicks: int
    total_cost: float
    total_conversions: float
    campaigns: List[CampaignSnapshot] = field(default_factory=list)

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


class GoogleAdsScriptsService:
    """Service for handling Google Ads Scripts webhook data."""

    # Store snapshots in memory for now (persists until restart)
    # In production, should use database table
    _snapshots: List[GoogleAdsSnapshot] = []

    @classmethod
    def store_snapshot(cls, data: Dict[str, Any]) -> GoogleAdsSnapshot:
        """
        Store a snapshot received from Google Ads Scripts webhook.

        Args:
            data: JSON payload from the script

        Returns:
            Parsed GoogleAdsSnapshot
        """
        try:
            campaigns = []
            for c in data.get("campaigns", []):
                campaigns.append(CampaignSnapshot(
                    timestamp=datetime.utcnow(),
                    account_id=data.get("accountId", ""),
                    campaign_id=c.get("id", ""),
                    campaign_name=c.get("name", "Unknown"),
                    status=c.get("status", "UNKNOWN"),
                    impressions=int(c.get("impressions", 0)),
                    clicks=int(c.get("clicks", 0)),
                    cost=float(c.get("cost", 0)),
                    conversions=float(c.get("conversions", 0)),
                    ctr=float(c.get("ctr", 0)),
                    avg_cpc=float(c.get("avgCpc", 0)),
                    date=c.get("date", datetime.utcnow().strftime("%Y-%m-%d"))
                ))

            snapshot = GoogleAdsSnapshot(
                received_at=datetime.utcnow(),
                account_id=data.get("accountId", ""),
                account_name=data.get("accountName", "Unknown"),
                currency=data.get("currency", "USD"),
                date_range=data.get("dateRange", "LAST_7_DAYS"),
                total_impressions=int(data.get("totalImpressions", 0)),
                total_clicks=int(data.get("totalClicks", 0)),
                total_cost=float(data.get("totalCost", 0)),
                total_conversions=float(data.get("totalConversions", 0)),
                campaigns=campaigns
            )

            # Store (keep last 30 snapshots)
            cls._snapshots.append(snapshot)
            if len(cls._snapshots) > 30:
                cls._snapshots = cls._snapshots[-30:]

            logger.info(
                f"Stored Google Ads snapshot: {snapshot.total_clicks} clicks, "
                f"${snapshot.total_cost:.2f} cost, {snapshot.total_conversions} conversions"
            )

            return snapshot

        except Exception as e:
            logger.error(f"Error parsing Google Ads webhook data: {e}")
            raise

    @classmethod
    def get_latest_snapshot(cls) -> Optional[GoogleAdsSnapshot]:
        """Get the most recent snapshot."""
        if not cls._snapshots:
            return None
        return cls._snapshots[-1]

    @classmethod
    def get_snapshots(cls, days: int = 7) -> List[GoogleAdsSnapshot]:
        """Get snapshots from the last N days."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        return [s for s in cls._snapshots if s.received_at >= cutoff]

    @classmethod
    def check_anomalies(cls) -> List[Dict[str, Any]]:
        """
        Check for concerning patterns in the latest Google Ads data.

        Returns list of anomalies.
        """
        anomalies = []
        snapshot = cls.get_latest_snapshot()

        if not snapshot:
            return anomalies

        # Check for high CPC (above $5 is concerning for quote tool)
        if snapshot.overall_cpc > 5.0:
            anomalies.append({
                "type": "high_cpc",
                "severity": "high",
                "message": f"CPC is ${snapshot.overall_cpc:.2f} - consider adjusting bid strategy",
                "value": snapshot.overall_cpc,
                "threshold": 5.0
            })

        # Check for low CTR (below 1% suggests ad copy issues)
        if snapshot.total_impressions > 100 and snapshot.overall_ctr < 1.0:
            anomalies.append({
                "type": "low_ctr",
                "severity": "high",
                "message": f"CTR is {snapshot.overall_ctr:.2f}% - ad copy may need improvement",
                "value": snapshot.overall_ctr,
                "threshold": 1.0
            })

        # Check for zero conversions with significant spend
        if snapshot.total_cost > 50 and snapshot.total_conversions == 0:
            anomalies.append({
                "type": "no_conversions",
                "severity": "critical",
                "message": f"Spent ${snapshot.total_cost:.2f} with 0 conversions - check landing page",
                "value": snapshot.total_cost,
                "conversions": 0
            })

        # Check for low impressions (budget may be exhausted or ads paused)
        if snapshot.total_impressions < 100:
            anomalies.append({
                "type": "low_impressions",
                "severity": "high",
                "message": f"Only {snapshot.total_impressions} impressions - ads may be paused or budget exhausted",
                "value": snapshot.total_impressions
            })

        return anomalies

    @classmethod
    def generate_recommendations(cls) -> List[str]:
        """Generate AI-powered recommendations based on latest data."""
        recommendations = []
        snapshot = cls.get_latest_snapshot()

        if not snapshot:
            recommendations.append(
                "📊 **No Data Yet**: Run the Google Ads Script to start receiving data."
            )
            return recommendations

        # CTR recommendations
        if snapshot.overall_ctr < 2.0:
            recommendations.append(
                "📝 **Improve Ad Copy**: Your CTR is below 2%. Try:\n"
                "  - Add numbers/stats to headlines (e.g., '5 Min Quote')\n"
                "  - Include clear value prop ('No Signup Required')\n"
                "  - Test urgency ('Try Free Today')"
            )

        # CPC recommendations
        if snapshot.overall_cpc > 3.0:
            recommendations.append(
                "💰 **Reduce CPC**: Your cost per click is ${:.2f}. Consider:\n".format(snapshot.overall_cpc) +
                "  - Switch to 'Maximize Clicks' bid strategy\n"
                "  - Add negative keywords (competitors, 'free template', 'excel')\n"
                "  - Focus on long-tail keywords"
            )

        # Conversion recommendations
        if snapshot.total_clicks > 50 and snapshot.total_conversions < 1:
            recommendations.append(
                "🎯 **Fix Conversion Path**: {:.0f} clicks but no conversions. Check:\n".format(snapshot.total_clicks) +
                "  - Landing page load speed (aim for <3s)\n"
                "  - Mobile experience (most clicks are mobile)\n"
                "  - Clear CTA above the fold\n"
                "  - Conversion tracking is working"
            )

        # Impression recommendations
        if snapshot.total_impressions < 500:
            recommendations.append(
                "📈 **Increase Visibility**: Only {:.0f} impressions. Try:\n".format(snapshot.total_impressions) +
                "  - Increase daily budget\n"
                "  - Broaden keyword match types (phrase → broad)\n"
                "  - Check ad schedule (are ads running all day?)"
            )

        if not recommendations:
            recommendations.append(
                "✅ **Looking Good**: Metrics are within healthy ranges. "
                "Keep monitoring for trends."
            )

        return recommendations


def generate_google_ads_script(webhook_url: str, webhook_secret: str) -> str:
    """
    Generate the JavaScript code for Google Ads Scripts.

    Args:
        webhook_url: Full URL to POST data to
        webhook_secret: Secret for authentication

    Returns:
        JavaScript code to paste into Google Ads Scripts
    """
    return f'''
// Quoted.it Google Ads Data Sync v2
// Paste this into Google Ads → Tools & Settings → Scripts
// Run daily to sync campaign performance data

function main() {{
  var webhook_url = "{webhook_url}";
  var webhook_secret = "{webhook_secret}";

  // Get account info
  var account = AdsApp.currentAccount();
  var accountId = account.getCustomerId();
  var accountName = account.getName();
  var currency = account.getCurrencyCode();

  Logger.log("=== Quoted.it Data Sync ===");
  Logger.log("Account ID: " + accountId);
  Logger.log("Account Name: " + accountName);

  // Get ALL campaigns (no status filter)
  var campaigns = [];
  var totalImpressions = 0;
  var totalClicks = 0;
  var totalCost = 0;
  var totalConversions = 0;
  var campaignCount = 0;

  // Helper function to process campaign stats
  function processCampaign(campaign, campaignType) {{
    var stats = campaign.getStatsFor("LAST_7_DAYS");
    var impressions = stats.getImpressions();
    var clicks = stats.getClicks();
    var cost = stats.getCost();
    var conversions = stats.getConversions();
    var ctr = impressions > 0 ? (clicks / impressions * 100) : 0;
    var avgCpc = clicks > 0 ? (cost / clicks) : 0;
    var status = campaign.isEnabled() ? "ENABLED" : "PAUSED";

    Logger.log("  [" + campaignType + "] " + campaign.getName() + " [" + status + "]");
    Logger.log("    Clicks: " + clicks + ", Impressions: " + impressions + ", Cost: $" + cost.toFixed(2));

    campaigns.push({{
      id: campaign.getId().toString(),
      name: campaign.getName(),
      type: campaignType,
      status: status,
      impressions: impressions,
      clicks: clicks,
      cost: cost,
      conversions: conversions,
      ctr: ctr.toFixed(2),
      avgCpc: avgCpc.toFixed(2)
    }});

    totalImpressions += impressions;
    totalClicks += clicks;
    totalCost += cost;
    totalConversions += conversions;
    campaignCount++;
  }}

  Logger.log("Scanning campaigns...");

  // 1. Regular campaigns (Search, Display, Video, etc.)
  var regularIterator = AdsApp.campaigns().forDateRange("LAST_7_DAYS").get();
  while (regularIterator.hasNext()) {{
    processCampaign(regularIterator.next(), "Standard");
  }}

  // 2. Performance Max campaigns (requires separate API)
  try {{
    var pmaxIterator = AdsApp.performanceMaxCampaigns().forDateRange("LAST_7_DAYS").get();
    while (pmaxIterator.hasNext()) {{
      processCampaign(pmaxIterator.next(), "Performance Max");
    }}
  }} catch (e) {{
    Logger.log("  Note: Could not access Performance Max campaigns: " + e.message);
  }}

  // 3. Shopping campaigns
  try {{
    var shoppingIterator = AdsApp.shoppingCampaigns().forDateRange("LAST_7_DAYS").get();
    while (shoppingIterator.hasNext()) {{
      processCampaign(shoppingIterator.next(), "Shopping");
    }}
  }} catch (e) {{
    // Shopping campaigns not available
  }}

  Logger.log("Found " + campaignCount + " campaign(s) total");

  // Build payload
  var payload = {{
    accountId: accountId,
    accountName: accountName,
    currency: currency,
    dateRange: "LAST_7_DAYS",
    totalImpressions: totalImpressions,
    totalClicks: totalClicks,
    totalCost: totalCost.toFixed(2),
    totalConversions: totalConversions,
    campaigns: campaigns,
    timestamp: new Date().toISOString()
  }};

  // Send to webhook
  var options = {{
    method: "POST",
    contentType: "application/json",
    headers: {{
      "X-Webhook-Secret": webhook_secret
    }},
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  }};

  try {{
    var response = UrlFetchApp.fetch(webhook_url, options);
    var responseCode = response.getResponseCode();

    if (responseCode === 200) {{
      Logger.log("✅ Data synced to Quoted!");
      Logger.log("Summary: " + totalClicks + " clicks, " + totalImpressions + " impressions, $" + totalCost.toFixed(2) + " cost");
    }} else {{
      Logger.log("❌ Webhook returned: " + responseCode);
      Logger.log(response.getContentText());
    }}
  }} catch (e) {{
    Logger.log("❌ Error sending data: " + e.message);
  }}
}}
'''
