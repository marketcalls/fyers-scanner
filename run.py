#!/usr/bin/env python
"""
Startup script for Fyers Intraday Scanner
"""
import os
import sys

def main():
    """Start the Fyers Scanner application"""

    # Set default environment variables if not already set
    if not os.getenv("SECRET_KEY"):
        print("⚠️  WARNING: Using default SECRET_KEY. Set SECRET_KEY environment variable for production!")

    if not os.getenv("LOG_LEVEL"):
        os.environ["LOG_LEVEL"] = "INFO"

    print("=" * 60)
    print("🚀 Starting Fyers Intraday Scanner")
    print("=" * 60)
    print(f"📊 Log Level: {os.getenv('LOG_LEVEL')}")
    print(f"🌐 Server: http://localhost:8000")
    print(f"📝 Logs: logs/fyers_scanner.log")
    print("=" * 60)
    print()

    # Import and run uvicorn
    try:
        import uvicorn
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level=os.getenv("LOG_LEVEL", "info").lower()
        )
    except ImportError:
        print("❌ Error: uvicorn not installed. Run: pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down Fyers Scanner...")
        sys.exit(0)

if __name__ == "__main__":
    main()
