import os
import re
import csv
import subprocess as sp
from collections import defaultdict

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    POMSG_REGEX = re.compile(r'#: (.*?)\nmsgid "(.*?)"\nmsgstr "(.*?)"\n')
    IGNORE_FOLDERS = (
        'node_modules/',
    )

    def add_arguments(self, parser):
        parser.add_argument('action', choices=('collect', 'apply'))
        parser.add_argument('--file', '-f', help="Path to CSV file", required=True)

    def handle(self, *args, **options):
        if options['action'] == 'collect':
            self._collect(**options)
        elif options['action'] == 'apply':
            self._apply(**options)

    def _collect(self, **options):
        lang_def, langs = self._prepare_languages()

        self.stdout.write(f"Making messages for {langs}...")
        self._make_messages(langs)

        self.stdout.write("Collecting translations from PO-files...")
        translations = self._collect_translations(langs)

        self.stdout.write(f"Preparing CSV-file, location: '{options['file']}'")
        self._prepare_csv(translations, lang_def, langs, options['file'])

        self.stdout.write("Completed")

    def _apply(self, **options):
        lang_def, langs = self._prepare_languages()

        self.stdout.write("Parsing translations...")
        translations = self._parse_csv(lang_def, langs, options['file'])

        self.stdout.write("Patching PO-files...")
        self._patch_messages(translations, langs)

        self.stdout.write("Compiling messages...")
        sp.Popen("python manage.py compilemessages",
                 shell=True, stdout=sp.DEVNULL).communicate()

        self.stdout.write("Completed")

    def _get_languages(self):
        return list(list(zip(*settings.LANGUAGES))[0])

    def _get_default_language(self):
        return settings.LANGUAGE_CODE[:2]

    def _prepare_languages(self):
        lang_def = self._get_default_language()
        langs = self._get_languages()
        langs.remove(lang_def)  # Removing defualt language from langs
        return lang_def, langs

    def _find_po_files(self, lang):
        for locale_path in settings.LOCALE_PATHS:
            folder = os.path.join(locale_path, lang, 'LC_MESSAGES')
            if os.path.exists(folder):
                file_django = os.path.join(folder, 'django.po')
                file_djangojs = os.path.join(folder, 'djangojs.po')
                if os.path.exists(file_django):
                    yield file_django
                if os.path.exists(file_djangojs):
                    yield file_djangojs

    def _parse_po_file(self, path):
        with open(path) as f:
            content = f.read()
        for loc, msgid, msgstr in self.POMSG_REGEX.findall(content, re.DOTALL):
            if not any(loc.startswith(folder) for folder in self.IGNORE_FOLDERS):
                yield msgid, msgstr

    def _make_messages(self, langs):
        for lang in langs:
            command = f"python manage.py makemessages -d djangojs -l {lang}"
            process = sp.Popen(command, shell=True, stdout=sp.DEVNULL)
            process.communicate()

    def _collect_translations(self, langs):
        translations = defaultdict(dict)
        for lang in langs:
            for path in self._find_po_files(lang):
                for msgid, msgstr in self._parse_po_file(path):
                    translations[msgid][lang] = msgstr
        return translations

    def _prepare_csv(self, translations, lang_def, langs, csv_path):
        with open(csv_path, "w") as f:
            writer = csv.writer(f)

            # Writing header
            writer.writerow([lang_def] + langs)

            # Writing rows
            keys = sorted(translations.keys())
            for msgid in keys:
                row = [msgid]
                for lang in langs:
                    row.append(translations[msgid].get(lang, ""))
                writer.writerow(row)

    def _parse_csv(self, lang_def, langs, csv_path):
        translations = {}

        with open(csv_path) as f:
            reader = csv.reader(f)

            header = next(reader)
            langs_csv = header[1:]

            assert header[0] == lang_def, "Invalid default language"
            assert not(set(langs) - set(langs_csv)), "Invalid set of languages"

            for msgid, *msgstrs in reader:
                translations[msgid] = {
                    lang: msgstr
                    for lang, msgstr in zip(langs_csv, msgstrs)
                    if lang in langs
                }

        return translations

    def _patch_messages(self, translations, langs):
        for lang in langs:
            for path in self._find_po_files(lang):
                with open(path) as f:
                    content = f.read()
                for msgid, trans in translations.items():
                    msgstr = trans.get(lang, "")
                    content = re.sub(
                        r'msgid "{}"\nmsgstr ".*?"\n'.format(msgid),
                        r'msgid "{}"\nmsgstr "{}"\n'.format(msgid, msgstr),
                        content
                    )
                with open(path, "w") as f:
                    f.write(content)
