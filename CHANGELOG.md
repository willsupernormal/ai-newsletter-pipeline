# Changelog

All notable changes to the AI Newsletter Pipeline project.

---

## [3.0.0] - 2025-11-05

### Major Changes

#### Phase 3: Google Drive / Markdown Output
- **Added:** Flexible content output system with 3 modes
  - `CONTENT_OUTPUT_MODE=airtable` - Airtable only (default, backward compatible)
  - `CONTENT_OUTPUT_MODE=markdown` - Google Drive markdown only
  - `CONTENT_OUTPUT_MODE=both` - Save to both destinations in parallel
- **Added:** Markdown + YAML frontmatter format for Claude Code querying
- **Added:** Google Drive API integration (reuses Context Parser service account)
- **Benefit:** Choose output destination without code changes, queryable content files

#### New Files Created
- `services/gdocs_markdown_client.py` - Google Drive markdown file creation and upload
- `services/content_pipeline.py` - Content routing orchestrator

#### Updated Files
- `services/slack_webhook_handler.py` - Routes to content pipeline instead of direct Airtable
- `config/settings.py` - Added 3 new environment variables
- `.env.example` - Documented Google Drive configuration
- `README.md` - Added Phase 3 documentation and architecture diagrams

### Technical Implementation

#### Content Pipeline Architecture
```python
# User clicks button in Slack
→ Railway webhook receives submission
→ ContentPipelineHandler routes based on CONTENT_OUTPUT_MODE
→ Saves to Airtable and/or Google Drive
→ Returns unified result
→ Slack shows success with destination info
```

#### Markdown File Format
- **YAML frontmatter:** Structured metadata (title, theme, tags, etc.)
- **Markdown body:** Human-readable content with sections
- **Queryable:** Use `grep` or Claude Code to filter by metadata
- **Example:** `2025-11-05-openai-gpt5.md`

#### Environment Variables (New)
```bash
CONTENT_OUTPUT_MODE=airtable|markdown|both
GOOGLE_SERVICE_ACCOUNT_KEY={json_string}
MARKDOWN_CONTENT_FOLDER_ID=drive_folder_id
```

### Backward Compatibility

- ✅ **100% backward compatible** - Defaults to Airtable-only mode
- ✅ **No breaking changes** - Existing deployments continue working
- ✅ **Old code preserved** - AirtableClient still exists, now wrapped by pipeline
- ✅ **Easy rollback** - Set `CONTENT_OUTPUT_MODE=airtable` to revert

### Benefits

#### For Content Management
- **Flexibility:** Choose storage based on workflow needs
- **Redundancy:** Save to both destinations for backup
- **Migration:** Easy transition from Airtable to Drive

#### For Claude Code Integration
- **Queryable:** Structured YAML enables filtering and search
- **File-first:** Matches Context Parser System philosophy
- **Grep-friendly:** Use CLI tools to query content
- **Example queries:**
  ```bash
  grep -r "theme: \"AI Governance\"" ./content/
  grep -r "companies_mentioned.*OpenAI" ./content/
  ```

### Infrastructure Reuse

- **Service Account:** Reuses `context-parser-service@context-parser.iam.gserviceaccount.com`
- **Shared Drive:** Uses same "Context Parser" drive as Slack integration
- **Railway:** Same deployment, just new environment variables
- **No new costs:** Leverages existing Google Workspace

### Testing Recommendations

1. **Test Airtable-only** (default):
   ```bash
   CONTENT_OUTPUT_MODE=airtable
   ```

2. **Test Markdown-only:**
   ```bash
   CONTENT_OUTPUT_MODE=markdown
   GOOGLE_SERVICE_ACCOUNT_KEY={...}
   MARKDOWN_CONTENT_FOLDER_ID={...}
   ```

3. **Test Both:**
   ```bash
   CONTENT_OUTPUT_MODE=both
   ```

### Documentation

- **README.md:** Complete Phase 3 section with architecture diagrams
- **CHANGELOG.md:** This file
- **.env.example:** Documented all new variables with examples
- **In-code comments:** Comprehensive docstrings in new files

---

## [2.0.0] - 2025-10-30

### Major Changes

#### Simplified AI Fields (9 → 5)
- **Removed:** `strategic_context`, `talking_points`, `newsletter_angles`, `technical_details`
- **Kept:** `detailed_summary`, `business_impact`, `key_quotes`, `specific_data`, `companies_mentioned`
- **Merged:** Strategic context now included in `business_impact`
- **Benefit:** 44% reduction in AI fields, simpler Airtable integration

#### Interactive Slack Modal
- **Added:** Modal form on "Add to Pipeline" button click
- **Fields:** Theme (10 options), Content Type (6 options), Your Angle (free text)
- **All optional:** Can submit without filling any fields
- **User Experience:** Better content categorization and customization

### Technical Improvements

#### Database
- Dropped 4 unused columns from `digest_articles` table
- Dropped dependent views before column removal
- Recreated views with simplified schema
- Added migration: `update_digest_articles_remove_fields.sql`

#### Airtable Integration
- Added 3 new user-selected fields: Theme, Content Type, Your Angle
- Simplified to 5 AI-generated fields
- Exact field name matching (case-sensitive)
- Better error handling for field mismatches

#### Railway Webhook Server
- Added modal opening on button click
- Added modal submission handling
- Async processing of modal submissions
- Success messages posted to channel
- Better user object handling

