import sublime
import sublime_plugin
import os
import os.path
import subprocess

class TortoiseGitCommand(sublime_plugin.WindowCommand):
    def run(self, cmd, paths=None, isHung=False):
        if paths is not None:
            for index, path in enumerate(paths):
              if "${PROJECT_PATH}" in path:
                  project_data  = sublime.active_window().project_data()
                  project_folder = project_data['folders'][0]['path']
                  path = path.replace("${PROJECT_PATH}", project_folder);
                  paths[index] = path
        dir = self.get_path(paths)

        if not dir:
            return

        settings = sublime.load_settings('TortoiseGIT.sublime-settings')
        tortoiseproc_path = settings.get('tortoisegit_proc_path')
        pathEncoding = settings.get('pathEncoding')

        if tortoiseproc_path is None or not os.path.isfile(tortoiseproc_path):
            sublime.error_message('can\'t find TortoiseGitProc.exe,'
                ' please config setting file' '\n   --sublime-TortoiseGit')
            return

        closeonend = settings.get('close_on_end')
        if closeonend is None:
            closeonend = 0

        cmd = '"' + tortoiseproc_path + '"' + ' /command:' + cmd + ' /closeonend:%s' % closeonend + ' /path:"%s"' % dir
        # print (cmd)

        proce = subprocess.Popen(cmd.encode(pathEncoding) if pathEncoding else cmd , stdout=subprocess.PIPE)

        # This is required, cause of ST must wait TortoiseGit update then revert
        # the file. Otherwise the file reverting occur before Git update, if the
        # file changed the file content in ST is older.
        if isHung:
            proce.communicate()

    def get_path(self, paths):
        path = None
        if paths:
            path = '*'.join(paths)
        else:
            view = sublime.active_window().active_view()
            path = view.file_name() if view else None

        return path

    def get_setting(self):
        return sublime.load_settings('TortoiseGIT.sublime-settings')


class TortoiseGITBashCommand(TortoiseGitCommand):
    def run(self, paths=None, isHung=False):
        dir = self.get_path(paths)
        # print (paths)

        if not dir:
            return

        settings = sublime.load_settings('TortoiseGIT.sublime-settings')
        gitbash_path = settings.get('git_bash_path')

        if gitbash_path is None or not os.path.isfile(gitbash_path):
            sublime.error_message(''.join(['can\'t find sh.exe (gitbash),',
                ' please config setting file', '\n   --sublime-TortoiseGIT']))
            raise

        command = 'cd %s & "%s" --login -i' % (dir, gitbash_path)
        os.system(command)


class MutatingTortoiseGitCommand(TortoiseGitCommand):
    def run(self, cmd, paths=None):
        TortoiseGitCommand.run(self, cmd, paths, True)

        self.view = sublime.active_window().active_view()
        row, col = self.view.rowcol(self.view.sel()[0].begin())
        self.lastLine = str(row + 1);
        sublime.set_timeout(self.revert, 100)

    def revert(self):
        self.view.run_command('revert')
        sublime.set_timeout(self.revertPoint, 600)

    def revertPoint(self):
        self.view.window().run_command('goto_line', {'line':self.lastLine})


class GitCloneCommand(MutatingTortoiseGitCommand):
    def run(self, paths=None):
        MutatingTortoiseGitCommand.run(self, 'clone', paths)

class GitSwitchCommand(TortoiseGitCommand):
    def run(self, paths=None):
        TortoiseGitCommand.run(self, 'switch', paths)

class GitStatusCommand(TortoiseGitCommand):
    def run(self, paths=None):
        TortoiseGitCommand.run(self, 'repostatus', paths)

class GitCommitCommand(TortoiseGitCommand):
    def run(self, paths=None):
        TortoiseGitCommand.run(self, 'commit', paths)

class GitPushCommand(TortoiseGitCommand):
	def run(self, paths=None):
		TortoiseGitCommand.run(self, 'push', paths)

class GitFetchCommand(TortoiseGitCommand):
    def run(self, paths=None):
        TortoiseGitCommand.run(self, 'fetch', paths)

class GitPullCommand(TortoiseGitCommand):
	def run(self, paths=None):
		TortoiseGitCommand.run(self, 'pull', paths)

class GitBashCommand(TortoiseGITBashCommand):
    def run(self, paths=None):
        TortoiseGITBashCommand.run(self, paths)

    # def is_visible(self, paths=None):
    #     print (paths)
    #     if paths is None:
    #         return True
    #     else:
    #         return os.path.isdir(paths)


class GitRevertCommand(MutatingTortoiseGitCommand):
    def run(self, paths=None):
        MutatingTortoiseGitCommand.run(self, 'revert', paths)


class GitLogCommand(TortoiseGitCommand):
    def run(self, paths=None):
        TortoiseGitCommand.run(self, 'log', paths)


class GitDiffCommand(TortoiseGitCommand):
    def run(self, paths=None):
        TortoiseGitCommand.run(self, 'diff', paths)


class GitMergeCommand(TortoiseGitCommand):
    def run(self, paths=None):
        TortoiseGitCommand.run(self, 'merge', paths)


class GitBlameCommand(TortoiseGitCommand):
    def run(self, paths=None):
        view = sublime.active_window().active_view()
        row = view.rowcol(view.sel()[0].begin())[0] + 1

        TortoiseGitCommand.run(self, 'blame /line:' + str(row), paths)

    def is_visible(self, paths=None):
        file = self.get_path(paths)
        return os.path.isfile(file) if file else False
