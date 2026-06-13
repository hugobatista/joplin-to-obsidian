from pathlib import Path

import pytest


@pytest.fixture
def vault(tmp_path: Path) -> Path:
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()
    res_dir = vault_dir / "_resources"
    res_dir.mkdir()
    (res_dir / "image.png").write_text("png")
    (res_dir / "doc.pdf").write_text("pdf")
    return vault_dir


@pytest.fixture
def md_file(vault: Path) -> Path:
    md = vault / "note.md"
    md.write_text("""---
title: Test
---

Hello ![](../_resources/image.png)
""")
    return md


@pytest.fixture
def md_with_html(vault: Path) -> Path:
    md = vault / "html_note.md"
    md.write_text("""---
title: HTML
---

<img src="../_resources/image.png" alt="img" />
""")
    return md


@pytest.fixture
def md_with_location(vault: Path) -> Path:
    md = vault / "location_note.md"
    md.write_text("""---
title: Located
latitude: 40.7128
longitude: -74.0060
altitude: 10.5
---

Some content
""")
    return md


@pytest.fixture
def md_trailing_name(vault: Path) -> Path:
    md = vault / "note_.md"
    md.write_text("content")
    return md


@pytest.fixture
def nested_vault(tmp_path: Path) -> Path:
    vault_dir = tmp_path / "nested_vault"
    vault_dir.mkdir()
    res_dir = vault_dir / "_resources"
    res_dir.mkdir()
    (res_dir / "img.png").write_text("img")
    sub = vault_dir / "subfolder"
    sub.mkdir()
    (sub / "sub_note.md").write_text("""---
title: Sub
---

![](../_resources/img.png)
""")
    sub_res = sub / "_resources"
    sub_res.mkdir()
    (sub_res / "existing.png").write_text("existing")
    return vault_dir