#### Code Quality
- Fixed JSONB parsing errors in Airtable client
- Added type checks for None and string values
- Better error logging and debugging
- Cleaner separation of concerns

### Bug Fixes
- Fixed `'str' object has no attribute 'get'` error in webhook server
- Fixed `name 'theme' is not defined` error in async handler
- Fixed channel_not_found error in Slack posting
- Fixed view dependency errors in database migration

### Documentation
- Created comprehensive README with architecture diagrams
- Created CHANGELOG for version tracking
- Created TROUBLESHOOTING guide with common issues
- Removed 20+ unnecessary markdown files
- Consolidated all important information

---

## [1.5.0] - 2025-10-28

### Added
- Async button processing (no more 3-second timeouts)
- Visual button feedback (Processing → Added)
- Background task processing for Airtable operations
- Response URL for async Slack updates

### Fixed
- Slack button timeout issues
- Button state management
- Error handling in webhook server

---

## [1.4.0] - 2025-10-26

### Added
- Railway webhook server for production
- FastAPI endpoint for Slack interactions
- Slack signature verification
- Environment-based configuration

### Changed
- Moved from local webhook to Railway production server
- Updated Slack app configuration for interactivity
- Improved error logging

---

## [1.3.0] - 2025-10-25

### Added
- Slack interactive buttons
- "Add to Pipeline" button in digest messages
- Airtable integration for article storage
- Full article scraping on button click

### Changed
- Digest format to include interactive elements
- Article storage to include Airtable tracking

---

## [1.2.0] - 2025-10-20

### Added
- Multi-stage AI filtering (Stage 1: 18 articles, Stage 2: 5 articles)
- 9 AI-generated fields per article
- Supabase `digest_articles` table
- Comprehensive AI analysis for each article

### Changed
- Replaced single-stage filtering with two-stage process
- Improved article selection quality
- Better AI prompt engineering

---

## [1.1.0] - 2025-10-15

### Added
- 31 RSS feed sources
- Daily digest generation
- Slack posting integration
- Basic AI filtering with GPT-4

### Changed
- Expanded from 14 to 31 RSS sources
- Improved scraping reliability
- Better error handling

---

## [1.0.0] - 2025-10-01

### Initial Release
- RSS feed scraping
- Basic AI evaluation
- Supabase storage
- Daily digest generation
- Slack integration

---

## Key Milestones

### Version 2.0 (Current)
- **Focus:** Simplification and user experience
- **Achievement:** Streamlined AI fields, interactive modal, cleaner codebase
- **Impact:** Faster development, easier maintenance, better UX

### Version 1.5
- **Focus:** Performance and reliability
- **Achievement:** Async processing, no timeouts
- **Impact:** 100% button click success rate

### Version 1.4
- **Focus:** Production deployment
- **Achievement:** Railway webhook server
- **Impact:** 24/7 availability, scalable infrastructure

### Version 1.3
- **Focus:** Interactivity
- **Achievement:** Slack buttons, Airtable integration
- **Impact:** One-click article addition to content pipeline

### Version 1.2
- **Focus:** AI quality
- **Achievement:** Multi-stage filtering, comprehensive AI analysis
- **Impact:** Better article selection, richer metadata

### Version 1.0
- **Focus:** Core functionality
- **Achievement:** Automated daily digest
- **Impact:** Daily AI news delivered to Slack

---

## Lessons Learned

### Database Changes
- **Always check for dependent views before dropping columns**
- Use `DROP VIEW IF EXISTS ... CASCADE` before schema changes
- Recreate views after column modifications
- Test migrations on copy of data first

### Slack Integration
- **All tokens must be from same Slack app**
- Interactivity requires OAuth redirect URL
- Modal submissions have different payload structure
- Use `trigger_id` to open modals (expires in 3 seconds)

### Airtable Integration
- **Field names must match exactly (case-sensitive)**
- Create Airtable fields before deploying code
- Use Long text for AI-generated content
- Single select for dropdowns, Single line text for arrays

### Railway Deployment
- **Auto-deploys on git push to main**
- Takes 2-3 minutes to deploy
- Check logs for successful startup
- Environment variables must be set in Railway dashboard

### Code Quality
- **Always check for None values before calling methods**
- Use `isinstance()` checks for type safety
- Add comprehensive error logging
- Test end-to-end before deploying

---

## Future Improvements

### Planned
- [ ] Automated daily digest scheduling (GitHub Actions)
- [ ] Email digest option
- [ ] Article analytics and tracking
- [ ] Custom RSS feed management UI
- [ ] A/B testing for AI prompts

### Under Consideration
- [ ] Multiple Slack workspaces support
- [ ] Multiple Airtable bases support
- [ ] Article recommendation engine
- [ ] Sentiment analysis
- [ ] Trend detection

---

## Breaking Changes

### Version 2.0
- **Database:** Removed 4 columns from `digest_articles` table
- **Airtable:** Removed 4 fields, added 3 new fields
- **Code:** Changed method signatures in `slack_webhook_handler.py`
- **Migration Required:** Run `update_digest_articles_remove_fields.sql`

### Version 1.4
- **Environment:** New Railway deployment required
- **Slack:** New app configuration required
- **Tokens:** All 3 tokens must be updated

### Version 1.2
- **Database:** New `digest_articles` table required
- **Schema:** Run `create_digest_articles_table.sql`

---

## Contributors

- Will Bainbridge - Project Lead & Developer

---

## Support

For issues and questions:
- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Review Railway logs
- Check Supabase logs
- Verify environment variables
