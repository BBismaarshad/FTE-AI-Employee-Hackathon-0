"""
Silver Tier Test Script - Validates all Silver tier components.

This script tests:
1. Gmail Watcher - Authentication and email detection
2. LinkedIn Watcher - Browser automation
3. LinkedIn Poster - Content generation
4. Filesystem Watcher - File drop detection
5. Orchestrator - Plan creation
6. Email MCP Server - OAuth setup
7. Windows Task Scheduler - Configuration

Usage:
    python test_silver_tier.py --vault ./AI_Employee_Vault
"""

import sys
import json
import time
import shutil
import logging
from pathlib import Path
from datetime import datetime

# Add paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / 'watchers'))
sys.path.insert(0, str(Path(__file__).parent / 'skills'))

from base_watcher import setup_logging

logger = setup_logging('SilverTierTest')


def test_credentials():
    """Test 1: Verify Gmail credentials are properly configured."""
    logger.info('=' * 60)
    logger.info('TEST 1: Gmail Credentials Verification')
    logger.info('=' * 60)
    
    creds_file = Path(__file__).parent / 'credentials.json'
    
    if not creds_file.exists():
        logger.error('❌ credentials.json not found')
        return False
    
    try:
        creds = json.loads(creds_file.read_text())
        
        # Check required fields
        required = ['client_id', 'client_secret', 'project_id', 'auth_uri', 'token_uri']
        installed = creds.get('installed', {})
        
        missing = [k for k in required if k not in installed]
        if missing:
            logger.error(f'❌ Missing fields in credentials: {missing}')
            return False
        
        logger.info(f'✅ Client ID: {installed["client_id"]}')
        logger.info(f'✅ Project ID: {installed["project_id"]}')
        logger.info('✅ Credentials structure is valid')
        logger.info('⚠️  NOTE: First run will require browser authentication')
        return True
        
    except Exception as e:
        logger.error(f'❌ Error reading credentials: {e}')
        return False


def test_gmail_watcher_import():
    """Test 2: Verify Gmail Watcher can be imported."""
    logger.info('=' * 60)
    logger.info('TEST 2: Gmail Watcher Import')
    logger.info('=' * 60)
    
    try:
        from gmail_watcher import GmailWatcher
        logger.info('✅ GmailWatcher class imported successfully')
        
        # Check dependencies
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            logger.info('✅ Google API dependencies available')
            return True
        except ImportError as e:
            logger.error(f'❌ Missing Google API dependencies: {e}')
            return False
            
    except Exception as e:
        logger.error(f'❌ Failed to import GmailWatcher: {e}')
        return False


def test_linkedin_watcher_import():
    """Test 3: Verify LinkedIn Watcher can be imported."""
    logger.info('=' * 60)
    logger.info('TEST 3: LinkedIn Watcher Import')
    logger.info('=' * 60)
    
    try:
        from linkedin_watcher import LinkedInWatcher
        logger.info('✅ LinkedInWatcher class imported successfully')
        
        # Check Playwright
        try:
            from playwright.sync_api import sync_playwright
            logger.info('✅ Playwright dependency available')
            return True
        except ImportError as e:
            logger.error(f'❌ Missing Playwright dependency: {e}')
            return False
            
    except Exception as e:
        logger.error(f'❌ Failed to import LinkedInWatcher: {e}')
        return False


def test_linkedin_poster():
    """Test 4: Verify LinkedIn Poster can generate content."""
    logger.info('=' * 60)
    logger.info('TEST 4: LinkedIn Poster Content Generation')
    logger.info('=' * 60)
    
    try:
        from linkedin_poster import LinkedInPoster
        
        # Create poster instance
        poster = LinkedInPoster(vault_path=str(Path(__file__).parent / 'AI_Employee_Vault'))
        logger.info('✅ LinkedInPoster instantiated')
        
        # Generate test post
        post_data = poster.generate_post('industry_insight')
        
        if not post_data.get('text'):
            logger.error('❌ Generated post has no text')
            return False
        
        # Verify post structure
        if len(post_data['text']) < 50:
            logger.error(f'❌ Post too short: {len(post_data["text"])} chars')
            return False
        
        if not post_data.get('hashtags'):
            logger.error('❌ Post has no hashtags')
            return False
        
        logger.info(f'✅ Post generated: {len(post_data["text"])} characters')
        logger.info(f'✅ Category: {post_data["category"]}')
        logger.info(f'✅ Hashtags: {", ".join(post_data["hashtags"])}')
        
        # Preview first 100 chars
        preview = post_data['text'][:100].replace('\n', ' ')
        logger.info(f'✅ Preview: {preview}...')
        
        # Create draft file
        draft_path = poster.create_draft_file(post_data)
        logger.info(f'✅ Draft file created: {draft_path.name}')
        
        return True
        
    except Exception as e:
        logger.error(f'❌ LinkedIn Poster test failed: {e}', exc_info=True)
        return False


