#!/usr/bin/env python3
"""
Audit production learning data quality.
Runs via: railway run python scripts/audit_learning_data.py
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.models.database import PricingModel
from backend.services.database import get_session
import json

def score_statement(statement: str, category: str) -> dict:
    """Score a learning statement 0-100 based on quality heuristics."""
    score = 0
    issues = []

    # Length check (30-200 chars is ideal)
    length = len(statement)
    if 30 <= length <= 200:
        score += 10
    elif length < 30:
        issues.append("too_short")
    else:
        issues.append("too_long")

    # Has dollar amounts ($X)
    if '$' in statement:
        score += 30
    else:
        issues.append("no_dollar_amounts")

    # Has percentages (X%)
    if '%' in statement:
        score += 25

    # Has specific items (check common terms)
    specific_terms = ['deck', 'tile', 'paint', 'sqft', 'linear', 'foot', 'railing',
                      'demo', 'material', 'labor', 'hour', 'day']
    if any(term in statement.lower() for term in specific_terms):
        score += 30
    else:
        issues.append("too_generic")

    # Has action words
    action_words = ['increase', 'add', 'charge', 'reduce', 'multiply', 'adjust',
                    'include', 'budget']
    if any(word in statement.lower() for word in action_words):
        score += 20
    else:
        issues.append("no_action_words")

    # Vague phrases (penalize)
    vague = ['sometimes', 'maybe', 'consider', 'might', 'could', 'generally', 'usually']
    if any(word in statement.lower() for word in vague):
        score -= 15
        issues.append("vague_language")

    # Generic phrases (penalize)
    generic = ['review', 'careful', 'pay attention', 'make sure', 'check']
    if any(phrase in statement.lower() for phrase in generic):
        score -= 10
        issues.append("generic_advice")

    # Cap at 0-100
    score = max(0, min(100, score))

    # Quality tier
    if score >= 70:
        tier = "high"
    elif score >= 40:
        tier = "medium"
    elif score >= 20:
        tier = "low"
    else:
        tier = "useless"

    return {
        "score": score,
        "tier": tier,
        "issues": issues,
        "statement": statement,
        "category": category
    }

def main():
    session = next(get_session())
    models = session.query(PricingModel).all()

    total_statements = 0
    category_counts = {}
    contractor_counts = {}
    all_scores = []

    print("\n=== PRODUCTION LEARNING DATA AUDIT ===\n")

    for model in models:
        contractor_id = model.contractor_id

        if model.pricing_knowledge and 'categories' in model.pricing_knowledge:
            for cat_name, cat_data in model.pricing_knowledge['categories'].items():
                learnings = cat_data.get('learned_adjustments', [])

                if learnings:
                    count = len(learnings)
                    total_statements += count
                    category_counts[cat_name] = category_counts.get(cat_name, 0) + count

                    if contractor_id not in contractor_counts:
                        contractor_counts[contractor_id] = 0
                    contractor_counts[contractor_id] += count

                    # Score each statement
                    for stmt in learnings:
                        scored = score_statement(stmt, cat_name)
                        all_scores.append(scored)

    # Summary statistics
    print(f"Total learning statements: {total_statements}")
    print(f"Categories with learnings: {len(category_counts)}")
    print(f"Contractors with learnings: {len(contractor_counts)}")
    print(f"\n--- Category Distribution ---")
    for cat, count in sorted(category_counts.items(), key=lambda x: -x[1])[:10]:
        print(f"  {cat}: {count}")

    # Quality distribution
    print(f"\n--- Quality Distribution ---")
    tier_counts = {"high": 0, "medium": 0, "low": 0, "useless": 0}
    for scored in all_scores:
        tier_counts[scored["tier"]] += 1

    total = len(all_scores)
    print(f"High (70+):    {tier_counts['high']:4d} ({tier_counts['high']/total*100:5.1f}%)")
    print(f"Medium (40-69): {tier_counts['medium']:4d} ({tier_counts['medium']/total*100:5.1f}%)")
    print(f"Low (20-39):   {tier_counts['low']:4d} ({tier_counts['low']/total*100:5.1f}%)")
    print(f"Useless (<20):  {tier_counts['useless']:4d} ({tier_counts['useless']/total*100:5.1f}%)")

    # Sample from each tier
    print(f"\n--- Sample Statements (30 total) ---")
    samples_per_tier = 7

    for tier in ["high", "medium", "low", "useless"]:
        tier_samples = [s for s in all_scores if s["tier"] == tier][:samples_per_tier]
        if tier_samples:
            print(f"\n{tier.upper()} Quality:")
            for s in tier_samples[:5]:  # Show 5 per tier
                print(f"  [{s['category']}] Score: {s['score']}")
                print(f"    \"{s['statement'][:100]}...\"" if len(s['statement']) > 100 else f"    \"{s['statement']}\"")
                if s['issues']:
                    print(f"    Issues: {', '.join(s['issues'])}")

    # Recommendations
    print(f"\n--- Recommendations ---")

    useless_pct = tier_counts['useless'] / total * 100
    low_pct = tier_counts['low'] / total * 100

    if useless_pct > 20:
        print(f"⚠️  {useless_pct:.0f}% of statements are USELESS (score <20)")
        print("   → Implement quality filtering before storage")

    if (useless_pct + low_pct) > 40:
        print(f"⚠️  {useless_pct + low_pct:.0f}% of statements are LOW quality (score <40)")
        print("   → Revise refinement prompt to require specificity")

    high_pct = tier_counts['high'] / total * 100
    if high_pct < 30:
        print(f"⚠️  Only {high_pct:.0f}% of statements are HIGH quality (score 70+)")
        print("   → Prompt should require: dollar amounts, percentages, specific items")

    # Export detailed results
    output_file = "/tmp/learning_audit_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            "summary": {
                "total_statements": total_statements,
                "categories": len(category_counts),
                "contractors": len(contractor_counts),
                "quality_distribution": tier_counts
            },
            "all_scores": all_scores[:100]  # First 100 for detailed review
        }, f, indent=2)

    print(f"\n✅ Detailed results exported to: {output_file}")

if __name__ == "__main__":
    main()
