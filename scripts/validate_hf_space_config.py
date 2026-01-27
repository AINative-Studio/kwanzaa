#!/usr/bin/env python3
"""
Validate HuggingFace Space configuration before pushing

This script checks for common issues that cause build failures:
- Conflicting requirements.txt file
- Incorrect file count
- Missing required files
- Dependency version conflicts
- Base image issues

Usage:
    python3 scripts/validate_hf_space_config.py /path/to/space/directory
"""

import sys
import os
import re
from pathlib import Path
from typing import List, Tuple, Dict

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")

def print_success(text: str):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_error(text: str):
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def check_file_count(space_dir: Path) -> Tuple[bool, List[str]]:
    """Check that Space has exactly 5 files"""
    files = [f.name for f in space_dir.iterdir() if f.is_file()]

    expected_files = {
        'Dockerfile',
        'app.py',
        'train.py',
        'README.md',
        '.gitattributes'
    }

    if len(files) != 5:
        return False, files

    missing = expected_files - set(files)
    extra = set(files) - expected_files

    if missing or extra:
        return False, files

    return True, files

def check_requirements_txt(space_dir: Path) -> bool:
    """Check for conflicting requirements.txt file"""
    req_file = space_dir / 'requirements.txt'
    return not req_file.exists()

def check_dockerfile(space_dir: Path) -> Tuple[bool, List[str]]:
    """Validate Dockerfile configuration"""
    dockerfile = space_dir / 'Dockerfile'
    if not dockerfile.exists():
        return False, ["Dockerfile not found"]

    content = dockerfile.read_text()
    issues = []

    # Check base image
    if ':latest' in content:
        issues.append("Base image uses ':latest' tag (should be pinned)")

    if 'nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04' not in content:
        issues.append("Base image should be nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04")

    # Check for curl (needed for health check)
    if 'curl' not in content:
        issues.append("curl not installed (needed for HEALTHCHECK)")

    # Check PyTorch CUDA index
    if '--index-url https://download.pytorch.org/whl/cu118' not in content:
        issues.append("PyTorch should use CUDA 11.8 index URL")

    # Check health check
    if 'HEALTHCHECK' not in content:
        issues.append("Missing HEALTHCHECK directive")

    # Check port exposure
    if 'EXPOSE 7860' not in content:
        issues.append("Port 7860 not exposed")

    # Check huggingface_hub version
    if 'huggingface_hub==0.20.0' in content:
        issues.append("CRITICAL: huggingface_hub==0.20.0 incompatible with Gradio 5.10.0 (use 0.25.1)")

    if 'huggingface_hub==0.25.1' not in content:
        issues.append("huggingface_hub should be version 0.25.1 for Gradio compatibility")

    # Check Gradio version
    if 'gradio==5.10.0' not in content:
        issues.append("Gradio should be version 5.10.0")

    # Check dependency order (huggingface_hub should be first)
    hf_hub_match = re.search(r'huggingface_hub==', content)
    transformers_match = re.search(r'transformers==', content)

    if hf_hub_match and transformers_match:
        if hf_hub_match.start() > transformers_match.start():
            issues.append("huggingface_hub should be installed BEFORE transformers")

    return len(issues) == 0, issues

def check_readme(space_dir: Path) -> Tuple[bool, List[str]]:
    """Validate README.md YAML frontmatter"""
    readme = space_dir / 'README.md'
    if not readme.exists():
        return False, ["README.md not found"]

    content = readme.read_text()
    issues = []

    required_yaml = [
        'title:',
        'sdk: docker',
        'app_port: 7860'
    ]

    for item in required_yaml:
        if item not in content:
            issues.append(f"Missing YAML: {item}")

    return len(issues) == 0, issues

def check_app_py(space_dir: Path) -> Tuple[bool, List[str]]:
    """Validate app.py Gradio configuration"""
    app_py = space_dir / 'app.py'
    if not app_py.exists():
        return False, ["app.py not found"]

    content = app_py.read_text()
    issues = []

    # Check for Gradio 6.0 incompatibilities
    if 'show_api=False' in content:
        issues.append("Remove 'show_api=False' (not compatible with Gradio 5.10.0)")

    if 'theme=' in content and 'gr.Blocks(' in content:
        issues.append("Remove 'theme' parameter from gr.Blocks() (Gradio 5.10.0)")

    # Check for proper error handling
    if 'try:' not in content or 'except' not in content:
        issues.append("Missing error handling in training function")

    # Check for streaming output
    if 'yield' not in content:
        issues.append("Training function should yield output for streaming")

    return len(issues) == 0, issues

