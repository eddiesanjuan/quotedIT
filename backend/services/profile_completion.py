"""
Profile completion service for Quoted.

Determines when Quick Setup users should be prompted to complete
their full profile via the interview process.
"""

from typing import Optional, Dict
from datetime import datetime


class ProfileCompletionService:
    """
    Service to determine when to prompt Quick Setup users to complete their profile.

    Logic:
    - Only prompt Quick Setup users (setup_type: "quick")
    - Wait until they've demonstrated system competency
    - Don't over-prompt (respect dismissals)
    """

    def should_prompt_completion(
        self,
        pricing_model: Optional[Dict],
        quote_count: int,
        correction_count: int,
        dismissed_at: Optional[datetime] = None,
    ) -> bool:
        """
        Determine if we should prompt user to complete their profile.

        Args:
            pricing_model: User's pricing model (dict from DB)
            quote_count: Total quotes generated
            correction_count: Number of quotes corrected
            dismissed_at: When user last dismissed the prompt (if ever)

        Returns:
            True if we should show the prompt
        """
        # Only prompt Quick Setup users
        if not pricing_model or pricing_model.get("setup_type") != "quick":
            return False

        # Don't prompt if user recently dismissed
        if dismissed_at:
            days_since_dismissal = (datetime.utcnow() - dismissed_at).days
            if days_since_dismissal < 14:  # Wait 2 weeks before asking again
                return False

        # Trigger conditions:
        # - At least 5 quotes generated (shows engagement)
        # - At least 2 corrections made (shows they're refining)
        # - OR 10+ quotes with any corrections (power user, needs more precision)

        if quote_count >= 10 and correction_count >= 1:
            # Power user - definitely prompt
            return True

        if quote_count >= 5 and correction_count >= 2:
            # Engaged user - ready to level up
            return True

        return False

    def get_completion_prompt(
        self,
        contractor_name: str,
        quote_count: int,
        correction_count: int,
    ) -> Dict:
        """
        Generate the completion prompt message and metadata.

        Args:
            contractor_name: Business name
            quote_count: Total quotes
            correction_count: Total corrections

        Returns:
            Dict with prompt message, title, and CTA
        """
        # Tailor message based on usage
        if quote_count >= 10:
            message = f"""You've generated {quote_count} quotes with Quoted - you're crushing it!

Want even more accurate pricing? Complete your profile with a 5-minute interview
to teach the system your unique pricing patterns.

**What you'll get:**
- Fewer corrections needed on quotes
- Better category detection
- Custom pricing rules that match your workflow
- More professional initial quotes"""

        else:
            message = f"""You're getting the hang of Quoted! ({quote_count} quotes, {correction_count} corrections)

Ready to unlock more accurate pricing? Complete your profile with a quick interview
to help the system understand your unique approach.

**What you'll get:**
- More nuanced initial quotes
- Better pricing for complex jobs
- Custom terms and conditions
- Fewer manual adjustments needed"""

        return {
            "title": "Complete Your Profile",
            "message": message.strip(),
            "cta_primary": "Start Interview (5 min)",
            "cta_secondary": "Maybe Later",
            "quote_count": quote_count,
            "correction_count": correction_count,
        }

    def get_completion_benefits(self) -> Dict:
        """
        Get detailed benefits of completing profile.
        Used for the full completion page.

        Returns:
            Dict with categories of benefits
        """
        return {
            "accuracy": {
                "title": "More Accurate Quotes",
                "benefits": [
                    "Initial quotes closer to your actual pricing",
                    "Fewer manual corrections needed",
                    "Better handling of complex jobs",
                    "Nuanced pricing rules captured"
                ]
            },
            "efficiency": {
                "title": "Faster Quote Generation",
                "benefits": [
                    "Less time adjusting line items",
                    "Better category detection",
                    "Custom templates for common jobs",
                    "Smart defaults based on your style"
                ]
            },
            "professionalism": {
                "title": "More Professional Output",
                "benefits": [
                    "Custom terms and conditions",
                    "Your warranty language",
                    "Industry-specific line items",
                    "Branded quote language"
                ]
            },
            "learning": {
                "title": "Better System Learning",
                "benefits": [
                    "Richer baseline for AI to learn from",
                    "More context for corrections",
                    "Pattern recognition across job types",
                    "Faster improvement over time"
                ]
            }
        }

    def mark_interview_completed(
        self,
        pricing_model: Dict,
    ) -> Dict:
        """
        Update pricing_model to mark interview as completed.

        This is called when a Quick Setup user completes the interview.

        Args:
            pricing_model: Existing pricing model

        Returns:
            Updated pricing_model with interview marker
        """
        # Update setup_type from "quick" to "interview"
        pricing_model["setup_type"] = "interview"
        pricing_model["interview_completed_at"] = datetime.utcnow().isoformat()

        # Add metadata about the upgrade
        if "profile_history" not in pricing_model:
            pricing_model["profile_history"] = []

        pricing_model["profile_history"].append({
            "event": "interview_completed",
            "timestamp": datetime.utcnow().isoformat(),
            "previous_setup_type": "quick",
            "notes": "User completed interview after using Quick Setup"
        })

        return pricing_model


# Singleton pattern
_profile_completion_service: Optional[ProfileCompletionService] = None


def get_profile_completion_service() -> ProfileCompletionService:
    """Get the profile completion service singleton."""
    global _profile_completion_service
    if _profile_completion_service is None:
        _profile_completion_service = ProfileCompletionService()
    return _profile_completion_service
