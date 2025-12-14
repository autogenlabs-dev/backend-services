import subprocess
import sys

def run_tests():
    print("Starting E2E tests...")
    with open("e2e_output.log", "w", encoding="utf-8") as f:
        try:
            result = subprocess.run(
                [sys.executable, "test_e2e_payment.py"],
                cwd=r"c:\Users\Asus\Desktop\backend-services\user-management-backend",
                capture_output=True,
                text=True,
                check=False
            )
            f.write("STDOUT:\n")
            f.write(result.stdout)
            f.write("\nSTDERR:\n")
            f.write(result.stderr)
            print("Tests finished. Output written to e2e_output.log")
        except Exception as e:
            f.write(f"\nEXCEPTION: {e}")
            print(f"Tests failed with exception: {e}")

if __name__ == "__main__":
    run_tests()
