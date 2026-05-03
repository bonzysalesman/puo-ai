import os
import shutil
from datetime import datetime, timedelta

def cleanup_backups(backup_dir='backups', days_to_keep=30):
    if not os.path.exists(backup_dir):
        print(f"Directory {backup_dir} does not exist.")
        return

    now = datetime.now()
    cutoff = now - timedelta(days=days_to_keep)
    
    deleted_count = 0
    for item in os.listdir(backup_dir):
        path = os.path.join(backup_dir, item)
        if not os.path.isdir(path):
            continue
            
        # Expecting format backup_YYYYMMDD_HHMMSS
        if item.startswith('backup_'):
            try:
                date_str = item.split('_')[1]
                backup_date = datetime.strptime(date_str, '%Y%m%d')
                
                if backup_date < cutoff:
                    print(f"Deleting old backup: {item}")
                    shutil.rmtree(path)
                    deleted_count += 1
            except (ValueError, IndexError):
                print(f"Skipping non-standard backup directory: {item}")
                
    print(f"Cleanup complete. Deleted {deleted_count} old backups.")

if __name__ == "__main__":
    cleanup_backups()
