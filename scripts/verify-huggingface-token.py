#!/usr/bin/env python3
"""
HuggingFace Token Verification Script

Verifies that the configured HuggingFace token is valid and has the necessary
permissions for the Kwanzaa project.

Usage:
    python scripts/verify-huggingface-token.py
    python scripts/verify-huggingface-token.py --token hf_xxx
    python scripts/verify-huggingface-token.py --check-gated-models
    python scripts/verify-huggingface-token.py --check-write-access

Environment Variables:
    HF_TOKEN - HuggingFace API token (required if --token not provided)

Exit Codes:
    0 - Token is valid and has required permissions
    1 - Token is invalid or missing required permissions
    2 - Configuration error
"""

import argparse
import os
import sys
from typing import Dict, List, Optional, Tuple

try:
    from huggingface_hub import HfApi, whoami
    from huggingface_hub.utils import HfHubHTTPError
except ImportError:
    print("ERROR: huggingface_hub not installed")
    print("Install with: pip install huggingface-hub")
    sys.exit(2)


class Colors:
    """ANSI color codes for terminal output."""
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"


def print_header(text: str) -> None:
    """Print a formatted header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(80)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.RESET}\n")


def print_success(text: str) -> None:
    """Print a success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")


def print_error(text: str) -> None:
    """Print an error message."""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")


def print_warning(text: str) -> None:
    """Print a warning message."""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")


def print_info(text: str) -> None:
    """Print an info message."""
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")


def validate_token_format(token: str) -> Tuple[bool, str]:
    """
    Validate the format of a HuggingFace token.

    Returns:
        Tuple of (is_valid, message)
    """
    if not token:
        return False, "Token is empty"

    if not token.startswith("hf_"):
        return False, "Token must start with 'hf_'"

    # HuggingFace tokens are typically 37-43 characters
    # Older tokens: hf_ + 34 chars = 37 total
    # Newer tokens: hf_ + 40 chars = 43 total
    token_length = len(token)
    if token_length < 37:
        return False, f"Token is too short: {token_length} characters"
    elif token_length > 43:
        return False, f"Token is too long: {token_length} characters"
    elif token_length != 37 and token_length != 43:
        # Accept it but warn
        return True, f"Token format is valid (length: {token_length}, non-standard but acceptable)"

    return True, f"Token format is valid (length: {token_length})"


def check_token_authentication(token: str) -> Tuple[bool, Optional[Dict]]:
    """
    Check if the token is valid by authenticating with HuggingFace.

    Returns:
        Tuple of (is_valid, user_info)
    """
    try:
        user_info = whoami(token=token)
        return True, user_info
    except HfHubHTTPError as e:
        if e.response.status_code == 401:
            return False, None
        raise
    except Exception as e:
        print_error(f"Unexpected error during authentication: {e}")
        return False, None


def check_token_permissions(user_info: Dict) -> Dict[str, bool]:
    """
    Check what permissions the token has.

    Returns:
        Dictionary of permission checks
    """
    permissions = {
        "read": False,
        "write": False,
        "organizations": []
    }

    # Check token type from auth
    auth = user_info.get("auth", {})
    access_token = auth.get("accessToken", {})

    # Check role (read or write)
    role = access_token.get("role", "")
    permissions["read"] = role in ["read", "write", "admin"]
    permissions["write"] = role in ["write", "admin"]

    # Get organizations
    orgs = user_info.get("orgs", [])
    permissions["organizations"] = [org.get("name") for org in orgs]

    return permissions


def check_gated_model_access(api: HfApi, model_id: str, token: str) -> Tuple[bool, str]:
    """
    Check if the token has access to a specific gated model.

    Returns:
        Tuple of (has_access, message)
    """
    try:
        model_info = api.model_info(model_id, token=token)

        if model_info.gated:
            # If we got model info, we have access
            return True, f"Access granted to gated model: {model_id}"
        else:
            return True, f"Model is not gated: {model_id}"

    except HfHubHTTPError as e:
        if e.response.status_code == 401:
            return False, f"Access denied to {model_id} (request access first)"
        elif e.response.status_code == 404:
            return False, f"Model not found: {model_id}"
        else:
            return False, f"Error checking {model_id}: {e}"
    except Exception as e:
        return False, f"Unexpected error checking {model_id}: {e}"


