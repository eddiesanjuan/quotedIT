"""
Services for Quoted.
These are the core business logic components.
"""

from .transcription import TranscriptionService, get_transcription_service
from .quote_generator import QuoteGenerationService, get_quote_service
from .pdf_generator import PDFGeneratorService, get_pdf_service
from .onboarding import OnboardingService, get_onboarding_service
from .learning import LearningService, get_learning_service
from .database import DatabaseService, get_db_service
from .pricing_brain import PricingBrainService, get_pricing_brain_service
from .pricing_sanity_check import PricingSanityCheckService, get_sanity_check_service

# Alias for backward compatibility
get_database_service = get_db_service

__all__ = [
    "TranscriptionService",
    "get_transcription_service",
    "QuoteGenerationService",
    "get_quote_service",
    "PDFGeneratorService",
    "get_pdf_service",
    "OnboardingService",
    "get_onboarding_service",
    "LearningService",
    "get_learning_service",
    "DatabaseService",
    "get_db_service",
    "get_database_service",
    "PricingBrainService",
    "get_pricing_brain_service",
    "PricingSanityCheckService",
    "get_sanity_check_service",
]
