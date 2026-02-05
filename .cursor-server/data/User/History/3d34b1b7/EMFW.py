import os
import subprocess

def run(svc):
    try:
        # Try systemctl first
        result = subprocess.run(
            ["systemctl", "status", svc, "--no-pager", "-l"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            return result.stdout
        else:
            # If systemctl fails, try alternative methods
            # Check if service exists
            check_result = subprocess.run(
                ["systemctl", "list-unit-files", f"{svc}.service"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if check_result.returncode == 0 and svc in check_result.stdout:
                # Service exists but status check failed
                return f"Service '{svc}' exists but status check failed.\n\nError: {result.stderr}\n\nTry: systemctl status {svc}"
            else:
                return f"Service '{svc}' not found.\n\nPossible reasons:\n- Service is not installed\n- Service name is incorrect\n- Service is not managed by systemd\n\nTry: systemctl list-unit-files | grep {svc}"
    except FileNotFoundError:
        return "systemctl command not found. This system may not use systemd."
    except subprocess.TimeoutExpired:
        return f"Timeout while checking service '{svc}' status."
    except Exception as e:
        return f"Error checking service '{svc}': {str(e)}"
