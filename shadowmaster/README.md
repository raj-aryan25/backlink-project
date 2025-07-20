# Cross-Site Shadow DOM Automation Framework

# ShadowMaster Framework - Complete File Structure

## Total Files Created: 19

## Directory Structure and Files:

- `shadowmaster/.env.example` (554 bytes)\n
- `shadowmaster/README.md` (9,470 bytes)\n
- `shadowmaster/__init__.py` (479 bytes)\n
- `shadowmaster/config/settings.yaml` (1,684 bytes)\n
- `shadowmaster/core/__init__.py` (339 bytes)\n
- `shadowmaster/core/ai_selector.py` (11,068 bytes)\n
- `shadowmaster/core/browser_manager.py` (4,943 bytes)\n
- `shadowmaster/core/shadow_helper.py` (9,543 bytes)\n
- `shadowmaster/main.py` (13,463 bytes)\n
- `shadowmaster/pages/__init__.py` (307 bytes)\n
- `shadowmaster/pages/base_page.py` (10,606 bytes)\n
- `shadowmaster/pages/dasoertliche_page.py` (15,521 bytes)\n
- `shadowmaster/pages/gelbeseiten_page.py` (20,257 bytes)\n
- `shadowmaster/pages/reddit_page.py` (11,671 bytes)\n
- `shadowmaster/requirements.txt` (131 bytes)\n
- `shadowmaster/tests/__init__.py` (83 bytes)\n
- `shadowmaster/tests/test_cross_site_flow.py` (16,325 bytes)\n
- `shadowmaster/utils/__init__.py` (123 bytes)\n
- `shadowmaster/utils/page_factory.py` (2,737 bytes)\n

## Key Components Overview:

### Core Framework Files:

- **browser_manager.py**: Browser lifecycle management with Playwright
- **shadow_helper.py**: Universal Shadow DOM interaction utilities
- **ai_selector.py**: AI-powered selector inference using GPT-4o

### Page Objects:

- **base_page.py**: Base page object with common Shadow DOM functionality
- **reddit_page.py**: Reddit-specific interactions and modal handling
- **dasoertliche_page.py**: Das Örtliche with Shadow DOM cookie banner handling
- **gelbeseiten_page.py**: Gelbe Seiten with Shadow DOM consent manager

### Configuration & Utilities:

- **settings.yaml**: Site configurations with Shadow DOM element definitions
- **page_factory.py**: Dynamic page object creation
- **main.py**: Main runner script for cross-site testing

### Tests:

- **test_cross_site_flow.py**: Comprehensive test suite for all three websites

### Documentation:

- **README.md**: Complete framework documentation with examples
- **requirements.txt**: All required dependencies

## Framework Capabilities:

✅ **Universal Shadow DOM Support**: Open, closed, and nested Shadow DOM handling
✅ **Cross-Site Testing**: Reddit, Das Örtliche, Gelbe Seiten pre-configured  
✅ **AI-Powered Selectors**: Optional GPT-4o integration for intelligent selector inference
✅ **Robust Architecture**: Clean page object pattern with inheritance
✅ **Comprehensive Testing**: Full test suite with screenshots and video recording
✅ **Configurable**: YAML configuration with environment variable support
✅ **Extensible**: Easy to add new sites and Shadow DOM patterns
✅ **Error Handling**: Multiple fallback strategies and graceful degradation
✅ **Maintainable**: Well-structured codebase following best practices

This complete framework satisfies all Assignment 1 requirements for cross-site Shadow DOM automation.