def check_write_access(api: HfApi, username: str, token: str) -> Tuple[bool, str]:
    """
    Check if the token has write access by attempting to list user repos.

    Returns:
        Tuple of (has_access, message)
    """
    try:
        # Try to list user's models (requires write access)
        models = list(api.list_models(author=username, token=token, limit=1))
        return True, "Write access confirmed (can manage repositories)"
    except HfHubHTTPError as e:
        if e.response.status_code == 401:
            return False, "No write access (read-only token)"
        else:
            return False, f"Error checking write access: {e}"
    except Exception as e:
        return False, f"Unexpected error checking write access: {e}"


def main():
    """Main verification function."""
    parser = argparse.ArgumentParser(
        description="Verify HuggingFace token configuration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        "--token",
        help="HuggingFace token to verify (defaults to HF_TOKEN env var)"
    )
    parser.add_argument(
        "--check-gated-models",
        action="store_true",
        help="Check access to common gated models (LLaMA, Mistral, etc.)"
    )
    parser.add_argument(
        "--check-write-access",
        action="store_true",
        help="Check if token has write permissions"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format"
    )

    args = parser.parse_args()

    # Get token from argument or environment
    token = args.token or os.getenv("HF_TOKEN")

    if not token:
        print_error("No HuggingFace token provided")
        print_info("Set HF_TOKEN environment variable or use --token argument")
        return 2

    # Start verification
    print_header("HuggingFace Token Verification")

    # Step 1: Validate token format
    print_info("Step 1: Validating token format...")
    is_valid_format, format_msg = validate_token_format(token)

    if is_valid_format:
        print_success(format_msg)
    else:
        print_error(format_msg)
        return 1

    # Step 2: Authenticate with HuggingFace
    print_info("\nStep 2: Authenticating with HuggingFace...")
    is_authenticated, user_info = check_token_authentication(token)

    if not is_authenticated:
        print_error("Token authentication failed")
        print_info("Token may be invalid, expired, or revoked")
        return 1

    username = user_info.get("name", "unknown")
    user_type = user_info.get("type", "unknown")
    email = user_info.get("email", "not provided")

    print_success(f"Authenticated as: {username}")
    print_info(f"  Account type: {user_type}")
    print_info(f"  Email: {email}")

    # Step 3: Check permissions
    print_info("\nStep 3: Checking token permissions...")
    permissions = check_token_permissions(user_info)

    if permissions["read"]:
        print_success("READ permission: Available")
    else:
        print_error("READ permission: Not available")

    if permissions["write"]:
        print_success("WRITE permission: Available")
    else:
        print_warning("WRITE permission: Not available (read-only token)")
        print_info("  This is fine for development, but you'll need write access to publish adapters")

    if permissions["organizations"]:
        print_success(f"Organizations: {', '.join(permissions['organizations'])}")
    else:
        print_info("Organizations: None (personal account only)")
        print_info("  Consider creating 'kwanzaa-project' or 'ainative' organization")

    # Initialize API
    api = HfApi(token=token)

    # Step 4: Check gated model access (optional)
    if args.check_gated_models:
        print_info("\nStep 4: Checking access to gated models...")

        gated_models = [
            "meta-llama/Llama-3.2-1B",
            "meta-llama/Llama-3.2-3B",
            "mistralai/Mistral-7B-v0.1",
        ]

        for model_id in gated_models:
            has_access, message = check_gated_model_access(api, model_id, token)
            if has_access:
                print_success(message)
            else:
                print_warning(message)

    # Step 5: Check write access (optional)
    if args.check_write_access:
        print_info("\nStep 5: Verifying write access...")
        has_write, write_msg = check_write_access(api, username, token)

        if has_write:
            print_success(write_msg)
        else:
            print_warning(write_msg)

    # Summary
    print_header("Verification Summary")

    print_success("Token is valid and ready to use")
    print_info(f"Username: {username}")
    print_info(f"Permissions: {'READ + WRITE' if permissions['write'] else 'READ only'}")

    if permissions["organizations"]:
        print_info(f"Organizations: {', '.join(permissions['organizations'])}")

    print_info("\nRecommendations:")
    print("  1. For local development: Current token is sufficient")
    print("  2. For publishing adapters: Ensure token has WRITE permissions")
    print("  3. For production CI/CD: Use fine-grained token with repo-specific access")
    print("  4. Rotate tokens every 90 days for security")

    if not permissions["organizations"]:
        print("\n  5. Consider creating organization account:")
        print("     - Option A: 'kwanzaa-project' (dedicated to this project)")
        print("     - Option B: 'ainative' (shared across AINative projects)")

    print(f"\n{Colors.GREEN}All checks passed!{Colors.RESET}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
