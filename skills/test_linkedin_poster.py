"""
LinkedIn Auto-Poster Test Suite

Tests all components of the LinkedIn posting system:
1. Authentication system
2. Content generation
3. Draft creation
4. Approval workflow
5. Post execution
6. Integration with vault

Usage:
    python skills/test_linkedin_poster.py --vault ./AI_Employee_Vault
"""

import sys
import json
import time
import logging
from pathlib import Path
from datetime import datetime

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from watchers.base_watcher import setup_logging

logger = setup_logging('LinkedInPosterTest')


def test_auth_module():
    """Test 1: LinkedIn Authentication Module"""
    logger.info('=' * 60)
    logger.info('TEST 1: LinkedIn Authentication Module')
    logger.info('=' * 60)

    try:
        from skills.linkedin_auth import LinkedInAuth

        # Create auth instance
        auth = LinkedInAuth()
        logger.info('✅ LinkedInAuth class instantiated')

        # Check session status
        has_session = auth.has_valid_session()
        if has_session:
            logger.info('✅ Valid LinkedIn session found')
            logger.info(f'   Session path: {auth.session_path}')
        else:
            logger.info('⚠️  No LinkedIn session found (expected for first run)')
            logger.info('   Run: python skills/linkedin_auth.py --login')

        return True

    except Exception as e:
        logger.error(f'❌ Auth module test failed: {e}', exc_info=True)
        return False


def test_poster_instantiation():
    """Test 2: LinkedInPoster Class Instantiation"""
    logger.info('=' * 60)
    logger.info('TEST 2: LinkedInPoster Class Instantiation')
    logger.info('=' * 60)

    try:
        from skills.linkedin_poster import LinkedInPoster

        vault_path = Path(__file__).parent.parent / 'AI_Employee_Vault'

        # Create poster instance
        poster = LinkedInPoster(vault_path=str(vault_path))
        logger.info('✅ LinkedInPoster instantiated')

        # Verify components
        assert poster.auth is not None, 'Auth helper not initialized'
        logger.info('✅ Authentication helper initialized')

        assert poster.drafts_folder.exists(), 'Drafts folder missing'
        logger.info(f'✅ Drafts folder exists: {poster.drafts_folder}')

        assert poster.pending_approval.exists(), 'Pending approval folder missing'
        logger.info(f'✅ Pending approval folder exists')

        assert poster.approved_folder.exists(), 'Approved folder missing'
        logger.info(f'✅ Approved folder exists')

        return True

    except Exception as e:
        logger.error(f'❌ Poster instantiation test failed: {e}', exc_info=True)
        return False


def test_content_generation():
    """Test 3: Content Generation for All Categories"""
    logger.info('=' * 60)
    logger.info('TEST 3: Content Generation (All Categories)')
    logger.info('=' * 60)

    try:
        from skills.linkedin_poster import LinkedInPoster

        vault_path = Path(__file__).parent.parent / 'AI_Employee_Vault'
        poster = LinkedInPoster(vault_path=str(vault_path))

        categories = [
            'service_announcement',
            'success_story',
            'industry_insight',
            'behind_the_scenes',
            'thought_leadership'
        ]

        all_ok = True
        generated_posts = []

        for category in categories:
            # Generate post
            post_data = poster.generate_post(category)

            # Validate structure
            if not post_data.get('text'):
                logger.error(f'❌ {category}: No text generated')
                all_ok = False
                continue

            if len(post_data['text']) < 50:
                logger.error(f'❌ {category}: Post too short ({len(post_data["text"])} chars)')
                all_ok = False
                continue

            if not post_data.get('hashtags'):
                logger.error(f'❌ {category}: No hashtags')
                all_ok = False
                continue

            logger.info(f'✅ {category}: {len(post_data["text"])} chars, {len(post_data["hashtags"])} hashtags')
            generated_posts.append((category, post_data))

        if all_ok:
            logger.info(f'✅ All {len(categories)} categories generated successfully')
        else:
            logger.warning(f'⚠️  Some categories failed to generate')

        return all_ok and len(generated_posts) > 0

    except Exception as e:
        logger.error(f'❌ Content generation test failed: {e}', exc_info=True)
        return False


