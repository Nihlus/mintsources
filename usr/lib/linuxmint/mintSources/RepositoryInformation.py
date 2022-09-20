from __future__ import annotations

from debian import deb822
from typing import Iterable, SupportsIndex

import re
import urllib.parse


class _BaseRepositoryInformation:
    """
    Acts as a base type for repository information classes, containing common settings and fields.
    """

    def __init__(
            self,
            components: list[str],
            enabled: bool = None,
            architectures: list[str] | None = None,
            languages: list[str] | None = None,
            targets: list[str] | None = None,
            pdiffs: bool | None = None,
            by_hash: str | None = None,
            allow_insecure: bool | None = None,
            allow_weak: bool | None = None,
            allow_downgrade_to_insecure: bool | None = None,
            trusted: bool | None = None,
            signed_by: str | None = None,
            check_valid_until: bool | None = None,
            valid_until_min: int | None = None,
            valid_until_max: int | None = None,
            check_date: bool | None = None,
            date_max_future: int | None = None,
            inrelease_path: str | None = None
    ) -> None:
        self.components = components
        self.enabled = enabled
        self.architectures = architectures
        self.languages = languages
        self.targets = targets
        self.pdiffs = pdiffs
        self.by_hash = by_hash
        self.allow_insecure = allow_insecure
        self.allow_weak = allow_weak
        self.allow_downgrade_to_insecure = allow_downgrade_to_insecure
        self.trusted = trusted
        self.signed_by = signed_by
        self.check_valid_until = check_valid_until
        self.valid_until_min = valid_until_min
        self.valid_until_max = valid_until_max
        self.check_date = check_date
        self.date_max_future = date_max_future
        self.inrelease_path = inrelease_path

    def is_enabled(self):
        """
        Determines whether the repository is enabled.
        :return: true if the repository is enabled; otherwise, false.
        """

        if self.enabled is None:
            return True

        return self.enabled


