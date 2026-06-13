from pathlib import Path

from joplin_to_obsidian.cleanup import (
    remove_empty_resources_dirs,
    remove_location_frontmatter,
    remove_trailing_underscores,
)


class TestRemoveTrailingUnderscores:
    def test_renames_file_with_trailing_underscore(self, vault: Path) -> None:
        f = vault / "note_.md"
        f.write_text("content")
        remove_trailing_underscores(vault)
        assert not (vault / "note_.md").exists()
        assert (vault / "note.md").exists()

    def test_renames_dir_with_trailing_underscore(self, vault: Path) -> None:
        dir_ = vault / "folder_"
        dir_.mkdir()
        remove_trailing_underscores(vault)
        assert not (vault / "folder_").exists()
        assert (vault / "folder").exists()

    def test_skips_underscore_only_name(self, vault: Path) -> None:
        f = vault / "_.md"
        f.write_text("x")
        remove_trailing_underscores(vault)
        assert f.exists()

    def test_avoids_file_collision_with_counter(self, vault: Path) -> None:
        (vault / "note.md").write_text("existing")
        f = vault / "note_.md"
        f.write_text("underscore")
        remove_trailing_underscores(vault)
        new = vault / "note_1.md"
        assert new.exists()
        assert new.read_text() == "underscore"

    def test_avoids_dir_collision_with_counter(self, vault: Path) -> None:
        (vault / "folder").mkdir()
        dir_ = vault / "folder_"
        dir_.mkdir()
        remove_trailing_underscores(vault)
        assert (vault / "folder_1").exists()


class TestRemoveEmptyResourcesDirs:
    def test_removes_empty_dir(self, vault: Path) -> None:
        empty = vault / "sub" / "_resources"
        empty.mkdir(parents=True)
        result = remove_empty_resources_dirs(vault)
        assert empty in result

    def test_skips_non_empty_dir(self, vault: Path) -> None:
        res = vault / "_resources"
        result = remove_empty_resources_dirs(vault)
        assert res not in result

    def test_returns_empty_list_when_no_resources_dirs(self, tmp_path: Path) -> None:
        d = tmp_path / "no_res"
        d.mkdir()
        result = remove_empty_resources_dirs(d)
        assert result == []

    def test_handles_oserror(self, vault: Path, monkeypatch) -> None:
        def broken_rmdir(path):
            raise OSError("permission denied")

        monkeypatch.setattr("os.rmdir", broken_rmdir)
        empty = vault / "sub" / "_resources"
        empty.mkdir(parents=True)
        result = remove_empty_resources_dirs(vault)
        assert result == []


class TestRemoveLocationFrontmatter:
    def test_removes_location_fields(self, vault: Path) -> None:
        md = vault / "loc.md"
        md.write_text("""---
title: Located
latitude: 40.7128
longitude: -74.0060
altitude: 10.5
---

Some content
""")
        remove_location_frontmatter(vault)
        content = md.read_text()
        assert "latitude" not in content
        assert "longitude" not in content
        assert "altitude" not in content
        assert "title: Located" in content

    def test_skips_file_without_location(self, vault: Path) -> None:
        md = vault / "note.md"
        md.write_text("no frontmatter")
        before = md.read_text()
        remove_location_frontmatter(vault)
        assert md.read_text() == before

    def test_removes_frontmatter_entirely_when_empty(self, vault: Path) -> None:
        md = vault / "empty_fm.md"
        md.write_text("---\nlatitude: 1.0\n---\nbody")
        remove_location_frontmatter(vault)
        assert md.read_text() == "body"

    def test_skips_file_without_frontmatter(self, vault: Path) -> None:
        md = vault / "no_fm.md"
        md.write_text("just content")
        remove_location_frontmatter(vault)
        assert md.read_text() == "just content"

    def test_handles_markdown_extension(self, vault: Path) -> None:
        md = vault / "note.markdown"
        md.write_text("---\nlatitude: 2.0\n---\ncontent")
        remove_location_frontmatter(vault)
        assert "latitude" not in md.read_text()

    def test_handles_read_error(self, vault: Path, monkeypatch) -> None:
        md = vault / "broken.md"
        md.write_text("---\nlatitude: 1.0\n---\nbody")

        def broken_read(*args, **kwargs):
            raise OSError("read failed")

        monkeypatch.setattr(Path, "read_text", broken_read)
        remove_location_frontmatter(vault)
