#!/usr/bin/env python3
"""
Drishti System Verification Script
Performs comprehensive checks on all system components
"""

import sys
import os
import importlib.util
import subprocess
import json
from pathlib import Path

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BLUE}{text:^70}{Colors.END}")
    print(f"{Colors.BLUE}{'='*70}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

# Results tracking
results = {
    "passed": [],
    "failed": [],
    "warnings": [],
    "info": []
}

def check_python_version():
    """Check Python version"""
    print_header("Python Version Check")
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version.major == 3 and version.minor >= 10:
        print_success(f"Python {version_str} - OK (requires 3.10+)")
        results["passed"].append(f"Python {version_str}")
        return True
    else:
        print_error(f"Python {version_str} - FAILED (requires 3.10+)")
        results["failed"].append(f"Python version {version_str} < 3.10")
        return False

def check_backend_dependencies():
    """Check if backend dependencies are installed"""
    print_header("Backend Dependencies Check")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        backend_dir = Path(".")
    
    requirements_file = backend_dir / "requirements.txt"
    
    if not requirements_file.exists():
        print_error("requirements.txt not found")
        results["failed"].append("requirements.txt missing")
        return False
    
    # Read requirements
    with open(requirements_file) as f:
        requirements = [line.strip().split('==')[0].split('[')[0] 
                       for line in f if line.strip() and not line.startswith('#')]
    
    missing = []
    installed = []
    
    critical_packages = [
        'fastapi', 'uvicorn', 'psycopg2', 'mistralai', 'chromadb',
        'sentence_transformers', 'pandas', 'numpy', 'scikit-learn',
        'prophet', 'networkx', 'reportlab', 'python-jose', 'passlib',
        'python-dotenv', 'requests', 'pytest'
    ]
    
    for package in critical_packages:
        try:
            __import__(package.replace('-', '_'))
            installed.append(package)
            print_success(f"{package} - installed")
        except ImportError:
            missing.append(package)
            print_error(f"{package} - MISSING")
    
    if missing:
        print_warning(f"\nMissing packages: {', '.join(missing)}")
        print_info("Run: pip install -r requirements.txt")
        results["failed"].append(f"Missing packages: {', '.join(missing)}")
        return False
    else:
        print_success(f"\nAll {len(installed)} critical packages installed")
        results["passed"].append(f"All {len(installed)} backend packages installed")
        return True

def check_backend_imports():
    """Check if backend modules can be imported"""
    print_header("Backend Module Import Check")
    
    sys.path.insert(0, str(Path.cwd() / "backend"))
    
    modules_to_check = [
        'database',
        'mistral_client',
        'rag_pipeline',
        'translation',
        'routes.auth',
        'routes.chat',
        'routes.network',
        'routes.predictions',
        'routes.export',
        'middlewares.auth_middleware',
        'middlewares.rate_limiter',
        'utils.audit_logger',
        'utils.session_manager',
        'schemas.user_schema',
        'schemas.crime_schema'
    ]
    
    import_failures = []
    import_success = []
    
    for module_name in modules_to_check:
        try:
            module = importlib.import_module(module_name)
            print_success(f"{module_name} - OK")
            import_success.append(module_name)
        except Exception as e:
            print_error(f"{module_name} - FAILED: {str(e)[:60]}")
            import_failures.append(f"{module_name}: {str(e)[:60]}")
    
    if import_failures:
        results["failed"].extend(import_failures)
        return False
    else:
        results["passed"].append(f"All {len(import_success)} backend modules importable")
        return True

def check_fastapi_app():
    """Check if FastAPI app can be created"""
    print_header("FastAPI Application Check")
    
    try:
        sys.path.insert(0, str(Path.cwd() / "backend"))
        from main import app
        
        # Check if all routes are registered
        routes = [route.path for route in app.routes]
        expected_routes = ['/api/auth', '/api/chat', '/api/network', '/api/predictions', '/api/export']
        
        print_success("FastAPI app created successfully")
        print_info(f"Total routes: {len(routes)}")
        
        for expected in expected_routes:
            matching = [r for r in routes if r.startswith(expected)]
            if matching:
                print_success(f"  {expected} routes registered")
            else:
                print_error(f"  {expected} routes MISSING")
                results["failed"].append(f"Missing {expected} routes")
        
        results["passed"].append("FastAPI app initialization")
        return True
    except Exception as e:
        print_error(f"Failed to create FastAPI app: {e}")
        results["failed"].append(f"FastAPI app creation failed: {str(e)}")
        return False

def check_frontend_structure():
    """Check frontend file structure"""
    print_header("Frontend Structure Check")
    
    frontend_dir = Path("frontend")
    
    required_files = [
        "package.json",
        "tsconfig.json",
        "vite.config.ts",
        "src/App.tsx",
        "src/main.tsx",
        "src/pages/LoginPage.tsx",
        "src/pages/DashboardPage.tsx",
        "src/pages/NetworkPage.tsx",
        "src/pages/AuditPage.tsx",
        "src/components/Chat.tsx",
        "src/components/NetworkGraph.tsx",
        "src/components/PDFExport.tsx"
    ]
    
    missing_files = []
    
    for file_path in required_files:
        full_path = frontend_dir / file_path
        if full_path.exists():
            print_success(f"{file_path} - exists")
        else:
            print_error(f"{file_path} - MISSING")
            missing_files.append(file_path)
    
    if missing_files:
        results["failed"].append(f"Missing frontend files: {', '.join(missing_files)}")
        return False
    else:
        results["passed"].append(f"All {len(required_files)} frontend files exist")
        return True

def check_docker_files():
    """Check Docker configuration files"""
    print_header("Docker Configuration Check")
    
    docker_files = [
        "docker-compose.yml",
        "backend/Dockerfile",
        "frontend/Dockerfile",
        "frontend/nginx.conf"
    ]
    
    missing = []
    
    for file_path in docker_files:
        if Path(file_path).exists():
            print_success(f"{file_path} - exists")
        else:
            print_error(f"{file_path} - MISSING")
            missing.append(file_path)
    
    if missing:
        results["failed"].append(f"Missing Docker files: {', '.join(missing)}")
        return False
    else:
        results["passed"].append("All Docker configuration files exist")
        return True

def check_documentation():
    """Check documentation files"""
    print_header("Documentation Check")
    
    docs = [
        "README.md",
        "QUICKSTART.md",
        "ARCHITECTURE.md",
        "DEPLOYMENT.md",
        "TESTING.md",
        "PROJECT_STATUS.md",
        "DELIVERABLES_CHECKLIST.md",
        "EXECUTIVE_SUMMARY.md"
    ]
    
    missing = []
    
    for doc in docs:
        if Path(doc).exists():
            print_success(f"{doc} - exists")
        else:
            print_error(f"{doc} - MISSING")
            missing.append(doc)
    
    if missing:
        results["failed"].append(f"Missing docs: {', '.join(missing)}")
        return False
    else:
        results["passed"].append(f"All {len(docs)} documentation files exist")
        return True

def check_test_files():
    """Check test files"""
    print_header("Test Files Check")
    
    test_files = [
        "backend/tests/test_auth.py",
        "backend/tests/test_chat.py",
        "backend/tests/test_network.py",
        "backend/tests/test_predictions.py",
        "backend/tests/test_export.py",
        "backend/tests/test_integration.py",
        "backend/tests/conftest.py",
        "backend/pytest.ini"
    ]
    
    missing = []
    
    for test_file in test_files:
        if Path(test_file).exists():
            print_success(f"{test_file} - exists")
        else:
            print_error(f"{test_file} - MISSING")
            missing.append(test_file)
    
    if missing:
        results["failed"].append(f"Missing test files: {', '.join(missing)}")
        return False
    else:
        results["passed"].append(f"All {len(test_files)} test files exist")
        return True

def check_env_templates():
    """Check environment template files"""
    print_header("Environment Templates Check")
    
    env_files = [
        "backend/.env.example",
        "frontend/.env.example"
    ]
    
    missing = []
    
    for env_file in env_files:
        if Path(env_file).exists():
            print_success(f"{env_file} - exists")
        else:
            print_error(f"{env_file} - MISSING")
            missing.append(env_file)
    
    if missing:
        results["failed"].append(f"Missing env templates: {', '.join(missing)}")
        return False
    else:
        results["passed"].append("All environment templates exist")
        return True

def generate_summary():
    """Generate verification summary"""
    print_header("Verification Summary")
    
    total_checks = len(results["passed"]) + len(results["failed"]) + len(results["warnings"])
    passed_checks = len(results["passed"])
    failed_checks = len(results["failed"])
    warning_checks = len(results["warnings"])
    
    completion_percentage = (passed_checks / total_checks * 100) if total_checks > 0 else 0
    
    print(f"\n{Colors.BLUE}Total Checks:{Colors.END} {total_checks}")
    print(f"{Colors.GREEN}Passed:{Colors.END} {passed_checks}")
    print(f"{Colors.RED}Failed:{Colors.END} {failed_checks}")
    print(f"{Colors.YELLOW}Warnings:{Colors.END} {warning_checks}")
    print(f"\n{Colors.BLUE}Completion:{Colors.END} {completion_percentage:.1f}%\n")
    
    if results["failed"]:
        print(f"{Colors.RED}Failed Checks:{Colors.END}")
        for failure in results["failed"]:
            print(f"  • {failure}")
    
    if results["warnings"]:
        print(f"\n{Colors.YELLOW}Warnings:{Colors.END}")
        for warning in results["warnings"]:
            print(f"  • {warning}")
    
    return {
        "total": total_checks,
        "passed": passed_checks,
        "failed": failed_checks,
        "warnings": warning_checks,
        "completion_percentage": completion_percentage,
        "details": results
    }

def main():
    """Main verification function"""
    print(f"\n{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BLUE}{'DRISHTI SYSTEM VERIFICATION':^70}{Colors.END}")
    print(f"{Colors.BLUE}{'='*70}{Colors.END}")
    
    # Run all checks
    check_python_version()
    check_backend_dependencies()
    check_backend_imports()
    check_fastapi_app()
    check_frontend_structure()
    check_docker_files()
    check_documentation()
    check_test_files()
    check_env_templates()
    
    # Generate summary
    summary = generate_summary()
    
    # Return exit code based on failures
    return 0 if summary["failed"] == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
