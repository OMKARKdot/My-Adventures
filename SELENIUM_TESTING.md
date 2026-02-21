# 🧪 Selenium Testing for My Adventures

This directory contains a complete Dockerized Selenium testing suite for the My Adventures waterpark website.

## 📁 Files Overview

| File | Description |
|------|-------------|
| `test.py` | Main Selenium test suite (36 comprehensive tests) |
| `Dockerfile.selenium` | Docker image for running tests with Chrome |
| `requirements.txt` | Python dependencies |
| `docker-compose.test.yml` | Orchestrates web server and test runner |
| `SELENIUM_TESTING.md` | This documentation |

## 🚀 Quick Start

### Option 1: Using Docker Compose (Recommended)

Run everything with one command:

```bash
# Build and run tests
docker-compose -f docker-compose.test.yml up --build

# Clean up after tests
docker-compose -f docker-compose.test.yml down
```

### Option 2: Manual Docker Build

```bash
# 1. Build the test image
docker build -f Dockerfile.selenium -t my-adventures-selenium .

# 2. Run tests (assumes website is running on localhost:9090)
docker run --network=host -e BASE_URL=http://localhost:9090 my-adventures-selenium

# Or with custom URL
docker run -e BASE_URL=http://your-website-url my-adventures-selenium
```

### Option 3: Local Development (No Docker)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Make sure Chrome is installed on your system

# 3. Run tests
python test.py

# Or with specific URL
BASE_URL=http://localhost:9090 python test.py
```

## 🧪 Test Coverage

The test suite includes **36 comprehensive tests** covering:

### Index Page Tests (20 tests)
- ✅ Homepage loads successfully
- ✅ Hero section visibility and content
- ✅ Navigation links presence
- ✅ Deals banner display
- ✅ Parks section rendering
- ✅ Park cards (20 parks)
- ✅ Park card details (name, location, price)
- ✅ Modal functionality (open/close)
- ✅ Modal sections (description, timings, packages, offers, map)
- ✅ Modal interactions (click, escape, overlay)
- ✅ Splash highlights
- ✅ Intro section content
- ✅ Special offers section
- ✅ Contact section
- ✅ Search box functionality
- ✅ Filter buttons and functionality

### Page Tests (7 tests)
- ✅ Login page
- ✅ Booking page
- ✅ Contact page
- ✅ Blog page
- ✅ Portfolio page
- ✅ Payment page

### Navigation Tests (4 tests)
- ✅ Book Now navigation
- ✅ Log In navigation
- ✅ Modal Book Now button
- ✅ Cross-page navigation

### Technical Tests (5 tests)
- ✅ Responsive design (multiple viewport sizes)
- ✅ Image loading
- ✅ JavaScript execution
- ✅ Performance check
- ✅ Headless Chrome compatibility

## 🔧 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BASE_URL` | `http://localhost:9090` | Website URL to test |
| `HEADLESS` | `true` | Run Chrome in headless mode |
| `CHROME_BIN` | Auto-detected | Path to Chrome binary |
| `CHROMEDRIVER_PATH` | Auto-detected | Path to ChromeDriver |

## 🐳 Docker Architecture

```
┌─────────────────────────────────────────┐
│         Docker Network                  │
│  ┌─────────────┐    ┌───────────────┐  │
│  │   web       │◄───│ selenium-tests│  │
│  │  (nginx)    │    │  (Python +    │  │
│  │  Port 9090  │    │   Chrome)     │  │
│  └─────────────┘    └───────────────┘  │
│       Website           Test Runner     │
└─────────────────────────────────────────┘
```

## 📊 Test Output Example

```
test_01_homepage_loads (__main__.TestMyAdventures) ... ✅ Homepage loaded successfully
ok
test_02_hero_section_visible (__main__.TestMyAdventures) ... ✅ Hero section visible with correct title
ok
...
test_36_performance_check (__main__.TestMyAdventures) ... ✅ Page load time: 1.23s
ok

============================================================
TEST SUMMARY
============================================================
Tests Run: 36
Successes: 36
Failures: 0
Errors: 0
Skipped: 0
============================================================
```

## 🛠️ Troubleshooting

### Chrome/Driver Version Mismatch
The Dockerfile automatically installs matching Chrome and ChromeDriver versions.

### Website Not Reachable
Ensure the website is running before tests:
```bash
# Start website locally
docker run -p 9090:80 -v $(pwd):/usr/share/nginx/html nginx:alpine
```

### Tests Failing in Docker
Check logs:
```bash
docker logs my-adventures-tests
```

### Slow Tests
Tests include intentional waits for animations and page loads. Adjust `time.sleep()` values in `test.py` if needed.

## 📝 Adding New Tests

To add a new test, add a method to the `TestMyAdventures` class:

```python
def test_37_new_feature(self):
    """Test description"""
    self.driver.get(BASE_URL)
    # Your test code here
    self.assertTrue(condition)
    print("✅ New feature works")
```

Follow the naming convention: `test_XX_description`

## 🎯 CI/CD Integration

### GitHub Actions Example
```yaml
name: Selenium Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Selenium Tests
        run: |
          docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
```

### GitLab CI Example
```yaml
selenium-tests:
  script:
    - docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
```

## 📚 Additional Resources

- [Selenium Python Docs](https://selenium-python.readthedocs.io/)
- [ChromeDriver Downloads](https://chromedriver.chromium.org/downloads)
- [Docker Selenium Images](https://github.com/SeleniumHQ/docker-selenium)

---

**Happy Testing! 🎢💦**
