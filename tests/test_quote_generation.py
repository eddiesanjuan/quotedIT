"""
End-to-end tests for Quoted quote generation.
Tests the full pipeline with sample job descriptions.
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services import get_quote_service, get_pdf_service, get_learning_service


# Sample job descriptions to test
SAMPLE_JOB_DESCRIPTIONS = [
    {
        "name": "Simple Composite Deck",
        "transcription": """
        Okay so this is a 16 by 20 composite deck, Trex Select in Pebble Grey.
        No demo needed, we're building on new construction.
        Standard aluminum railing, about 45 linear feet.
        Four steps down to grade. Customer is Mike Johnson at 123 Oak Street.
        Should be about a 5 day job with two guys.
        """,
    },
    {
        "name": "Deck with Demo",
        "transcription": """
        This one's a tear off and replace. Existing deck is about 300 square feet,
        pretty rotted out. Customer wants TimberTech composite, the Azek line.
        New deck will be 18 by 18, so 324 square feet.
        Cable railing, looks like 50 linear feet.
        No stairs needed. Customer is Susan at 456 Maple Drive.
        Demo should take a day, then 4-5 days for the build.
        """,
    },
    {
        "name": "Large Multi-Level Deck",
        "transcription": """
        Big one here. Two level deck, upper level is 20 by 24, lower level is 12 by 16.
        That's 480 plus 192, call it 672 square feet total.
        Trex Transcend in Spiced Rum. Premium stuff.
        Composite railing on both levels, probably 90 linear feet total.
        Two sets of stairs, 5 steps each from upper to lower, then 4 steps to grade.
        Need to demo the old pressure treated deck, similar size.
        Customer is Robert Chen, 789 Pine Avenue.
        This is probably a 10 day job with a three man crew.
        """,
    },
    {
        "name": "Small Repair Job",
        "transcription": """
        Quick repair job. Customer has some loose deck boards, about 8 boards need replacing.
        Also the bottom step is rotted, need to replace that.
        It's a pressure treated deck. Should only take half a day.
        Customer is Janet at 222 Birch Lane.
        """,
    },
    {
        "name": "Wood Deck Build",
        "transcription": """
        Customer wants a cedar deck, 14 by 18, that's 252 square feet.
        Wood railing with metal balusters, about 35 linear feet.
        Three steps down to the patio.
        No demo, new construction attached to the house.
        Customer is Tom Williams at 555 Elm Street.
        Probably 4 days with two of us.
        """,
    },
]


# Demo contractor and pricing model
DEMO_CONTRACTOR = {
    "id": "demo-contractor",
    "business_name": "Mike's Deck Pros",
    "owner_name": "Mike Johnson",
    "email": "mike@deckpros.com",
    "phone": "(555) 123-4567",
    "address": "123 Main St, Anytown, USA",
    "primary_trade": "deck_builder",
}

DEMO_PRICING_MODEL = {
    "labor_rate_hourly": 75.0,
    "helper_rate_hourly": 45.0,
    "material_markup_percent": 20.0,
    "minimum_job_amount": 1500.0,
    "pricing_knowledge": {
        "composite_deck": {
            "base_per_sqft": 58.0,
            "typical_range": [48.0, 75.0],
            "unit": "sqft",
            "notes": "Trex Select baseline",
            "confidence": 0.85,
            "samples": 23,
        },
        "wood_deck": {
            "base_per_sqft": 42.0,
            "typical_range": [35.0, 55.0],
            "unit": "sqft",
        },
        "railing": {
            "per_linear_foot": 38.0,
            "unit": "linear_ft",
            "cable_rail_multiplier": 1.8,
        },
        "demolition": {
            "base_rate": 900.0,
            "per_sqft_adder": 2.5,
            "notes": "Add 50% for second story",
        },
        "stairs": {
            "per_step": 175.0,
            "landing_flat": 400.0,
        },
    },
    "pricing_notes": "Add 10% for difficult access. 5% discount for repeat customers. "
                     "TimberTech Azek is premium, add 15% to base composite rate. "
                     "Trex Transcend add 10%.",
}

DEMO_TERMS = {
    "deposit_percent": 50.0,
    "quote_valid_days": 30,
    "labor_warranty_years": 2,
    "accepted_payment_methods": ["check", "credit_card", "Zelle"],
}


async def test_quote_generation():
    """Test quote generation with sample job descriptions."""
    print("=" * 60)
    print("QUOTED - End-to-End Quote Generation Test")
    print("=" * 60)
    print()

    quote_service = get_quote_service()
    pdf_service = get_pdf_service()

    results = []

    for sample in SAMPLE_JOB_DESCRIPTIONS:
        print(f"Testing: {sample['name']}")
        print("-" * 40)

        try:
            # Generate quote
            quote = await quote_service.generate_quote(
                transcription=sample["transcription"],
                contractor=DEMO_CONTRACTOR,
                pricing_model=DEMO_PRICING_MODEL,
                terms=DEMO_TERMS,
            )

            # Display results
            print(f"Job Type: {quote.get('job_type', 'Unknown')}")
            print(f"Description: {quote.get('job_description', 'N/A')[:100]}...")
            print(f"Confidence: {quote.get('confidence', 'N/A')}")
            print()
            print("Line Items:")
            for item in quote.get("line_items", []):
                print(f"  - {item.get('name')}: ${item.get('amount', 0):,.2f}")
            print()
            print(f"TOTAL: ${quote.get('subtotal', 0):,.2f}")
            print(f"Timeline: {quote.get('estimated_days', 'N/A')} days")
            print()

            if quote.get("questions"):
                print("Questions for contractor:")
                for q in quote.get("questions", [])[:3]:
                    print(f"  ? {q}")
                print()

            results.append({
                "name": sample["name"],
                "success": True,
                "total": quote.get("subtotal", 0),
                "confidence": quote.get("confidence"),
            })

            # Generate PDF
            pdf_path = f"./data/pdfs/test_{sample['name'].lower().replace(' ', '_')}.pdf"
            os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
            pdf_service.generate_quote_pdf(
                quote_data=quote,
                contractor=DEMO_CONTRACTOR,
                terms=DEMO_TERMS,
                output_path=pdf_path,
            )
            print(f"PDF generated: {pdf_path}")

        except Exception as e:
            print(f"ERROR: {str(e)}")
            results.append({
                "name": sample["name"],
                "success": False,
                "error": str(e),
            })

        print()
        print("=" * 60)
        print()

    # Summary
    print("TEST SUMMARY")
    print("-" * 40)
    successful = sum(1 for r in results if r.get("success"))
    print(f"Total tests: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {len(results) - successful}")
    print()

    for r in results:
        status = "PASS" if r.get("success") else "FAIL"
        if r.get("success"):
            print(f"  [{status}] {r['name']}: ${r['total']:,.2f} ({r['confidence']})")
        else:
            print(f"  [{status}] {r['name']}: {r.get('error', 'Unknown error')}")

    return results


async def test_learning_loop():
    """Test the learning/correction loop."""
    print()
    print("=" * 60)
    print("QUOTED - Learning Loop Test")
    print("=" * 60)
    print()

    quote_service = get_quote_service()
    learning_service = get_learning_service()

    # Generate an initial quote
    original_quote = await quote_service.generate_quote(
        transcription="16 by 20 composite deck, Trex Select. Standard railing, 45 feet. 4 steps.",
        contractor=DEMO_CONTRACTOR,
        pricing_model=DEMO_PRICING_MODEL,
    )

    print(f"Original quote total: ${original_quote.get('subtotal', 0):,.2f}")

    # Simulate a correction (contractor adjusted the price up by 10%)
    corrected_quote = original_quote.copy()
    corrected_items = []
    for item in corrected_quote.get("line_items", []):
        new_item = item.copy()
        new_item["amount"] = item.get("amount", 0) * 1.1  # 10% increase
        corrected_items.append(new_item)
    corrected_quote["line_items"] = corrected_items
    corrected_quote["subtotal"] = sum(i.get("amount", 0) for i in corrected_items)

    print(f"Corrected quote total: ${corrected_quote.get('subtotal', 0):,.2f}")

    # Process the correction
    learning_result = await learning_service.process_correction(
        original_quote=original_quote,
        final_quote=corrected_quote,
        contractor_notes="I always add 10% for jobs in this neighborhood - parking is tough.",
    )

    print()
    print("Learning Result:")
    print(f"  Has changes: {learning_result.get('has_changes')}")
    if learning_result.get("corrections"):
        corrections = learning_result["corrections"]
        print(f"  Total change: ${corrections.get('total_change', 0):,.2f}")
        print(f"  Percent change: {corrections.get('total_change_percent', 0):.1f}%")

    if learning_result.get("learnings"):
        learnings = learning_result["learnings"]
        print(f"  Overall tendency: {learnings.get('overall_tendency', 'N/A')}")
        print(f"  Summary: {learnings.get('summary', 'N/A')[:200]}...")

    print()
    print("Learning loop test complete!")


def main():
    """Run all tests."""
    print()
    print("*" * 60)
    print("*  QUOTED - Voice to Quote for Contractors")
    print("*  End-to-End Test Suite")
    print("*" * 60)
    print()

    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("WARNING: ANTHROPIC_API_KEY not set!")
        print("Set it with: export ANTHROPIC_API_KEY=your-key-here")
        print()
        print("Running in mock mode (tests will fail without real API)...")
        print()

    # Run tests
    asyncio.run(test_quote_generation())
    asyncio.run(test_learning_loop())


if __name__ == "__main__":
    main()
