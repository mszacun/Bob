import os
import os.path

from npyscreen import FileSelector


class NotHiddenFileSelector(FileSelector):
    def update_grid(self,):
        if self.value:
            self.value = os.path.expanduser(self.value)

        if not os.path.exists(self.value):
            self.value = os.getcwd()

        if os.path.isdir(self.value):
            working_dir = self.value
        else:
            working_dir = os.path.dirname(self.value)

        self.wStatus1.value = working_dir

        file_list = []
        if os.path.abspath(os.path.join(working_dir, '..')) != os.path.abspath(working_dir):
            file_list.append('..')
        try:
            file_list.extend([os.path.join(working_dir, fn) for fn in os.listdir(working_dir) if not fn.startswith('.')])
        except OSError:
            utilNotify.notify_wait(title="Error", message="Could not read specified directory.")
        # DOES NOT CURRENTLY WORK - EXCEPT FOR THE WORKING DIRECTORY.  REFACTOR.
        new_file_list= []
        for f in file_list:
            f = os.path.normpath(f)
            if os.path.isdir(f):
                new_file_list.append(f + os.sep)
            else:
                new_file_list.append(f) # + "*")
        file_list = new_file_list
        del new_file_list

        # sort Filelist
        file_list.sort()
        if self.sort_by_extension:
            file_list.sort(key=self.get_extension)
        file_list.sort(key=os.path.isdir, reverse=True)

        self.wMain.set_grid_values_from_flat_list(file_list, reset_cursor=False)

        self.display()


def selectFile(starting_value=None, *args, **keywords):
    F = NotHiddenFileSelector(*args, **keywords)
    F.set_colors()
    F.wCommand.show_bold = True
    if starting_value:
        if not os.path.exists(os.path.abspath(os.path.expanduser(starting_value))):
            F.value = os.getcwd()
        else:
            F.value = starting_value
            F.wCommand.value = starting_value
    else:
        F.value = os.getcwd()
    F.update_grid()
    F.display()
    F.edit()
    return F.wCommand.value
