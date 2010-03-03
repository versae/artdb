"""
 Command for backup database
"""

import os, time

import pexpect

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Backup database. Only Mysql and Postgresql engines are implemented"

    def handle(self, *args, **options):
        from django.conf import settings

        self.engine = settings.DATABASE_ENGINE
        self.db = settings.DATABASE_NAME
        self.user = settings.DATABASE_USER
        self.passwd = settings.DATABASE_PASSWORD
        self.host = settings.DATABASE_HOST
        self.port = settings.DATABASE_PORT

        backup_dir = getattr(settings, 'BACKUPS_DIR', 'backups')
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        outfile = os.path.join(backup_dir, 'backup_%s.sql' % time.strftime('%y%m%d%S'))

        if self.engine == 'mysql':
            print 'Doing Mysql backup to database %s into %s' % (self.db, outfile)
            self.do_mysql_backup(outfile)
        elif self.engine in ('postgresql_psycopg2', 'postgresql'):
            print 'Doing Postgresql backup to database %s into %s' % (self.db, outfile)
            self.do_postgresql_backup(outfile)
        else:
            print 'Backup in %s engine not implemented' % self.engine

    def do_mysql_backup(self, outfile):
        args = []
        if self.user:
            args += ["--user=%s" % self.user]
        if self.passwd:
            args += ["--password=%s" % self.passwd]
        if self.host:
            args += ["--host=%s" % self.host]
        if self.port:
            args += ["--port=%s" % self.port]
        args += [self.db]

        os.system('mysqldump %s > %s' % (' '.join(args), outfile))

    def do_postgresql_backup(self, outfile):
        args = ['pg_dump']
        if self.user:
            args += ["--username=%s" % self.user]
        if self.passwd:
            args += ["--password"]
        if self.host:
            args += ["--host=%s" % self.host]
        if self.port:
            args += ["--port=%s" % self.port]
        if self.db:
            args += [self.db]

        child = pexpect.spawn(' '.join(args))
        if self.passwd:
            child.expect("\s*:") # pg_dump ask for the password here
            child.sendline(self.passwd)

        child.expect(pexpect.EOF)
        file(outfile, "w").write(child.before)
        child.close()