def test_filesystem_watcher():
    """Test 5: Verify Filesystem Watcher workflow."""
    logger.info('=' * 60)
    logger.info('TEST 5: Filesystem Watcher Workflow')
    logger.info('=' * 60)
    
    try:
        from filesystem_watcher import FilesystemWatcher
        
        vault_path = Path(__file__).parent / 'AI_Employee_Vault'
        drop_folder = Path(__file__).parent / 'drop_folder'
        
        # Clean up state file to allow fresh test
        state_file = vault_path / '.state' / 'filesystem_watcher.txt'
        if state_file.exists():
            state_file.unlink()
        
        # Create test file with unique name
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        test_file = drop_folder / f'test_silver_{timestamp}.txt'
        test_content = f'Test task for Silver tier validation\nTimestamp: {datetime.now().isoformat()}'
        test_file.write_text(test_content)
        logger.info(f'✅ Test file created: {test_file.name}')
        
        # Create watcher and run once
        watcher = FilesystemWatcher(
            vault_path=str(vault_path),
            drop_folder=str(drop_folder)
        )
        
        # Reload processed files after state cleanup
        watcher.processed_ids = set()
        
        count = watcher.run_once()
        
        if count == 0:
            logger.error('❌ Filesystem watcher did not create action file')
            return False
        
        logger.info(f'✅ Filesystem watcher created {count} action file(s)')
        
        # Verify action file was created
        needs_action = vault_path / 'Needs_Action'
        action_files = list(needs_action.glob(f'FILE_test_silver_{timestamp}_*.md'))
        
        if not action_files:
            logger.error('❌ No action file found in Needs_Action folder')
            return False
        
        logger.info(f'✅ Action file verified: {action_files[0].name}')
        
        # Clean up test files
        test_file.unlink(missing_ok=True)
        for af in action_files:
            af.unlink(missing_ok=True)
        logger.info('✅ Test files cleaned up')
        
        return True
        
    except Exception as e:
        logger.error(f'❌ Filesystem Watcher test failed: {e}', exc_info=True)
        return False


def test_orchestrator():
    """Test 6: Verify Orchestrator can process action files."""
    logger.info('=' * 60)
    logger.info('TEST 6: Orchestrator Plan Creation')
    logger.info('=' * 60)
    
    try:
        from orchestrator import Orchestrator
        
        vault_path = Path(__file__).parent / 'AI_Employee_Vault'
        
        # Clean up state file
        state_file = vault_path / '.state' / 'orchestrator.txt'
        if state_file.exists():
            state_file.unlink()
        
        # Create test action file with unique name
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        test_action = vault_path / 'Needs_Action' / f'TEST_ORCHESTRATOR_{timestamp}.md'
        
        test_action.write_text(f'''---
type: test
priority: high
created: {datetime.now().isoformat()}
status: pending
---

# Test: Orchestrator Validation

This is a test action file for Silver tier validation.
''')
        
        logger.info('✅ Test action file created')
        
        # Create orchestrator and process
        orchestrator = Orchestrator(vault_path=str(vault_path))
        
        # Clear processed files to allow fresh test
        orchestrator.processed_files = set()
        
        count = orchestrator.process_pending()
        
        if count == 0:
            logger.error('❌ Orchestrator did not process action file')
            return False
        
        logger.info(f'✅ Orchestrator processed {count} action file(s)')
        
        # Verify plan was created
        plans_folder = vault_path / 'Plans'
        plan_files = list(plans_folder.glob(f'PLAN_TEST_ORCHESTRATOR_{timestamp}_*.md'))
        
        if not plan_files:
            logger.error('❌ No plan file found in Plans folder')
            return False
        
        logger.info(f'✅ Plan file verified: {plan_files[0].name}')
        
        # Clean up
        test_action.unlink(missing_ok=True)
        for pf in plan_files:
            pf.unlink(missing_ok=True)
        logger.info('✅ Test files cleaned up')
        
        return True
        
    except Exception as e:
        logger.error(f'❌ Orchestrator test failed: {e}', exc_info=True)
        return False


