import sublime
import sublime_plugin


class SbpToggleCommentCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        self.view.run_command("toggle_comment")
        self.view.run_command("sbp_cancel_mark")


# Remove any existing marks
#
class SbpCancelMarkCommand(sublime_plugin.TextCommand):

    def run(self, edit, **args):
        cursor = self.view.sel()[0]
        self.view.erase_regions("mark")
        self.view.sel().clear()
        self.view.sel().add(sublime.Region(cursor.end(), cursor.end()))


class SbpSetMarkCommand(sublime_plugin.TextCommand):
    def run(self, edit):

        m = self.view.get_regions("mark")
        self.view.run_command("sbp_cancel_mark")
        mark = [s for s in self.view.sel()]

        if m != mark:
            self.view.add_regions("mark", mark, "mark", "dot",
                sublime.HIDDEN | sublime.PERSISTENT)


class SbpSwapWithMarkCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        old_mark = self.view.get_regions("mark")

        mark = [s for s in self.view.sel()]
        self.view.add_regions("mark", mark, "mark", "dot",
            sublime.HIDDEN | sublime.PERSISTENT)

        if len(old_mark):
            self.view.sel().clear()
            for r in old_mark:
                self.view.sel().add(r)


class SbpSelectToMarkCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        mark = self.view.get_regions("mark")

        num = min(len(mark), len(self.view.sel()))

        regions = []
        for i in range(num):
            regions.append(self.view.sel()[i].cover(mark[i]))

        for i in range(num, len(self.view.sel())):
            regions.append(self.view.sel()[i])

        self.view.sel().clear()
        for r in regions:
            self.view.sel().add(r)


class SbpDeleteToMark(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.run_command("copy")
        self.view.run_command("sbp_add_to_kill_ring", {"forward": False})
        #self.view.run_command("sbp_select_to_mark")
        self.view.run_command("left_delete")
        self.view.run_command("sbp_cancel_mark")


#
# If a mark has been set, color the region between the mark and the point
#
class SbpEmacsMarkDetector(sublime_plugin.EventListener):

    def __init__(self, *args, **kwargs):
        sublime_plugin.EventListener.__init__(self, *args, **kwargs)

    # When text is modified, we cancel the mark.
    def on_modified(self, view):
        #view.erase_regions("mark")
        pass

    def on_selection_modified(self, view):
        mark = view.get_regions("mark")
        num = min(len(mark), len(view.sel()))
        regions = []

        for i in range(num):
            regions.append(view.sel()[i].cover(mark[i]))

        for i in range(num, len(view.sel())):
            regions.append(view.sel()[i])

        view.sel().clear()
        for r in regions:
            view.sel().add(r)

    def on_query_context(self, view, key, operator, operand, match_all):
        if key == "sbp_emacs_has_mark":
            if operator == sublime.OP_EQUAL:
                return len(view.get_regions("mark")) > 0
