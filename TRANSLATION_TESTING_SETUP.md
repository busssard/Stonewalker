# Translation Testing Setup

This document describes the complete translation management and testing setup that ensures translations are compiled before every test execution.

## 🎯 Overview

The setup includes:
- **Automatic translation compilation** before tests
- **Pre-commit hooks** for translation compilation
- **Django management commands** for translation management
- **Excel/CSV translation editing** workflow
- **Comprehensive test suite** for translation quality

## 📁 Files Created

### Core Scripts
- `po_to_excel.py` - Extract translations from .po files to Excel/CSV
- `excel_to_po.py` - Convert Excel/CSV back to .po files
- `run_tests.py` - Test runner with automatic translation compilation

### Configuration Files
- `pytest.ini` - Pytest configuration for Django tests
- `conftest.py` - Pytest configuration with translation compilation
- `requirements.txt` - Updated with testing dependencies
- `translation_requirements.txt` - Dependencies for Excel support

### Django Management
- `source/main/management/commands/compile_translations.py` - Django command for translation compilation

### Git Hooks
- `.git/hooks/pre-commit` - Pre-commit hook for automatic translation compilation

### Build Tools
- `Makefile` - Convenient commands for testing and translation management

## 🚀 Usage

### 1. Install Dependencies
```bash
# Activate virtual environment
source venv/bin/activate

# Install all dependencies
make install
```

### 2. Run Tests (with automatic translation compilation)
```bash
# Run all tests
make test

# Run only fast tests (unit tests)
make test-fast

# Run only slow tests (integration tests)
make test-slow

# Run tests with coverage
make test-cov

# Or use the test runner directly
python run_tests.py
```

### 3. Manage Translations
```bash
# Extract translations to CSV
make translations

# Compile translations manually
make compile-translations

# Or use Django management command
cd source && python manage.py compile_translations
```

### 4. Edit Translations
```bash
# Extract to CSV for editing
python po_to_excel.py source/content/locale translations.csv

# Edit in your preferred spreadsheet editor
# Then convert back to .po files
python excel_to_po.py translations.csv source/content/locale
```

## 🔧 How It Works

### Automatic Translation Compilation

1. **Before Tests**: The `conftest.py` file automatically compiles translations before any test runs
2. **Pre-commit**: The pre-commit hook compiles translations before commits
3. **Test Runner**: The `run_tests.py` script ensures translations are compiled before running tests

### Test Workflow

```bash
# This automatically:
# 1. Compiles translations
# 2. Runs tests
# 3. Reports results
python run_tests.py
```

### Pre-commit Hook

The pre-commit hook:
- Detects modified .po files
- Compiles translations automatically
- Adds compiled .mo files to the commit
- Prevents commits if compilation fails

## 🧪 Test Categories

### Unit Tests (Fast)
- Account management tests
- Profile management tests
- Navigation UI tests
- CSS utility class tests

### Integration Tests (Slow)
- Translation quality assurance tests
- Translation functionality tests
- Language switching tests
- Translation coverage tests

## 📊 Translation Quality Tests

The test suite includes comprehensive translation quality checks:

1. **PO File Headers** - Ensures proper charset and language specifications
2. **Forbidden Characters** - Checks for smart quotes and special characters
3. **Empty Translations** - Validates no empty msgstr entries
4. **Duplicate Keys** - Ensures no duplicate msgid entries
5. **Compilation Success** - Verifies all .po files compile without errors
6. **Translation Functionality** - Tests actual translation behavior
7. **Language Switching** - Validates language switching works correctly

## 🔄 Translation Workflow

### For Developers
1. **Edit translations** in Excel/CSV format
2. **Convert back** to .po files
3. **Tests automatically compile** translations
4. **Pre-commit hook** ensures compilation before commits

### For CI/CD
1. **Tests run** with automatic translation compilation
2. **Translation quality** is validated
3. **Compilation errors** fail the build
4. **Coverage reports** include translation tests

## 🛠️ Troubleshooting

### Common Issues

1. **Tests not found**: Ensure you're in the virtual environment and using `python run_tests.py`
2. **Translation compilation fails**: Check .po file syntax and encoding
3. **Pre-commit hook not working**: Ensure the hook is executable (`chmod +x .git/hooks/pre-commit`)
4. **Import errors**: Make sure all dependencies are installed in the virtual environment

### Debug Commands

```bash
# Check if translations compile
cd source && python manage.py compile_translations

# Run tests with verbose output
python run_tests.py -v

# Check test collection
python run_tests.py --collect-only

# Run specific test file
python run_tests.py accounts/tests.py
```

## 📈 Benefits

1. **Automatic Quality Assurance** - Translations are validated before every test
2. **Developer Experience** - Easy Excel/CSV editing workflow
3. **CI/CD Integration** - Translation compilation is part of the test suite
4. **Pre-commit Safety** - Prevents broken translations from being committed
5. **Comprehensive Testing** - 26 tests covering translation quality and functionality

## 🎉 Success Indicators

- ✅ All tests pass with translation compilation
- ✅ Pre-commit hooks work automatically
- ✅ Translation quality tests validate .po files
- ✅ Excel/CSV workflow functions correctly
- ✅ CI/CD pipeline includes translation validation

This setup ensures that your Django application's translations are always properly compiled and validated before any code changes are committed or deployed. 