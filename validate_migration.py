#!/usr/bin/env python3
"""
Validate the SQL migration file for digest_articles table
"""

import re

def validate_migration():
    """Validate the SQL migration file"""
    
    print("🔍 Validating SQL Migration File...")
    print("=" * 60)
    
    with open('database/migrations/create_digest_articles_table.sql', 'r') as f:
        sql = f.read()
    
    checks = []
    
    # Check 1: Table creation
    if 'CREATE TABLE IF NOT EXISTS digest_articles' in sql:
        checks.append(("✅", "Table creation statement found"))
    else:
        checks.append(("❌", "Table creation statement MISSING"))
    
    # Check 2: Required columns
    required_columns = [
        'id', 'title', 'url', 'source_name', 'source_type',
        'digest_date', 'detailed_summary', 'business_impact',
        'strategic_context', 'key_quotes', 'specific_data',
        'talking_points', 'newsletter_angles', 'technical_details',
        'companies_mentioned', 'posted_to_slack', 'added_to_airtable'
    ]
    
    missing_columns = []
    for col in required_columns:
        if col not in sql:
            missing_columns.append(col)
    
    if not missing_columns:
        checks.append(("✅", f"All {len(required_columns)} required columns found"))
    else:
        checks.append(("❌", f"Missing columns: {', '.join(missing_columns)}"))
    
    # Check 3: Indexes
    required_indexes = [
        'idx_digest_articles_date',
        'idx_digest_articles_companies',
        'idx_digest_articles_technical',
        'idx_digest_articles_url',
        'idx_digest_articles_slack'
    ]
    
    missing_indexes = []
    for idx in required_indexes:
        if idx not in sql:
            missing_indexes.append(idx)
    
    if not missing_indexes:
        checks.append(("✅", f"All {len(required_indexes)} indexes found"))
    else:
        checks.append(("❌", f"Missing indexes: {', '.join(missing_indexes)}"))
    
    # Check 4: Unique constraint
    if 'idx_digest_articles_url_date' in sql and 'UNIQUE' in sql:
        checks.append(("✅", "Unique constraint on (url, digest_date) found"))
    else:
        checks.append(("❌", "Unique constraint MISSING"))
    
    # Check 5: Views
    if 'current_week_digest' in sql and 'pending_airtable_articles' in sql:
        checks.append(("✅", "Both views (current_week_digest, pending_airtable_articles) found"))
    else:
        checks.append(("❌", "Views MISSING"))
    
    # Check 6: Data types
    if 'JSONB' in sql:
        checks.append(("✅", "JSONB type used for key_quotes and specific_data"))
    else:
        checks.append(("❌", "JSONB type MISSING"))
    
    if 'TEXT[]' in sql:
        checks.append(("✅", "Array type used for talking_points, etc."))
    else:
        checks.append(("❌", "Array type MISSING"))
    
    # Check 7: GIN indexes for arrays
    if 'USING gin' in sql or 'using gin' in sql.lower():
        checks.append(("✅", "GIN indexes for array columns found"))
    else:
        checks.append(("❌", "GIN indexes MISSING"))
    
    # Print results
    print()
    for status, message in checks:
        print(f"{status} {message}")
    
    print()
    print("=" * 60)
    
    # Summary
    passed = sum(1 for status, _ in checks if status == "✅")
    total = len(checks)
    
    if passed == total:
        print(f"✅ ALL CHECKS PASSED ({passed}/{total})")
        print()
        print("Migration file is valid! Ready to execute in Supabase.")
        return True
    else:
        print(f"❌ SOME CHECKS FAILED ({passed}/{total} passed)")
        print()
        print("Please review the migration file before executing.")
        return False

if __name__ == '__main__':
    success = validate_migration()
    exit(0 if success else 1)