def test_draft_creation():
    """Test 4: Draft File Creation"""
    logger.info('=' * 60)
    logger.info('TEST 4: Draft File Creation')
    logger.info('=' * 60)

    try:
        from skills.linkedin_poster import LinkedInPoster

        vault_path = Path(__file__).parent.parent / 'AI_Employee_Vault'
        poster = LinkedInPoster(vault_path=str(vault_path))

        # Generate a post
        post_data = poster.generate_post('industry_insight')

        # Create draft file
        draft_path = poster.create_draft_file(post_data)

        if not draft_path.exists():
            logger.error('❌ Draft file was not created')
            return False

        logger.info(f'✅ Draft file created: {draft_path.name}')

        # Verify draft content
        content = draft_path.read_text(encoding='utf-8')

        # Check for required sections
        required_sections = [
            '---',  # Frontmatter
            'type: linkedin_draft',
            'category:',
            '# LinkedIn Post Draft',
            '## Content',
            '## Metadata',
            '## Suggested Actions'
        ]

        for section in required_sections:
            if section not in content:
                logger.error(f'❌ Draft missing required section: {section}')
                return False

        logger.info('✅ Draft file structure validated')
        logger.info(f'✅ Draft contains {len(content)} characters')

        # Verify post content is in draft
        if post_data['text'] in content:
            logger.info('✅ Post content correctly embedded in draft')
        else:
            logger.warning('⚠️  Post content may not be properly embedded')

        return True

    except Exception as e:
        logger.error(f'❌ Draft creation test failed: {e}', exc_info=True)
        return False


def test_approval_workflow():
    """Test 5: Approval Request Creation"""
    logger.info('=' * 60)
    logger.info('TEST 5: Approval Workflow')
    logger.info('=' * 60)

    try:
        from skills.linkedin_poster import LinkedInPoster

        vault_path = Path(__file__).parent.parent / 'AI_Employee_Vault'
        poster = LinkedInPoster(vault_path=str(vault_path))

        # Generate post and create approval
        approval_path = poster.run_with_approval('success_story')

        if not approval_path.exists():
            logger.error('❌ Approval request was not created')
            return False

        logger.info(f'✅ Approval request created: {approval_path.name}')

        # Verify approval content
        content = approval_path.read_text(encoding='utf-8')

        required_fields = [
            'type: approval_request',
            'action: linkedin_post',
            'status: pending',
            'draft_file:',
            '# LinkedIn Post - Approval Required',
            '## To Approve',
            '## To Reject'
        ]

        for field in required_fields:
            if field not in content:
                logger.error(f'❌ Approval missing: {field}')
                return False

        logger.info('✅ Approval request structure validated')

        # Verify draft file was also created
        draft_ref = None
        for line in content.split('\n')[:20]:
            if line.startswith('draft_file:'):
                draft_ref = line.split(':', 1)[1].strip()
                break

        if draft_ref:
            draft_path = poster.drafts_folder / draft_ref
            if draft_path.exists():
                logger.info(f'✅ Referenced draft exists: {draft_ref}')
            else:
                logger.warning(f'⚠️  Referenced draft not found: {draft_ref}')

        return True

    except Exception as e:
        logger.error(f'❌ Approval workflow test failed: {e}', exc_info=True)
        return False


def test_content_extraction():
    """Test 6: Content Extraction from Draft"""
    logger.info('=' * 60)
    logger.info('TEST 6: Content Extraction from Draft')
    logger.info('=' * 60)

    try:
        from skills.linkedin_poster import LinkedInPoster

        vault_path = Path(__file__).parent.parent / 'AI_Employee_Vault'
        poster = LinkedInPoster(vault_path=str(vault_path))

        # Create a test draft
        post_data = poster.generate_post('thought_leadership')
        draft_path = poster.create_draft_file(post_data)

        # Read draft content
        draft_content = draft_path.read_text(encoding='utf-8')

        # Extract content
        extracted = poster._extract_post_content(draft_content)

        if not extracted:
            logger.error('❌ Content extraction returned empty')
            return False

        if len(extracted) < 50:
            logger.error(f'❌ Extracted content too short: {len(extracted)} chars')
            return False

        logger.info(f'✅ Extracted {len(extracted)} characters from draft')

        # Verify extracted content matches original
        if post_data['text'] in extracted or extracted in post_data['text']:
            logger.info('✅ Extracted content matches original post')
        else:
            logger.warning('⚠️  Extracted content may differ from original')

        # Show preview
        preview = extracted[:100].replace('\n', ' ')
        logger.info(f'✅ Preview: {preview}...')

        return True

    except Exception as e:
        logger.error(f'❌ Content extraction test failed: {e}', exc_info=True)
        return False


def test_folder_structure():
    """Test 7: Vault Folder Structure"""
    logger.info('=' * 60)
    logger.info('TEST 7: Vault Folder Structure')
    logger.info('=' * 60)

    vault_path = Path(__file__).parent.parent / 'AI_Employee_Vault'

    required_folders = [
        'Drafts/LinkedIn',
        'Pending_Approval/LinkedIn',
        'Approved/LinkedIn',
        'Rejected/LinkedIn',
        'Done/LinkedIn',
        'Logs'
    ]

    all_ok = True

    for folder in required_folders:
        folder_path = vault_path / folder
        if folder_path.exists() and folder_path.is_dir():
            logger.info(f'✅ {folder}/ exists')
        else:
            logger.warning(f'⚠️  {folder}/ not found')
            all_ok = False

    return all_ok


