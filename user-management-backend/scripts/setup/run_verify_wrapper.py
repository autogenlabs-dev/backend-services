import subprocess
import sys

def run_verification():
    print("Starting Key Verification...")
    with open("verify_output.log", "w", encoding="utf-8") as f:
        try:
            result = subprocess.run(
                [sys.executable, "verify_razorpay_keys.py"],
                cwd=r"c:\Users\Asus\Desktop\backend-services\user-management-backend",
                capture_output=True,
                text=True,
                check=False
            )
            f.write("STDOUT:\n")
            f.write(result.stdout)
            f.write("\nSTDERR:\n")
            f.write(result.stderr)
            print("Verification finished. Output written to verify_output.log")
        except Exception as e:
            f.write(f"\nEXCEPTION: {e}")
            print(f"Verification failed with exception: {e}")

if __name__ == "__main__":
    run_verification()