class Deb822RepositoryInformation(_BaseRepositoryInformation):
    """
    Represents a DEB822-formatted repository, which can contain multiple types, URIs, and suites in one.
    """

    def __init__(
            self,
            repo_types: list[str],
            uris: list[str],
            suites: list[str],
            components: list[str],
            enabled: bool = None,
            architectures: list[str] | None = None,
            languages: list[str] | None = None,
            targets: list[str] | None = None,
            pdiffs: bool | None = None,
            by_hash: str | None = None,
            allow_insecure: bool | None = None,
            allow_weak: bool | None = None,
            allow_downgrade_to_insecure: bool | None = None,
            trusted: bool | None = None,
            signed_by: str | None = None,
            check_valid_until: bool | None = None,
            valid_until_min: int | None = None,
            valid_until_max: int | None = None,
            check_date: bool | None = None,
            date_max_future: int | None = None,
            inrelease_path: str | None = None
    ) -> None:
        self.repo_types = repo_types
        self.uris = uris
        self.suites = suites

        super().__init__(
            components,
            enabled,
            architectures,
            languages,
            targets,
            pdiffs,
            by_hash,
            allow_insecure,
            allow_weak,
            allow_downgrade_to_insecure,
            trusted,
            signed_by,
            check_valid_until,
            valid_until_min,
            valid_until_max,
            check_date,
            date_max_future,
            inrelease_path
        )

    @staticmethod
    def from_deb822(value: deb822.Deb822) -> Deb822RepositoryInformation:
        """
        Parses a :py:class:`RepositoryInformation` instance from the given :py:class:`deb822.Deb822` data.

        :param value: The data.
        :return: The repository information.
        """

        def _get_values(container: deb822.Deb822, key: str) -> list[str] | None:
            """
            Gets whitespace-separated values from the given container with the given key. The contained value should be
            a whitespace-separated string, which will be split into its constituent parts.

            :param container: The container.
            :param key: The key.
            :return: The values.
            """
            something = container.get(key)
            if something is None:
                return None

            if not isinstance(something, str):
                raise TypeError

            return something.split()

        return Deb822RepositoryInformation(
            _get_values(value, 'Types'),
            _get_values(value, 'URIs'),
            _get_values(value, 'Suites'),
            _get_values(value, 'Components'),
            value.get('Enabled'),
            _get_values(value, 'Architectures'),
            _get_values(value, 'Languages'),
            _get_values(value, 'Targets'),
            value.get('PDiffs'),
            value.get('By-Hash'),
            value.get('Allow-Insecure'),
            value.get('Allow-Weak'),
            value.get('Allow-Downgrade-To-Insecure'),
            value.get('Trusted'),
            value.get('Signed-By'),
            value.get('Check-Valid-Until'),
            value.get('Valid-Until-Min'),
            value.get('Valid-Until-Max'),
            value.get('Check-Date'),
            value.get('Date-Max-Future')
        )

    @staticmethod
    def from_sources(value: Iterable[str]) -> list[Deb822RepositoryInformation]:
        """
        Parses a :py:class:`Deb822RepositoryInformation` instance from the given data. The data must be an iterable type
        that produces strings; typically, this means either a list or a file. Lines consisting entirely of whitespace
        will be ignored, as will malformed ones.

        :param value: The data.
        :return: The repository information.
        """
        repositories = []
        for paragraph in deb822.Deb822.iter_paragraphs(value):

            repository = Deb822RepositoryInformation.from_deb822(paragraph)
            if repository is None:
                continue

            repositories.append(repository)

        return repositories

    @staticmethod
    def from_line_information(value: LineRepositoryInformation) -> Deb822RepositoryInformation:
        """
        Converts a :py:class:`LineRepositoryInformation` instance to an equivalent
        :py:class:`Deb822RepositoryInformation` instance.

        :param value: The repository information.
        """
        return Deb822RepositoryInformation(
            [value.repo_type],
            [value.uri],
            [value.suite],
            value.components,
            value.enabled,
            value.architectures,
            value.languages,
            value.targets,
            value.pdiffs,
            value.by_hash,
            value.allow_insecure,
            value.allow_weak,
            value.allow_downgrade_to_insecure,
            value.trusted,
            value.signed_by,
            value.check_valid_until,
            value.valid_until_min,
            value.valid_until_max,
            value.check_date,
            value.date_max_future
        )

    def to_deb822(self) -> deb822.Deb822:
        def write_if_present(container: deb822.Deb822, key: (SupportsIndex, str), val: str | list[str] | bool | None):
            if val is None:
                return

            mapped_value: str
            if isinstance(val, str):
                mapped_value = val
            elif isinstance(val, list):
                mapped_value = ' '.join(val)
            elif isinstance(val, bool):
                mapped_value = 'yes' if val else 'no'
            else:
                raise TypeError

            container[key] = mapped_value

        value = deb822.Deb822()
        value['Types'] = ' '.join(self.repo_types)
        value['URIs'] = ' '.join(self.uris)
        value['Suites'] = ' '.join(self.suites)
        value['Components'] = ' '.join(self.components)

        write_if_present(value, 'Enabled', self.enabled)
        write_if_present(value, 'Architectures', self.architectures)
        write_if_present(value, 'Targets', self.targets)
        write_if_present(value, 'PDiffs', self.pdiffs)
        write_if_present(value, 'By-Hash', self.by_hash)
        write_if_present(value, 'Allow-Insecure', self.allow_insecure)
        write_if_present(value, 'Allow-Weak', self.allow_weak)
        write_if_present(value, 'Allow-Downgrade-To-Insecure', self.allow_downgrade_to_insecure)
        write_if_present(value, 'Trusted', self.trusted)
        write_if_present(value, 'Signed-By', self.signed_by)
        write_if_present(value, 'Check-Valid-Until', self.check_valid_until)
        write_if_present(value, 'Valid-Until-Min', self.valid_until_min)
        write_if_present(value, 'Valid-Until-Max', self.valid_until_max)
        write_if_present(value, 'Check-Date', self.check_date)
        write_if_present(value, 'Date-Max-Future', self.date_max_future)

        return value


