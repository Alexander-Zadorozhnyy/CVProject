from datetime import datetime

current_data = datetime.today().strftime('%Y-%m-%d')

SITE_DATABASE_NAME = "site.db"
SITE_DATABASE_BACKUP_NAME = 'site_' + current_data + '.db'

MY_PROJECTS_DATABASE_NAME = "projects.db"
MY_PROJECTS_DATABASE_BACKUP_NAME = 'projects_' + current_data + '.db'

MY_ACHIEVEMENTS_DATABASE_NAME = "achievements.db"
MY_ACHIEVEMENTS_DATABASE_BACKUP_NAME = 'achievements_' + current_data + '.db'

REVIEW_DATABASE_NAME = "review.db"
REVIEW_DATABASE_BACKUP_NAME = 'review_' + current_data + '.db'

CONTACTS_DATABASE_NAME = "contacts.db"
CONTACTS_DATABASE_BACKUP_NAME = 'contacts_' + current_data + '.db'
