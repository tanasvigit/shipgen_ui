"""
Audit script to check VIEWER role permissions across all API endpoints.

This script scans all router files and identifies:
- Endpoints with proper role guards (require_roles)
- Endpoints missing role guards (security risk)
- Mutation endpoints (POST/PUT/PATCH/DELETE) that need protection

Run from fastapi-app directory:
    python scripts/audit_viewer_permissions.py
"""

import os
import re
from pathlib import Path
from typing import List, Tuple


# Colors for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"


def scan_router_files(routers_dir: str) -> List[Tuple[str, str, int, str]]:
    """
    Scan all router files and find mutation endpoints.
    
    Returns list of tuples:
        (filename, endpoint_path, line_number, has_role_guard)
    """
    issues = []
    
    routers_path = Path(routers_dir)
    if not routers_path.exists():
        print(f"{RED}Error: Routers directory not found: {routers_dir}{RESET}")
        return issues
    
    # Pattern to match route decorators
    route_pattern = re.compile(
        r'@router\.(post|put|patch|delete)\("([^"]*)"',
        re.MULTILINE
    )
    
    # Pattern to check for require_roles
    require_roles_pattern = re.compile(r'require_roles\(')
    
    for py_file in sorted(routers_path.glob("*.py")):
        filename = py_file.name
        content = py_file.read_text()
        lines = content.split('\n')
        
        # Skip if file doesn't have any mutation routes
        if not route_pattern.search(content):
            continue
        
        # Find all route decorators
        for match in route_pattern.finditer(content):
            method = match.group(1).upper()
            path = match.group(2)
            line_num = content[:match.start()].count('\n') + 1
            
            # Look ahead 20 lines for require_roles
            lookahead_end = min(line_num + 20, len(lines))
            lookahead_text = '\n'.join(lines[line_num-1:lookahead_end])
            
            has_role_guard = bool(require_roles_pattern.search(lookahead_text))
            
            endpoint_path = f"{method} {path}"
            issues.append((filename, endpoint_path, line_num, has_role_guard))
    
    return issues


def print_report(issues: List[Tuple[str, str, int, str]]):
    """Print formatted audit report."""
    
    print("\n" + "="*80)
    print(f"{BOLD}{BLUE}VIEWER ROLE PERMISSIONS AUDIT REPORT{RESET}")
    print("="*80 + "\n")
    
    protected = [i for i in issues if i[3]]
    unprotected = [i for i in issues if not i[3]]
    
    # Summary
    print(f"{BOLD}Summary:{RESET}")
    print(f"  Total mutation endpoints: {len(issues)}")
    print(f"  {GREEN}✓ Protected with role guards: {len(protected)}{RESET}")
    print(f"  {RED}✗ Missing role guards: {len(unprotected)}{RESET}")
    print()
    
    # Protected endpoints
    if protected:
        print(f"{GREEN}{BOLD}✓ PROTECTED ENDPOINTS (Safe){RESET}")
        print("-" * 80)
        for filename, endpoint, line_num, _ in protected:
            print(f"  {GREEN}✓{RESET} {filename:40s} {endpoint:30s} (line {line_num})")
        print()
    
    # Unprotected endpoints (CRITICAL)
    if unprotected:
        print(f"{RED}{BOLD}✗ UNPROTECTED ENDPOINTS (SECURITY RISK){RESET}")
        print("-" * 80)
        print(f"{RED}These endpoints allow VIEWER to perform mutations!{RESET}\n")
        for filename, endpoint, line_num, _ in unprotected:
            print(f"  {RED}✗{RESET} {filename:40s} {endpoint:30s} (line {line_num})")
        print()
    
    # Per-file breakdown
    print(f"{BOLD}{BLUE}Per-File Breakdown:{RESET}")
    print("-" * 80)
    
    files_dict = {}
    for filename, endpoint, line_num, has_guard in issues:
        if filename not in files_dict:
            files_dict[filename] = {"protected": 0, "unprotected": 0}
        if has_guard:
            files_dict[filename]["protected"] += 1
        else:
            files_dict[filename]["unprotected"] += 1
    
    for filename in sorted(files_dict.keys()):
        stats = files_dict[filename]
        total = stats["protected"] + stats["unprotected"]
        
        if stats["unprotected"] > 0:
            status = f"{RED}✗ {stats['unprotected']} unprotected{RESET}"
        else:
            status = f"{GREEN}✓ All protected{RESET}"
        
        print(f"  {filename:40s} {total:3d} endpoints  {status}")
    
    print()
    
    # Final verdict
    print("="*80)
    if not unprotected:
        print(f"{GREEN}{BOLD}✓ PASS: All mutation endpoints are properly protected!{RESET}")
        print(f"{GREEN}VIEWER role has zero CRUD access. System is secure.{RESET}")
    else:
        print(f"{RED}{BOLD}✗ FAIL: {len(unprotected)} endpoints lack role guards!{RESET}")
        print(f"{RED}VIEWER role can perform unauthorized mutations. FIX REQUIRED.{RESET}")
    print("="*80 + "\n")
    
    return len(unprotected) == 0


def main():
    """Main entry point."""
    print(f"\n{BOLD}Scanning router files for VIEWER permission issues...{RESET}\n")
    
    # Determine routers directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    routers_dir = project_root / "app" / "api" / "v1" / "routers"
    
    if not routers_dir.exists():
        print(f"{RED}Error: Cannot find routers directory at:{RESET}")
        print(f"  {routers_dir}")
        print(f"\nPlease run this script from the fastapi-app directory:")
        print(f"  cd fastapi-app")
        print(f"  python scripts/audit_viewer_permissions.py\n")
        return 1
    
    # Scan files
    issues = scan_router_files(str(routers_dir))
    
    if not issues:
        print(f"{YELLOW}No mutation endpoints found. This seems wrong. Check routers directory.{RESET}")
        return 1
    
    # Print report
    passed = print_report(issues)
    
    # Exit code
    return 0 if passed else 1


if __name__ == "__main__":
    exit(main())