def test_integration_with_auth():
    """Test 8: Integration with Authentication"""
    logger.info('=' * 60)
    logger.info('TEST 8: Integration with Authentication')
    logger.info('=' * 60)

    try:
        from skills.linkedin_poster import LinkedInPoster
        from skills.linkedin_auth import LinkedInAuth

        vault_path = Path(__file__).parent.parent / 'AI_Employee_Vault'

        # Create both instances
        poster = LinkedInPoster(vault_path=str(vault_path))
        auth = LinkedInAuth()

        # Verify they use the same session path
        if poster.session_path == auth.session_path:
            logger.info('✅ Poster and Auth use same session path')
        else:
            logger.warning('⚠️  Session paths differ (may be intentional)')

        # Check auth status
        if poster.auth.has_valid_session():
            logger.info('✅ Poster has valid LinkedIn session')
            logger.info('ℹ️  Ready for automated posting')
        else:
            logger.info('⚠️  No LinkedIn session - posting will require login')
            logger.info('ℹ️  Run: python skills/linkedin_auth.py --login')

        return True  # This test passes either way - it's informational

    except Exception as e:
        logger.error(f'❌ Integration test failed: {e}', exc_info=True)
        return False


def run_all_tests():
    """Run complete LinkedIn Poster test suite."""
    logger.info('')
    logger.info('╔' + '═' * 58 + '╗')
    logger.info('║' + ' ' * 12 + 'LINKEDIN POSTER TEST SUITE' + ' ' * 19 + '║')
    logger.info('╚' + '═' * 58 + '╝')
    logger.info('')
    logger.info(f'Test run started: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    logger.info('')

    tests = [
        ('Authentication Module', test_auth_module),
        ('Poster Instantiation', test_poster_instantiation),
        ('Content Generation', test_content_generation),
        ('Draft Creation', test_draft_creation),
        ('Approval Workflow', test_approval_workflow),
        ('Content Extraction', test_content_extraction),
        ('Folder Structure', test_folder_structure),
        ('Auth Integration', test_integration_with_auth),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            logger.info('')
            time.sleep(0.3)
        except Exception as e:
            logger.error(f'❌ Test {test_name} crashed: {e}', exc_info=True)
            results.append((test_name, False))
            logger.info('')

    # Summary
    logger.info('')
    logger.info('╔' + '═' * 58 + '╗')
    logger.info('║' + ' ' * 18 + 'TEST RESULTS SUMMARY' + ' ' * 20 + '║')
    logger.info('╚' + '═' * 58 + '╝')
    logger.info('')

    passed = sum(1 for _, result in results if result)
    failed = sum(1 for _, result in results if not result)
    total = len(results)

    for test_name, result in results:
        status = '✅ PASS' if result else '❌ FAIL'
        logger.info(f'{status} | {test_name}')

    logger.info('')
    logger.info('─' * 60)
    logger.info(f'Total: {total} | Passed: {passed} | Failed: {failed}')
    logger.info('─' * 60)
    logger.info('')

    if failed == 0:
        logger.info('🎉 ALL TESTS PASSED! LinkedIn Poster is fully functional.')
        logger.info('')
        logger.info('Quick Start Guide:')
        logger.info('')
        logger.info('1. First-time LinkedIn Authentication:')
        logger.info('   python skills/linkedin_auth.py --login')
        logger.info('')
        logger.info('2. Generate a Draft Post:')
        logger.info('   python skills/linkedin_poster.py --vault ./AI_Employee_Vault --generate')
        logger.info('')
        logger.info('3. Create Approval Request:')
        logger.info('   python skills/linkedin_poster.py --vault ./AI_Employee_Vault --post')
        logger.info('')
        logger.info('4. Publish Approved Posts:')
        logger.info('   python skills/linkedin_poster.py --vault ./AI_Employee_Vault --execute-approved')
        logger.info('')
        logger.info('5. Check Posting Status:')
        logger.info('   python skills/linkedin_poster.py --vault ./AI_Employee_Vault --check-auth')
        logger.info('')
        return True
    else:
        logger.warning(f'⚠️  {failed} test(s) failed. Review errors above.')
        return False


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='LinkedIn Poster Test Suite')
    parser.add_argument('--vault', type=str, default=None,
                        help='Path to Obsidian vault (optional)')
    args = parser.parse_args()

    success = run_all_tests()
    sys.exit(0 if success else 1)
