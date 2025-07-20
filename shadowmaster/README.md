# ShadowMaster Framework

A robust Playwright-based automation framework for cross-site Shadow DOM interaction and testing.

## Overview

ShadowMaster is a comprehensive Python framework designed to handle complex web automation scenarios involving Shadow DOM elements across multiple websites. The framework provides universal APIs for discovering, piercing, and interacting with Shadow DOM elements, with built-in fallback strategies and optional AI-powered selector inference.

## Features

- **Universal Shadow DOM Support**: Works with open, closed, and nested Shadow DOM structures
- **Cross-Site Compatibility**: Pre-configured for Reddit, Das Örtliche, and Gelbe Seiten with extensible architecture
- **AI-Powered Selectors**: Optional GPT-4o integration for intelligent selector inference
- **Robust Error Handling**: Multiple fallback strategies and graceful degradation
- **Comprehensive Testing**: Full test suite with screenshot capture and video recording
- **Configurable Architecture**: YAML-based configuration with environment variable support
- **Clean Page Objects**: Maintainable page object pattern with inheritance

## Architecture

```
shadowmaster/
├── config/
│   └── settings.yaml          # Site configurations and settings
├── core/
│   ├── browser_manager.py     # Browser lifecycle management
│   ├── shadow_helper.py       # Shadow DOM interaction utilities
│   └── ai_selector.py         # AI-powered selector inference
├── pages/
│   ├── base_page.py          # Base page object with common functionality
│   ├── reddit_page.py        # Reddit-specific interactions
│   ├── dasoertliche_page.py  # Das Örtliche with Shadow DOM handling
│   └── gelbeseiten_page.py   # Gelbe Seiten consent manager handling
├── tests/
│   └── test_cross_site_flow.py # Comprehensive test suite
├── utils/
│   └── page_factory.py       # Dynamic page object creation
├── main.py                   # Main runner script
└── requirements.txt          # Dependencies
```

## Quick Start

### Installation

1. **Clone and setup**:
   ```bash
   cd shadowmaster
   pip install -r requirements.txt
   playwright install chromium
   ```

2. **Configure environment** (optional):
   ```bash
   cp .env.example .env
   # Edit .env with your preferences
   ```

3. **Run basic tests**:
   ```bash
   python main.py --sites reddit dasoertliche gelbeseiten
   ```

### Running Tests

**All sites, basic scenarios**:
```bash
python main.py
```

**Specific sites with shadow discovery**:
```bash
python main.py --sites dasoertliche gelbeseiten --scenarios shadow_discovery interaction
```

**Visible mode (non-headless)**:
```bash
python main.py --visible --log-level DEBUG
```

**Using pytest directly**:
```bash
pytest tests/test_cross_site_flow.py -v
```

## Shadow DOM Capabilities

### Supported Shadow DOM Types

1. **Open Shadow Roots**: Direct access via `element.shadowRoot`
2. **Closed Shadow Roots**: JavaScript injection fallbacks
3. **Nested Shadow DOM**: Recursive traversal through multiple levels
4. **Dynamic Shadow Elements**: Runtime discovery and caching

### Shadow Helper API

```python
from core.shadow_helper import ShadowHelper

# Initialize
shadow_helper = ShadowHelper(page)

# Query shadow element
element = await shadow_helper.query_shadow(
    host_selector="consent-manager",
    inner_selector="button[data-accept='all']"
)

# Click shadow element
success = await shadow_helper.click_shadow_element(
    "cookie-banner", ".accept-button"
)

# Fill shadow input
await shadow_helper.fill_shadow_input(
    "search-widget", "input[name='query']", "search term"
)

# Discover all shadow hosts
hosts = await shadow_helper.discover_shadow_hosts()
```

### Nested Shadow DOM Example

```python
# Handle deeply nested shadow structures
shadow_path = [
    {"host": "parent-component"},
    {"host": "child-component", "target": "button.action"}
]

element = await shadow_helper.pierce_nested_shadow(shadow_path)
```

## Site-Specific Implementations

### Reddit Page Object

```python
reddit_page = RedditPage(page, config)

# Handle login modal
await reddit_page.open_login_modal()
await reddit_page.switch_to_signup()
await reddit_page.fill_signup_email("test@example.com")

# Handle popups
await reddit_page.handle_popups_and_overlays()
```

### Das Örtliche Page Object

```python
dasoertliche_page = DasOertlichePage(page, config)

# Handle shadow cookie banner
await dasoertliche_page.handle_cookie_banner()

# Perform search
await dasoertliche_page.perform_search("Müller", "Berlin")
results = await dasoertliche_page.extract_search_results()
```

### Gelbe Seiten Page Object

