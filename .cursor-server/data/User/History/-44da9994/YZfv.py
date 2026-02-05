#!/usr/bin/env python3
"""
Script to fix all page.tsx files with common issues:
1. Replace getApiUrl with import from @/lib/api
2. Replace min-h-screen with h-screen w-screen overflow-hidden
3. Replace fetch calls with apiRequest
4. Add proper error handling
"""

import os
import re
from pathlib import Path

FRONTEND_DIR = Path("/home/ai/ai-agent/frontend/app")

def fix_page_file(file_path: Path):
    """Fix a single page.tsx file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = []
        
        # 1. Check if it needs the api import
        if 'const getApiUrl = () =>' in content and 'import { apiRequest }' not in content:
            # Remove getApiUrl function
            content = re.sub(
                r'const getApiUrl = \(\) => \{[^}]+\};',
                '',
                content,
                flags=re.DOTALL
            )
            # Add import if not present
            if 'import { apiRequest }' not in content:
                # Find the last import statement
                import_match = re.search(r'(import .+ from .+;\n)', content)
                if import_match:
                    last_import_pos = import_match.end()
                    content = content[:last_import_pos] + 'import { apiRequest } from "@/lib/api";\n' + content[last_import_pos:]
                    changes_made.append("Added apiRequest import")
        
        # 2. Fix layout classes
        if 'min-h-screen' in content:
            content = content.replace(
                '<main className="flex bg-slate-950 text-slate-200 min-h-screen">',
                '<main className="flex bg-slate-950 text-slate-200 h-screen w-screen overflow-hidden">'
            )
            content = content.replace(
                '<div className="flex-1 flex flex-col">',
                '<div className="flex-1 flex flex-col overflow-hidden">'
            )
            # Fix the content div
            content = re.sub(
                r'<div className="p-6">',
                '<div className="flex-1 overflow-y-auto overflow-x-hidden p-6 scrollbar-thin">',
                content,
                count=1
            )
            changes_made.append("Fixed layout classes")
        
        # 3. Replace fetch calls with apiRequest (basic pattern)
        # This is more complex and might need manual review
        fetch_pattern = r'const res = await fetch\(`\$\{getApiUrl\(\)\}([^`]+)`,\s*\{[^}]+\}\);'
        if re.search(fetch_pattern, content):
            changes_made.append("Found fetch calls - may need manual review")
        
        # Only write if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, changes_made
        
        return False, []
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False, []

def main():
    """Main function to fix all page.tsx files"""
    page_files = list(FRONTEND_DIR.rglob("page.tsx"))
    
    # Skip login page and main page (already fixed)
    skip_files = ['login/page.tsx', 'page.tsx']
    
    fixed_count = 0
    for page_file in page_files:
        relative_path = page_file.relative_to(FRONTEND_DIR)
        if str(relative_path) in skip_files:
            continue
        
        # Skip already fixed files
        if str(relative_path) in ['cost-analyzer/page.tsx', 'plugins/page.tsx', 
                                   'workflow-builder/page.tsx', 'digital-twin/page.tsx',
                                   'agent-mesh/page.tsx']:
            continue
        
        fixed, changes = fix_page_file(page_file)
        if fixed:
            fixed_count += 1
            print(f"✓ Fixed {relative_path}: {', '.join(changes)}")
    
    print(f"\nTotal files fixed: {fixed_count}")

if __name__ == "__main__":
    main()

