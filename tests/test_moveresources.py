from pathlib import Path

from joplin_to_obsidian.moveresources import move_resources


class TestMoveResources:
    def test_copies_resource_to_local_dir(self, vault: Path) -> None:
        md = vault / "note.md"
        md.write_text("![](../_resources/image.png)")
        move_resources(vault)
        assert (vault / "_resources" / "image.png").exists()

    def test_updates_markdown_link(self, vault: Path) -> None:
        md = vault / "note.md"
        md.write_text("![](../_resources/image.png)")
        move_resources(vault)
        assert "![](./_resources/image.png)" in md.read_text()

    def test_updates_html_img_src(self, vault: Path) -> None:
        md = vault / "note.md"
        md.write_text('<img src="../_resources/image.png" />')
        move_resources(vault)
        assert 'src="./_resources/image.png"' in md.read_text()

    def test_deletes_originals_after_copy(self, nested_vault: Path) -> None:
        move_resources(nested_vault)
        root_res = nested_vault / "_resources"
        assert not (root_res / "img.png").exists()

    def test_handles_nested_structure(self, nested_vault: Path) -> None:
        move_resources(nested_vault)
        sub_note = nested_vault / "subfolder" / "sub_note.md"
        assert "![](./_resources/img.png)" in sub_note.read_text()
        local_res = nested_vault / "subfolder" / "_resources"
        assert (local_res / "img.png").exists()
        assert (local_res / "existing.png").exists()

    def test_handles_same_destination(self, vault: Path) -> None:
        md = vault / "note.md"
        md.write_text("![](../_resources/image.png)")
        move_resources(vault)
        assert (vault / "_resources" / "image.png").exists()

    def test_no_resources_to_move(self, tmp_path: Path) -> None:
        d = tmp_path / "empty"
        d.mkdir()
        (d / "note.md").write_text("no resources")
        move_resources(d)
        assert not (d / "_resources").exists()

    def test_skips_missing_resource(self, vault: Path) -> None:
        md = vault / "bad_ref.md"
        md.write_text("![](../_resources/missing.png)")
        move_resources(vault)
        assert not (vault / "_resources" / "missing.png").exists()

    def test_handles_invalid_resource_path(self, vault: Path) -> None:
        md = vault / "invalid.md"
        md.write_text("![](../_resources/../outside.png)")
        move_resources(vault)
        assert "![](../_resources/../outside.png)" in md.read_text()

    def test_handles_html_invalid_resource_path(self, vault: Path) -> None:
        md = vault / "invalid_html.md"
        md.write_text('<img src="../_resources/../outside.png" />')
        move_resources(vault)
        assert '../_resources/../outside.png"' in md.read_text()

    def test_handles_html_missing_resource(self, vault: Path) -> None:
        md = vault / "html_missing.md"
        md.write_text('<img src="../_resources/nope.jpg" />')
        move_resources(vault)
        assert not (vault / "_resources" / "nope.jpg").exists()

    def test_handles_linked_image_not_markdown(self, vault: Path) -> None:
        md = vault / "linked.md"
        md.write_text("[![](../_resources/image.png)](http://example.com)")
        move_resources(vault)
        assert "![](./_resources/image.png)" in md.read_text()

    def test_dry_run_no_changes(self, nested_vault: Path) -> None:
        move_resources(nested_vault, dry_run=True)
        sub_note = nested_vault / "subfolder" / "sub_note.md"
        root_res = nested_vault / "_resources"
        assert "![](../_resources/img.png)" in sub_note.read_text()
        assert (root_res / "img.png").exists()

    def test_dry_run_resource_already_at_target(self, vault: Path) -> None:
        (vault / "note.md").write_text("![](../_resources/image.png)")
        move_resources(vault, dry_run=True)
        assert (vault / "_resources" / "image.png").exists()

    def test_skips_invalid_ref_among_valid(self, vault: Path) -> None:
        md = vault / "mixed.md"
        md.write_text("![](../_resources/image.png)\n![](../_resources/missing.png)")
        move_resources(vault)
        assert (vault / "_resources" / "image.png").exists()

    def test_handles_copy_error(self, nested_vault: Path, monkeypatch) -> None:
        import shutil

        def broken_copy(*args, **kwargs):
            raise OSError("copy failed")

        monkeypatch.setattr(shutil, "copy2", broken_copy)
        move_resources(nested_vault)

    def test_handles_delete_error(self, nested_vault: Path, monkeypatch) -> None:
        import os as os_module

        original_unlink = os_module.unlink

        def broken_unlink(path, *args, **kwargs):
            if "img.png" in str(path):
                raise OSError("delete failed")
            return original_unlink(path, *args, **kwargs)

        monkeypatch.setattr(os_module, "unlink", broken_unlink)
        move_resources(nested_vault)
