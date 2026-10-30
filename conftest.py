_pruebas_con_regla = []


def pytest_collection_modifyitems(items):
    _pruebas_con_regla.clear()
    for item in items:
        marker = item.get_closest_marker("regla")
        if marker and marker.args:
            reglas = ", ".join(marker.args)
            _pruebas_con_regla.append((item.nodeid, reglas))


def pytest_terminal_summary(terminalreporter):
    if not _pruebas_con_regla:
        return
    terminalreporter.write_sep("=", "reglas de negocio cubiertas")
    for nodeid, reglas in _pruebas_con_regla:
        terminalreporter.write_line(f"[regla: {reglas}] {nodeid}")
