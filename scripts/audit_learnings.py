#!/usr/bin/env python3
"""
Phase 1.1: Learning Statement Quality Audit
Queries production database for learning statements and analyzes quality.
"""
import asyncpg
import asyncio
import json
import os
import re

async def query_db():
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print('ERROR: DATABASE_URL not set')
        return

    print(f'Connecting to database...')

    # Convert postgres:// to postgresql:// for asyncpg
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)

    conn = await asyncpg.connect(db_url)

    # Query pricing models
    rows = await conn.fetch('''
        SELECT id, contractor_id, pricing_knowledge
        FROM pricing_models
        WHERE pricing_knowledge IS NOT NULL
    ''')

    print(f'Total pricing models: {len(rows)}')

    all_statements = []
    category_counts = {}

    for row in rows:
        pk = row['pricing_knowledge']
        if pk and 'categories' in pk:
            for cat_name, cat_data in pk['categories'].items():
                statements = cat_data.get('learned_adjustments', [])
                category_counts[cat_name] = category_counts.get(cat_name, 0) + len(statements)
                for stmt in statements:
                    all_statements.append({
                        'contractor_id': str(row['contractor_id']),
                        'category': cat_name,
                        'statement': str(stmt)[:300]
                    })

    print(f'Total learning statements: {len(all_statements)}')
    print(f'\nCategory distribution (top 15):')
    for cat, count in sorted(category_counts.items(), key=lambda x: -x[1])[:15]:
        print(f'  {cat}: {count} statements')

    # Quality scoring
    def score_quality(stmt):
        """Score a learning statement 0-100"""
        score = 0
        s = stmt.lower()

        # Has numbers (0-30 points)
        if re.search(r'\$\d+', s):  # Dollar amounts
            score += 30
        elif re.search(r'\d+%', s):  # Percentages
            score += 25
        elif re.search(r'\d+', s):  # Any numbers
            score += 15

        # Has specific items/actions (0-30 points)
        specific_words = ['deck', 'bathroom', 'kitchen', 'tile', 'demo', 'labor',
                         'material', 'railing', 'flooring', 'concrete', 'paint',
                         'plumbing', 'electrical', 'drywall', 'cabinet', 'window']
        if any(w in s for w in specific_words):
            score += 30

        # Has actionable direction (0-20 points)
        action_words = ['increase', 'decrease', 'add', 'reduce', 'charge', 'minimum',
                       'markup', 'higher', 'lower', 'include', 'exclude']
        if any(w in s for w in action_words):
            score += 20

        # Reasonable length (0-10 points)
        if 30 < len(stmt) < 200:
            score += 10
        elif len(stmt) >= 20:
            score += 5

        # Penalize generic phrases (0-10 points penalty)
        generic = ['review pricing', 'carefully', 'be careful', 'consider', 'might need']
        if any(g in s for g in generic):
            score -= 10

        return max(0, min(100, score))

    # Score all statements
    quality_dist = {'high': 0, 'medium': 0, 'low': 0, 'useless': 0}
    scored_statements = []

    for s in all_statements:
        score = score_quality(s['statement'])
        s['quality_score'] = score
        scored_statements.append(s)

        if score >= 70:
            quality_dist['high'] += 1
        elif score >= 40:
            quality_dist['medium'] += 1
        elif score >= 20:
            quality_dist['low'] += 1
        else:
            quality_dist['useless'] += 1

    total = len(all_statements)
    print(f'\n=== QUALITY DISTRIBUTION ===')
    print(f'High (70+):    {quality_dist["high"]:3d} ({100*quality_dist["high"]/total:.1f}%)')
    print(f'Medium (40-69): {quality_dist["medium"]:3d} ({100*quality_dist["medium"]/total:.1f}%)')
    print(f'Low (20-39):   {quality_dist["low"]:3d} ({100*quality_dist["low"]/total:.1f}%)')
    print(f'Useless (<20): {quality_dist["useless"]:3d} ({100*quality_dist["useless"]/total:.1f}%)')

    # Show examples
    high_quality = [s for s in scored_statements if s['quality_score'] >= 70]
    low_quality = [s for s in scored_statements if s['quality_score'] < 20]

    print(f'\n=== HIGH QUALITY EXAMPLES (score >= 70) ===')
    for s in sorted(high_quality, key=lambda x: -x['quality_score'])[:10]:
        print(f'  [{s["quality_score"]}] [{s["category"]}] {s["statement"][:150]}')

    print(f'\n=== LOW QUALITY EXAMPLES (score < 20) ===')
    for s in low_quality[:10]:
        print(f'  [{s["quality_score"]}] [{s["category"]}] {s["statement"][:150]}')

    await conn.close()
    print('\nDone!')

if __name__ == '__main__':
    asyncio.run(query_db())
