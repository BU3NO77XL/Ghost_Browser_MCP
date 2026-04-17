"""Tests for file-based asset downloading."""

from types import SimpleNamespace

import pytest


@pytest.mark.asyncio
async def test_download_element_assets_to_folder_writes_data_url(monkeypatch, tmp_path):
    from core import file_based_element_cloner as module
    from core.file_based_element_cloner import FileBasedElementCloner

    async def fake_extract_assets(*args, **kwargs):
        return {
            "images": [
                {
                    "src": "data:image/png;base64,iVBORw0KGgo=",
                    "alt": "tiny png",
                }
            ],
            "background_images": [],
            "fonts": {"font_faces": []},
            "icons": [],
            "videos": [],
            "audio": [],
            "loaded_resources": [
                {
                    "url": "data:image/png;base64,iVBORw0KGgo=",
                    "initiator_type": "img",
                }
            ],
        }

    monkeypatch.setattr(module.element_cloner, "extract_element_assets", fake_extract_assets)

    cloner = FileBasedElementCloner()
    tab = SimpleNamespace(url="https://example.com/page")

    result = await cloner.download_element_assets_to_folder(
        tab,
        selector="body",
        output_dir=str(tmp_path),
        include_backgrounds=False,
        include_fonts=False,
        include_icons=False,
        include_media=False,
    )

    assert result["summary"]["downloaded_count"] == 1
    assert (tmp_path / "manifest.json").exists()
    assert len(list((tmp_path / "images").iterdir())) == 1


def test_loaded_resource_iterator_respects_include_flags():
    from core.file_based_element_cloner import FileBasedElementCloner

    asset_data = {
        "loaded_resources": [
            {"url": "https://example.com/image.png", "initiator_type": "img"},
            {"url": "https://example.com/font.woff2", "initiator_type": "css"},
            {"url": "https://example.com/site.css", "initiator_type": "link"},
            {"url": "https://example.com/video.mp4", "initiator_type": "video"},
        ]
    }

    assets = list(
        FileBasedElementCloner()._iter_loaded_resource_urls(
            asset_data,
            include_images=False,
            include_fonts=True,
            include_media=False,
            include_stylesheets=False,
        )
    )

    assert [asset["category"] for asset in assets] == ["fonts"]
