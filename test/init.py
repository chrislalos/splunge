from splunge.cli import AppInfo

def test_new_app_info():
    name = "hello"
    bind = "0.0.0.0:13001"
    appInfo = AppInfo(name=name, bind=bind)
    assert name == appInfo.name
    assert bind == appInfo.bind
