from src.cleanup.cleanup import clean_orphans

print("\n🧹 Running cleanup...")
clean_orphans(dry_run=False)