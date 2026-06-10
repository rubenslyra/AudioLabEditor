from presentation.splash import SplashScreen


class _DummyWidget:
    def __init__(self):
        self.exists = True
        self.destroy_calls = 0
        self.set_calls = []
        self.config_calls = []

    def winfo_exists(self):
        return self.exists

    def destroy(self):
        self.destroy_calls += 1
        self.exists = False

    def set(self, value):
        self.set_calls.append(value)

    def configure(self, **kwargs):
        self.config_calls.append(kwargs)


class _DummyMaster:
    def __init__(self):
        self.update_calls = 0
        self.update_idletasks_calls = 0

    def update(self):
        self.update_calls += 1

    def update_idletasks(self):
        self.update_idletasks_calls += 1


def test_set_progress_is_ignored_after_close():
    master = _DummyMaster()
    splash = SplashScreen.__new__(SplashScreen)
    splash._master = master
    splash._closed = False
    splash.frame = _DummyWidget()
    splash.progress_bar = _DummyWidget()
    splash.status_label = _DummyWidget()

    splash.close()
    splash.set_progress(0.99, "Carregando aba")

    assert splash.progress_bar.set_calls == []
    assert splash.status_label.config_calls == []
    assert master.update_calls == 0
    assert master.update_idletasks_calls == 1


def test_close_is_idempotent():
    master = _DummyMaster()
    splash = SplashScreen.__new__(SplashScreen)
    splash._master = master
    splash._closed = False
    splash.frame = _DummyWidget()
    splash.progress_bar = _DummyWidget()
    splash.status_label = _DummyWidget()

    splash.close()
    splash.close()

    assert splash.frame.destroy_calls == 1
    assert master.update_idletasks_calls == 1
