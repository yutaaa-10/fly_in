import sys
from application import Application

if __name__ == "__main__":
    try:
        app = Application()
        sys.exit(app.run())
    except KeyboardInterrupt:
        print("\nProgram interrupted by user.")