class LineRepositoryInformation(_BaseRepositoryInformation):
    """
    Represents a one-line formatted repository which can only contain information about a single repository.
    """

    _name_map: dict[str, str] = {
        'arch': 'architectures',
        'architectures': 'arch',
        'lang': 'languages',
        'languages': 'lang',
        'target': 'targets',
        'targets': 'target'
    }

    def __init__(
            self,
            repo_type: str,
            uri: str,
            suite: str,
            components: list[str],
            enabled: bool = None,
            architectures: list[str] | None = None,
            languages: list[str] | None = None,
            targets: list[str] | None = None,
            pdiffs: bool | None = None,
            by_hash: str | None = None,
            allow_insecure: bool | None = None,
            allow_weak: bool | None = None,
            allow_downgrade_to_insecure: bool | None = None,
            trusted: bool | None = None,
            signed_by: str | None = None,
            check_valid_until: bool | None = None,
            valid_until_min: int | None = None,
            valid_until_max: int | None = None,
            check_date: bool | None = None,
            date_max_future: int | None = None,
            inrelease_path: str | None = None
    ) -> None:
        self.repo_type = repo_type
        self.uri = uri
        self.suite = suite

        super().__init__(
            components,
            enabled,
            architectures,
            languages,
            targets,
            pdiffs,
            by_hash,
            allow_insecure,
            allow_weak,
            allow_downgrade_to_insecure,
            trusted,
            signed_by,
            check_valid_until,
            valid_until_min,
            valid_until_max,
            check_date,
            date_max_future, inrelease_path
        )

    @staticmethod
    def from_line(line: str) -> LineRepositoryInformation | None:
        """
        Parses repository information from the given string. If no valid repository could be parsed from the string,
        this method returns None.
        :param line: The line to parse.
        :return: The parsed information or None.
        """
        options_regex = re.compile(r"\[.+]")

        options = options_regex.search(line)
        if options is not None:
            line = options_regex.sub('', line)
            options = options.group(0)[1:-1].split()
            options = {val.split('=')[0]: val.split('=')[1].split(',') for val in options}

        if line.startswith('#'):
            line = line[1:]
            enabled = False
        else:
            enabled = True

        parts = list(filter(None, line.split()))
        # at least one component is required
        if len(parts) < 4:
            return None

        if parts[0] not in ['deb', 'deb-src']:
            return None

        try:
            urllib.parse.urlparse(parts[1])
            uri = parts[1]
        except ValueError:
            return None

        return LineRepositoryInformation(
            parts[0],
            uri,
            parts[2],
            parts[3:],
            enabled,
            options.get('arch'),
            options.get('lang'),
            options.get('target'),
            options.get('pdiffs'),
            options.get('by-hash'),
            options.get('allow-insecure'),
            options.get('allow-weak'),
            options.get('allow-downgrade-to-insecure'),
            options.get('trusted'),
            options.get('signed-by'),
            options.get('check-valid-until'),
            options.get('valid-until-min'),
            options.get('valid-until-max'),
            options.get('check-date'),
            options.get('date-max-future')
        )

    @staticmethod
    def from_lists(value: Iterable[str]) -> list[LineRepositoryInformation]:
        """
        Parses a :py:class:`LineRepositoryInformation` instance from the given data. The data must be an iterable type
        that produces strings; typically, this means either a list or a file. Lines consisting entirely of whitespace
        will be ignored, as will malformed ones.
        :param value: The data.
        :return: The repository information.
        """
        repositories = []
        for line in value:
            if line.isspace():
                continue

            repository = LineRepositoryInformation.from_line(line)
            if repository is None:
                continue

            repositories.append(repository)

        return repositories

    @staticmethod
    def from_deb822_information(value: Deb822RepositoryInformation) -> list[LineRepositoryInformation]:
        """
        Converts a :py:class:`Deb822RepositoryInformation` instance to a set of equivalent
        :py:class:`LineRepositoryInformation` instances.

        :param value: The repository information.
        """
        for repo_type in value.repo_types:
            for uri in value.uris:
                for suite in value.suites:
                    yield LineRepositoryInformation(
                        repo_type,
                        uri,
                        suite,
                        value.components,
                        value.enabled,
                        value.architectures,
                        value.languages,
                        value.targets,
                        value.pdiffs,
                        value.by_hash,
                        value.allow_insecure,
                        value.allow_weak,
                        value.allow_downgrade_to_insecure,
                        value.trusted,
                        value.signed_by,
                        value.check_valid_until,
                        value.valid_until_min,
                        value.valid_until_max,
                        value.check_date,
                        value.date_max_future
                    )

    def to_line(self) -> str:
        """
        Formats the repository information as a one-line sources.list entry.
        :return: The formatted line.
        """

        def _format_options() -> str:
            """
            Formats the set options in the instance as one-line sources.list options.
            :return: The formatted options or an empty string if no options are set.
            """
            options = {k: v for k, v in self.__dict__.items() if k not in {'repo_type', 'uri', 'suite', 'components', 'enabled'} and v is not None}
            if len(options) <= 0:
                return ''

            option_string = ''
            for name, value in options.items():
                # Remap the name if required
                if name in self._name_map:
                    name = self._name_map[name]

                # Remap word separators
                name.replace('_', '-')

                stringified_value = value if not isinstance(value, list) else ','.join(value)
                option_string += name + '=' + stringified_value + ' '

            option_string = option_string.strip()

            return f' [{option_string}] '

        joined_components = ' '.join(self.components)
        disabler = '# ' if not self.enabled else ''
        result = f'{disabler}{self.repo_type}{_format_options()}{self.uri} {self.suite} {joined_components}'

        return result
