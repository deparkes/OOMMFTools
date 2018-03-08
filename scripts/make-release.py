#!/usr/bin/env python

"""
Copyright © 2010 by the Pallets team.
Modifications © 2018 by Duncan Parkes

Some rights reserved.

Redistribution and use in source and binary forms of the software as
well as documentation, with or without modification, are permitted
provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright
  notice, this list of conditions and the following disclaimer in the
  documentation and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE AND DOCUMENTATION IS PROVIDED BY THE COPYRIGHT HOLDERS AND
CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING,
BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
THIS SOFTWARE AND DOCUMENTATION, EVEN IF ADVISED OF THE POSSIBILITY OF
SUCH DAMAGE.
"""

from __future__ import print_function

import os
import re
import sys
from datetime import date, datetime
from subprocess import PIPE, Popen

_date_strip_re = re.compile(r'(?<=\d)(st|nd|rd|th)')


def parse_changelog():
    with open('CHANGES.rst') as f:
        lineiter = iter(f)
        for line in lineiter:
            match = re.search('^Version\s+(.*)', line.strip())

            if match is None:
                continue

            version = match.group(1).strip()

            if next(lineiter).count('-') != len(match.group(0)):
                continue

            while 1:
                change_info = next(lineiter).strip()

                if change_info:
                    break

            match = re.search(
                r'released on (\w+\s+\d+\w+\s+\d+)(?:, codename (.*))?',
                change_info,
                flags=re.IGNORECASE
            )

            if match is None:
                continue

            datestr, codename = match.groups()
            return version, parse_date(datestr), codename


def bump_version(version):
    try:
        parts = [int(i) for i in version.split('.')]
    except ValueError:
        fail('Current version is not numeric')

    parts[-1] += 1
    return '.'.join(map(str, parts))


def parse_date(string):
    string = _date_strip_re.sub('', string)
    return datetime.strptime(string, '%B %d %Y')


def set_filename_version(filename, version_number, pattern):
    assert os.path.isfile(filename)
    changed = []

    def inject_version(match):
        before, old, after = match.groups()
        changed.append(True)
        print(version_number)
        print(old)
        return before + version_number + after

    with open(filename) as f:
        contents = re.sub(
            r"^(\s*%s\s*=\s*')(.+?)(')" % pattern,
            inject_version, f.read(),
            flags=re.DOTALL | re.MULTILINE
        )
    print(contents)
    print('here')
    if not changed:
        fail('Could not find %s in %s', pattern, filename)

    with open(filename, 'w') as f:
        f.write(contents)


def set_init_version(version):
    info('Setting _about.py version to %s', version)
    set_filename_version('oommftools/_about.py', version, '__version__')


def build():
    cmd = [sys.executable, 'setup.py', 'sdist', 'bdist_wheel']
    Popen(cmd).wait()


def fail(message, *args):
    print('Error:', message % args, file=sys.stderr)
    sys.exit(1)


def info(message, *args):
    print(message % args, file=sys.stderr)


def get_git_tags():
    return set(
        Popen(['git', 'tag'], stdout=PIPE).communicate()[0].splitlines()
    )


def git_is_clean():
    return Popen(['git', 'diff', '--quiet']).wait() == 0


def make_git_commit(message, *args):
    message = message % args
    Popen(['git', 'commit', '-am', message]).wait()


def make_git_tag(tag):
    info('Tagging "%s"', tag)
    Popen(['git', 'tag', tag]).wait()


def main():
    os.chdir(os.path.join(os.path.dirname(__file__), '..'))

    rv = parse_changelog()

    if rv is None:
        fail('Could not parse changelog')

    version, release_date, codename = rv
    dev_version = bump_version(version) + '.dev'

    info(
        'Releasing %s (codename %s, release date %s)',
        version, codename, release_date.strftime('%d/%m/%Y')
    )
    tags = get_git_tags()

    if version in tags:
        fail('Version "%s" is already tagged', version)

    if release_date.date() != date.today():
        fail(
            'Release date is not today (%s != %s)',
            release_date.date(), date.today()
        )

    if not git_is_clean():
        fail('You have uncommitted changes in git')

    try:
        import wheel  # noqa: F401
    except ImportError:
        fail('You need to install the wheel package.')

    set_init_version(version)
    make_git_commit('Bump version number to %s', version)
    make_git_tag('v'+version)
    build()
    set_init_version(dev_version)


if __name__ == '__main__':
    main()