def check_train_py(space_dir: Path) -> Tuple[bool, List[str]]:
    """Validate train.py configuration"""
    train_py = space_dir / 'train.py'
    if not train_py.exists():
        return False, ["train.py not found"]

    content = train_py.read_text()
    issues = []

    # Check for HF_TOKEN usage
    if 'os.getenv("HF_TOKEN")' not in content and 'os.getenv(\'HF_TOKEN\')' not in content:
        issues.append("Should use os.getenv('HF_TOKEN') for authentication")

    # Check for push_to_hub
    if 'push_to_hub' not in content:
        issues.append("Missing push_to_hub configuration")

    # Check for dataset loading
    if 'load_dataset' not in content:
        issues.append("Missing dataset loading")

    return len(issues) == 0, issues

def validate_space(space_dir: str) -> bool:
    """Run all validation checks"""
    space_path = Path(space_dir)

    if not space_path.exists():
        print_error(f"Directory not found: {space_dir}")
        return False

    if not space_path.is_dir():
        print_error(f"Not a directory: {space_dir}")
        return False

    print_header("HuggingFace Space Configuration Validator")
    print(f"Validating: {space_path.absolute()}\n")

    all_passed = True

    # Check 1: File count
    print(f"{Colors.BOLD}1. Checking file count...{Colors.RESET}")
    passed, files = check_file_count(space_path)
    if passed:
        print_success(f"Exactly 5 files present: {', '.join(files)}")
    else:
        print_error(f"Expected 5 files, found {len(files)}: {', '.join(files)}")
        all_passed = False

    # Check 2: No requirements.txt
    print(f"\n{Colors.BOLD}2. Checking for requirements.txt conflict...{Colors.RESET}")
    passed = check_requirements_txt(space_path)
    if passed:
        print_success("No requirements.txt file (correct for Docker SDK)")
    else:
        print_error("CRITICAL: requirements.txt found - DELETE IT (Docker SDK uses Dockerfile only)")
        all_passed = False

    # Check 3: Dockerfile
    print(f"\n{Colors.BOLD}3. Validating Dockerfile...{Colors.RESET}")
    passed, issues = check_dockerfile(space_path)
    if passed:
        print_success("Dockerfile configuration valid")
    else:
        print_error(f"Dockerfile has {len(issues)} issue(s):")
        for issue in issues:
            print(f"   - {issue}")
        all_passed = False

    # Check 4: README.md
    print(f"\n{Colors.BOLD}4. Validating README.md...{Colors.RESET}")
    passed, issues = check_readme(space_path)
    if passed:
        print_success("README.md YAML frontmatter valid")
    else:
        print_error(f"README.md has {len(issues)} issue(s):")
        for issue in issues:
            print(f"   - {issue}")
        all_passed = False

    # Check 5: app.py
    print(f"\n{Colors.BOLD}5. Validating app.py...{Colors.RESET}")
    passed, issues = check_app_py(space_path)
    if passed:
        print_success("app.py configuration valid")
    else:
        print_error(f"app.py has {len(issues)} issue(s):")
        for issue in issues:
            print(f"   - {issue}")
        all_passed = False

    # Check 6: train.py
    print(f"\n{Colors.BOLD}6. Validating train.py...{Colors.RESET}")
    passed, issues = check_train_py(space_path)
    if passed:
        print_success("train.py configuration valid")
    else:
        print_warning(f"train.py has {len(issues)} suggestion(s):")
        for issue in issues:
            print(f"   - {issue}")

    # Final result
    print_header("Validation Result")
    if all_passed:
        print_success("ALL CHECKS PASSED - Safe to push to HuggingFace Space")
        return True
    else:
        print_error("VALIDATION FAILED - Fix issues before pushing")
        print("\nCommon fixes:")
        print("  - Delete requirements.txt: rm /path/to/space/requirements.txt")
        print("  - Update huggingface_hub: Change to version 0.25.1 in Dockerfile")
        print("  - Remove Gradio 6.0 parameters: show_api, theme in Blocks()")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/validate_hf_space_config.py /path/to/space/directory")
        print("\nExample:")
        print("  python3 scripts/validate_hf_space_config.py /tmp/kwanzaa-training")
        sys.exit(1)

    space_dir = sys.argv[1]
    success = validate_space(space_dir)
    sys.exit(0 if success else 1)