```python
gelbeseiten_page = GelbeseitenPage(page, config)

# Handle shadow consent manager
await gelbeseiten_page.handle_consent_manager()

# Business search
await gelbeseiten_page.perform_business_search("Restaurant", "München")
businesses = await gelbeseiten_page.extract_business_listings()
```

## AI-Powered Features (Optional)

Enable AI features by setting environment variables:

```bash
export OPENAI_API_KEY=your-api-key
export AI_ENABLED=true
```

### AI Selector Inference

```python
from core.ai_selector import get_ai_selector

ai_selector = get_ai_selector()
recommendation = await ai_selector.get_best_locator(
    html_snippet=page_html,
    target_description="close button for cookie banner"
)

print(f"Suggested selector: {recommendation.preferred}")
print(f"Confidence: {recommendation.confidence}")
```

### AI Shadow DOM Discovery

```python
shadow_paths = await ai_selector.infer_shadow_selectors(
    page_html, "consent management overlay"
)
```

## Configuration

### Site Configuration (settings.yaml)

```yaml
sites:
  example_site:
    url: "https://example.com"
    name: "Example Site"
    shadow_elements:
      - host: "consent-manager"
        inner: ".accept-all"
    locators:
      search_input: "input[name='query']"
      submit_btn: "button[type='submit']"

browser:
  headless: true
  timeout: 30000
  screenshots: true
  video_recording: true

ai:
  enabled: false
  model: "gpt-4o"
  cache_enabled: true
```

### Environment Variables

```bash
# Browser settings
HEADLESS=true
BROWSER_TIMEOUT=30000
SCREENSHOT_ENABLED=true

# AI features
OPENAI_API_KEY=your-key
AI_ENABLED=false

# Cache
REDIS_URL=redis://localhost:6379
```

## Extensibility

### Adding New Sites

1. **Create page object**:
   ```python
   # pages/newsite_page.py
   from pages.base_page import BasePage

   class NewSitePage(BasePage):
       async def handle_site_specific_element(self):
           return await self.shadow_helper.click_shadow_element(
               "site-banner", ".close-btn"
           )
   ```

2. **Register in factory**:
   ```python
   # utils/page_factory.py
   PageFactory.register_page_class("newsite", NewSitePage)
   ```

3. **Add configuration**:
   ```yaml
   # config/settings.yaml
   sites:
     newsite:
       url: "https://newsite.com"
       shadow_elements:
         - host: "site-banner"
           inner: ".close-btn"
   ```

### Custom Shadow DOM Patterns

```python
class CustomShadowHandler:
    async def handle_complex_shadow_pattern(self, page):
        # Custom logic for specific shadow DOM patterns
        await shadow_helper.pierce_nested_shadow([
            {"host": "app-root"},
            {"host": "modal-container", "target": ".modal-close"}
        ])
```

## Test Results

Tests generate comprehensive reports:

- **Screenshots**: `test-results/screenshots/`
- **Videos**: `test-results/videos/`
- **Traces**: `test-results/traces/`
- **Logs**: `test-results/logs/shadowmaster.log`
- **JSON Report**: `test-results/shadowmaster_results.json`
- **HTML Report**: `test-results/report.html`

### Sample Test Output

```json
{
  "total_sites": 3,
  "total_scenarios": 2,
  "summary": {
    "total_tests": 6,
    "passed": 6,
    "failed": 0,
    "success_rate": 1.0,
    "sites_tested": ["reddit", "dasoertliche", "gelbeseiten"]
  }
}
```

## Troubleshooting

### Common Issues

1. **Shadow element not found**:
   ```bash
   # Enable debug logging
   python main.py --log-level DEBUG
   ```

2. **Timeout errors**:
   ```yaml
   # Increase timeouts in settings.yaml
   browser:
     timeout: 60000
   ```

3. **Consent/Cookie issues**:
   ```python
   # Force consent handling
   await page_obj.handle_consent_manager()
   ```

### Debug Mode

```bash
# Run with full debugging
python main.py --visible --log-level DEBUG --sites dasoertliche
```

## Performance Optimization

1. **Browser reuse**: Single browser instance across tests
2. **Shadow root caching**: Cache discovered shadow roots
3. **Parallel execution**: Configure for parallel test runs
4. **AI caching**: Redis caching for AI responses

## Security Considerations

- Never commit API keys to repository
- Use environment variables for sensitive data
- Implement rate limiting for AI API calls
- Sanitize inputs in shadow DOM queries

## Contributing

1. Follow existing code patterns
2. Add tests for new functionality
3. Update documentation
4. Ensure Shadow DOM compatibility

## License

MIT License - see LICENSE file for details.

## Support

- Documentation: This README
- Issues: GitHub Issues
- Logs: Check `test-results/logs/` directory
- Screenshots: Available in `test-results/screenshots/`

---

**ShadowMaster Framework** - Robust Shadow DOM Automation for Modern Web Applications
