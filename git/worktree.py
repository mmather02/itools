# -*- coding: UTF-8 -*-
# Copyright (C) 2011 Juan David Ibáñez Palomar <jdavid@itaapy.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Import from the Standard Library
from datetime import datetime
from os import listdir, remove, rmdir, walk
from os.path import abspath, exists, getmtime, isabs, isdir, isfile, normpath
from re import search
from shutil import copy2, copytree
from subprocess import Popen, PIPE

# Import from pygit2
from pygit2 import Repository, GitError, init_repository
from pygit2 import GIT_SORT_REVERSE, GIT_SORT_TIME
from pygit2 import GIT_OBJ_COMMIT, GIT_OBJ_TREE


class Worktree(object):

    timestamp = None

    def __init__(self, path):
        self.path = abspath(path) + '/'
        self.index_path = '%s/.git/index' % path
        self.cache = {} # {sha: object}
        self.repo = Repository('%s/.git' % self.path)


    def _get_abspath(self, path):
        if isabs(path):
            if path.startswith(self.path):
                return path
            raise ValueError, 'unexpected absolute path "%s"' % path
        if path == '.':
            return self.path
        return '%s%s' % (self.path, path)


    def _call(self, command):
        """Wrapper around 'subprocess.Popen'
        """
        popen = Popen(command, stdout=PIPE, stderr=PIPE, cwd=self.path)
        stdoutdata, stderrdata = popen.communicate()
        if popen.returncode != 0:
            raise EnvironmentError, (popen.returncode, stderrdata)
        return stdoutdata


    def _resolve_reference(self, reference):
        if reference != 'HEAD':
            raise NotImplementedError

        repo_path = '%s/.git' % self.path
        ref = open('%s/HEAD' % repo_path).read().split()[-1]
        return open('%s/%s' % (repo_path, ref)).read().strip()


    def lookup(self, sha):
        cache = self.cache
        if sha not in cache:
            cache[sha] = self.repo[sha]

        return cache[sha]


    def _lookup_by_commit_and_path(self, commit, path):
        obj = commit.tree
        for name in path.split('/'):
            if obj.type != GIT_OBJ_TREE:
                return None

            if name not in obj:
                return None
            entry = obj[name]
            obj = self.lookup(entry.sha)
        return obj


    def walk(self, path='.'):
        # 1. Check and normalize path
        if isabs(path):
            raise ValueError, 'unexpected absolute path "%s"' % path

        path = normpath(path)
        if path == '.':
            path = ''
        elif path == '.git':
            raise ValueError, 'cannot walk .git'
        elif not isdir('%s%s' % (self.path, path)):
            yield path
            return
        else:
            path += '/'

        # 2. Go
        stack = [path]
        while stack:
            folder_rel = stack.pop()
            folder_abs = '%s%s' % (self.path, folder_rel)
            for name in listdir(folder_abs):
                path_abs = '%s%s' % (folder_abs, name)
                path_rel = '%s%s' % (folder_rel, name)
                if path_rel == '.git':
                    continue
                if isdir(path_abs):
                    path_rel += '/'
                    stack.append(path_rel)

                yield path_rel


    @property
    def index(self):
        index = self.repo.index
        # Bare repository
        if index is None:
            raise RuntimeError, 'expected standard repository, not bare'

        path = self.index_path
        if exists(path):
            mtime = getmtime(path)
            if not self.timestamp or self.timestamp < mtime:
                index.read()
                self.timestamp = mtime

        return index


    #######################################################################
    # Public API
    #######################################################################
    def git_add(self, *args):
        index = self.index
        for path in args:
            for path in self.walk(path):
                if path[-1] != '/':
                    index.add(path)


    def git_rm(self, *args):
        index = self.index
        n = len(self.path)
        for path in args:
            abspath = self._get_abspath(path)
            # 1. File
            if isfile(abspath):
                del index[path]
                remove(abspath)
                continue
            # 2. Folder
            for root, dirs, files in walk(abspath, topdown=False):
                for name in files:
                    del index['%s/%s' % (root[n:], name)]
                    remove('%s/%s' % (root, name))
                for name in dirs:
                    rmdir('%s/%s' % (root, name))


    def git_mv(self, source, target):
        source_abs = self._get_abspath(source)
        target = self._get_abspath(target)
        if isfile(source_abs):
            copy2(source_abs, target)
        else:
            copytree(source_abs, target)

        self.git_rm(source)


    def git_clean(self):
        index = self.index

        walk = self.walk()
        for path in sorted(walk, reverse=True):
            abspath = '%s%s' % (self.path, path)
            if path[-1] == '/':
                if not listdir(abspath):
                    rmdir(abspath)
            elif path not in index:
                remove(abspath)


    def git_commit(self, message, author=None, date=None, quiet=False):
        self.index.write()
        self.timestamp = getmtime(self.index_path)

        cmd = ['git', 'commit', '-m', message]
        if author:
            cmd.append('--author=%s' % author)
        if date:
            date = date.strftime('%Y-%m-%dT%H:%M:%S%Z')
            cmd.append('--date=%s' % date)
        if quiet:
            cmd.append('-q')

        try:
            self._call(cmd)
        except EnvironmentError, excp:
            # Avoid an exception for the 'nothing to commit' case
            # FIXME Not reliable, we may catch other cases
            if excp.errno != 1:
                raise


    def git_diff(self, expr, paths=None, stat=False):
        cmd = ['git', 'diff', expr]
        if stat:
            cmd.append('--stat')
        if paths:
            cmd.append('--')
            cmd.extend(paths)
        return self._call(cmd)


    def git_log(self, files=None, n=None, author=None, grep=None,
                reverse=False):
        # Get the sha
        sha = self._resolve_reference('HEAD')

        # Sort
        sort = GIT_SORT_TIME
        if reverse is True:
            sort |= GIT_SORT_REVERSE

        # Go
        commits = []
        for commit in self.repo.walk(sha, GIT_SORT_TIME):
            # --author=<pattern>
            if author:
                name, email, time = commit.author
                if not search(author, name) and not search(author, email):
                    continue

            # --grep=<pattern>
            if grep:
                if not search(grep, commit.message):
                    continue

            # -- path ...
            if files:
                parents = commit.parents
                parent = parents[0] if parents else None
                for path in files:
                    a = self._lookup_by_commit_and_path(commit, path)
                    if parent is None:
                        if a:
                            break
                    else:
                        b = self._lookup_by_commit_and_path(parent, path)
                        if a is not b:
                            break
                else:
                    continue

            ts = commit.commit_time
            commits.append(
                {'revision': commit.sha,             # commit
                 'username': commit.author[0],       # author name
                 'date': datetime.fromtimestamp(ts), # author date
                 'message': commit.message_short,    # subject
                })
            if n is not None:
                n -= 1
                if n == 0:
                    break

        # Ok
        return commits


    def git_reset(self):
        # Use a try/except because this fails with new repositories
        try:
            self._call(['git', 'reset', '--hard', '-q'])
        except EnvironmentError:
            pass


    def git_show(self, sha):
        commit = self.lookup(sha)

        data = self._call(['git', 'show', sha, '--pretty=format:'])
        data = data[1:]

        author = commit.author
        return {
            'author_name': author[0],
            'author_date': datetime.fromtimestamp(author[2]),
            'subject': commit.message_short,
            'diff': data}


    def git_stats(self, commit):
        cmd = ['git', 'show', '--pretty=format:', '--stat', commit]
        data = self._call(cmd)
        return data[1:]


    def describe(self, match=None):
        # The command
        command = ['git', 'describe', '--tags', '--long']
        if match:
            command.extend(['--match', match])

        # Call
        try:
            data = self._call(command)
        except EnvironmentError:
            return None
        tag, n, commit = data.rsplit('-', 2)
        return tag, int(n), commit


    def get_blob_id(self, commit_id, path):
        commit = self.lookup(commit_id)
        if commit.type != GIT_OBJ_COMMIT:
            raise ValueError, 'XXX'

        blob = self._lookup_by_commit_and_path(commit, path)
        return blob.sha


    def get_branch_name(self):
        """Returns the name of the current branch.
        """
        ref = open('%s/.git/HEAD' % self.path).read().rstrip()
        ref = ref.rsplit('/', 1)
        return ref[1] if len(ref) == 2 else None


    def get_filenames(self):
        """Returns the list of filenames tracked by git.
        """
        index = self.index
        return [ index[i].path for i in range(0, len(index)) ]


    def get_files_changed(self, since, until):
        """Get the files that have been changed by a set of commits.
        """
        expr = '%s..%s' % (since, until)
        cmd = ['git', 'show', '--numstat', '--pretty=format:', expr]
        data = self._call(cmd)
        lines = data.splitlines()
        return frozenset([ line.split('\t')[-1] for line in lines if line ])


    def get_metadata(self, reference='HEAD'):
        """Returns some metadata about the given commit reference.

        For now only the commit id and the timestamp are returned.
        """
        sha = self._resolve_reference(reference)
        commit = self.lookup(sha)
        parents = commit.parents
        an, ae, ad = commit.author
        cn, ce, cd = commit.committer

        return {
            'tree': commit.tree.sha,
            'parent': parents[0].sha if parents else None,
            'author': ('%s <%s>' % (an, ae), datetime.fromtimestamp(ad)),
            'committer': ('%s <%s>' % (cn, ce), datetime.fromtimestamp(cd)),
            'message': commit.message}


    def is_available(self):
        """Returns True if we are in a git working directory, False otherwise.
        """
        try:
            self.repo
        except GitError:
            return False
        return True



def init_worktree(path):
    init_repository(path, False)
    return Worktree(path)