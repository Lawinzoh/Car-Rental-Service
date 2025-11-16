from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, IntegrityError
from users.models import Client, Domain
import csv
import json
import os


class Command(BaseCommand):
    help = (
        "Create tenants in batch from a CSV or JSON file or interactively.\n"
        "CSV expected columns: schema_name,name,domain,is_primary,paid_until,on_trial"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            'path', nargs='?', help='Path to CSV or JSON file. If omitted, runs interactive prompt.'
        )
        parser.add_argument('--format', choices=['csv', 'json'], default='csv')
        parser.add_argument('--dry-run', action='store_true', help='Validate input and print actions without saving')
        parser.add_argument('--skip-migrations', action='store_true', help='Do not rely on auto-create schema behavior (no-op)')

    def _parse_csv(self, path):
        rows = []
        with open(path, newline='', encoding='utf-8') as fh:
            reader = csv.DictReader(fh)
            for r in reader:
                rows.append(r)
        return rows

    def _parse_json(self, path):
        with open(path, encoding='utf-8') as fh:
            data = json.load(fh)
        if isinstance(data, dict):
            # support single-object -> list
            return [data]
        return data

    def handle(self, *args, **options):
        path = options.get('path')
        fmt = options.get('format')
        dry = options.get('dry_run')

        tenants = []
        if path:
            if not os.path.exists(path):
                raise CommandError(f'File not found: {path}')
            if fmt == 'csv':
                tenants = self._parse_csv(path)
            else:
                tenants = self._parse_json(path)
        else:
            # interactive single tenant
            self.stdout.write('Interactive tenant creation')
            schema = input('schema_name: ').strip()
            name = input('name: ').strip()
            domain = input('domain (e.g. tenant1.localhost): ').strip()
            is_primary = input('is_primary [y/N]: ').strip().lower() in ('y', 'yes', 'true', '1')
            paid_until = input('paid_until [YYYY-MM-DD] (optional): ').strip() or None
            on_trial = input('on_trial [y/N]: ').strip().lower() in ('y', 'yes', 'true', '1')
            tenants = [
                {
                    'schema_name': schema,
                    'name': name,
                    'domain': domain,
                    'is_primary': is_primary,
                    'paid_until': paid_until,
                    'on_trial': on_trial,
                }
            ]

        if not tenants:
            self.stdout.write('No tenants to create.')
            return

        for row in tenants:
            schema_name = row.get('schema_name')
            name = row.get('name')
            domain = row.get('domain')
            is_primary = str(row.get('is_primary', 'True')).lower() in ('1', 'true', 'yes', 'y')
            paid_until = row.get('paid_until') or None
            on_trial = str(row.get('on_trial', 'True')).lower() in ('1', 'true', 'yes', 'y')

            self.stdout.write(f"Preparing tenant: schema='{schema_name}' name='{name}' domain='{domain}' primary={is_primary}")

            if dry:
                continue

            try:
                with transaction.atomic():
                    client = Client(
                        schema_name=schema_name,
                        name=name,
                    )
                    if paid_until:
                        client.paid_until = paid_until
                    client.on_trial = on_trial
                    # auto_create_schema True ensures django-tenants will create the schema
                    client.auto_create_schema = True
                    client.save()

                    if domain:
                        Domain.objects.create(domain=domain, tenant=client, is_primary=is_primary)

                    self.stdout.write(self.style.SUCCESS(f"Created tenant: {schema_name}"))
            except IntegrityError as e:
                self.stderr.write(self.style.ERROR(f"Failed to create tenant {schema_name}: {e}"))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Unexpected error for {schema_name}: {e}"))

        self.stdout.write(self.style.NOTICE('Batch tenant creation complete.'))