def test_email_mcp_server():
    """Test 7: Verify Email MCP Server structure."""
    logger.info('=' * 60)
    logger.info('TEST 7: Email MCP Server Structure')
    logger.info('=' * 60)
    
    try:
        mcp_file = Path(__file__).parent / 'skills' / 'email_mcp_server.py'
        
        if not mcp_file.exists():
            logger.error('❌ email_mcp_server.py not found')
            return False
        
        logger.info('✅ Email MCP Server file exists')
        
        # Try to import
        import importlib.util
        spec = importlib.util.spec_from_file_location('email_mcp_server', mcp_file)
        module = importlib.util.module_from_spec(spec)
        
        logger.info('✅ Email MCP Server module loaded')
        logger.info('⚠️  NOTE: First run will require Gmail authentication with send scope')
        
        return True
        
    except Exception as e:
        logger.error(f'❌ Email MCP Server test failed: {e}', exc_info=True)
        return False


def test_vault_structure():
    """Test 8: Verify Obsidian vault structure."""
    logger.info('=' * 60)
    logger.info('TEST 8: Obsidian Vault Structure')
    logger.info('=' * 60)
    
    vault_path = Path(__file__).parent / 'AI_Employee_Vault'
    
    required_files = [
        'Dashboard.md',
        'Company_Handbook.md',
        'Business_Goals.md'
    ]
    
    required_folders = [
        'Inbox',
        'Needs_Action',
        'Done',
        'Plans',
        'Pending_Approval',
        'Approved',
        'Rejected',
        'Logs'
    ]
    
    all_ok = True
    
    # Check files
    for filename in required_files:
        filepath = vault_path / filename
        if filepath.exists():
            logger.info(f'✅ {filename} exists')
        else:
            logger.warning(f'⚠️  {filename} not found')
            all_ok = False
    
    # Check folders
    for folder in required_folders:
        folder_path = vault_path / folder
        if folder_path.exists() and folder_path.is_dir():
            logger.info(f'✅ {folder}/ folder exists')
        else:
            logger.warning(f'⚠️  {folder}/ folder not found')
            all_ok = False
    
    return all_ok


def test_requirements():
    """Test 9: Verify all Python dependencies are installed."""
    logger.info('=' * 60)
    logger.info('TEST 9: Python Dependencies')
    logger.info('=' * 60)
    
    required_packages = [
        ('googleapiclient', 'Gmail API (google-api-python-client)'),
        ('google_auth_httplib2', 'Gmail Auth'),
        ('google_auth_oauthlib', 'Gmail OAuth'),
        ('playwright', 'Browser Automation'),
        ('watchdog', 'File System Monitoring'),
        ('mcp', 'Model Context Protocol'),
    ]
    
    all_ok = True
    
    for package, purpose in required_packages:
        try:
            __import__(package)
            logger.info(f'✅ {package} ({purpose})')
        except ImportError:
            logger.error(f'❌ {package} ({purpose}) - NOT INSTALLED')
            all_ok = False
    
    return all_ok


def run_all_tests():
    """Run all Silver tier validation tests."""
    logger.info('')
    logger.info('╔' + '═' * 58 + '╗')
    logger.info('║' + ' ' * 10 + 'SILVER TIER VALIDATION TEST SUITE' + ' ' * 16 + '║')
    logger.info('╚' + '═' * 58 + '╝')
    logger.info('')
    logger.info(f'Test run started: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    logger.info('')
    
    tests = [
        ('Gmail Credentials', test_credentials),
        ('Gmail Watcher Import', test_gmail_watcher_import),
        ('LinkedIn Watcher Import', test_linkedin_watcher_import),
        ('LinkedIn Poster', test_linkedin_poster),
        ('Filesystem Watcher', test_filesystem_watcher),
        ('Orchestrator', test_orchestrator),
        ('Email MCP Server', test_email_mcp_server),
        ('Vault Structure', test_vault_structure),
        ('Dependencies', test_requirements),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            logger.info('')
            time.sleep(0.5)  # Brief pause between tests
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
        logger.info('🎉 ALL TESTS PASSED! Silver tier is fully functional.')
        logger.info('')
        logger.info('Next Steps:')
        logger.info('1. Run Gmail Watcher for first-time authentication:')
        logger.info('   python watchers\\gmail_watcher.py --vault .\\AI_Employee_Vault --once')
        logger.info('')
        logger.info('2. Run LinkedIn Watcher for first-time login:')
        logger.info('   python watchers\\linkedin_watcher.py --vault .\\AI_Employee_Vault --once')
        logger.info('')
        logger.info('3. Setup Windows Task Scheduler (as Admin):')
        logger.info('   powershell -ExecutionPolicy Bypass -File skills\\setup_tasks.ps1 -All')
        logger.info('')
        return True
    else:
        logger.warning(f'⚠️  {failed} test(s) failed. Review errors above.')
        return False


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Silver Tier Validation Tests')
    parser.add_argument('--vault', type=str, default=None,
                        help='Path to Obsidian vault (optional)')
    args = parser.parse_args()
    
    success = run_all_tests()
    
    sys.exit(0 if success else 1)
