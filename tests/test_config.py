"""Tests for vcspull configuration format."""
import pathlib
import typing as t

import pytest

from vcspull import config

if t.TYPE_CHECKING:
    from vcspull.types import ConfigDict


class LoadYAMLFn(t.Protocol):
    """Typing for load_yaml pytest fixture."""

    def __call__(
        self,
        content: str,
        dir: str = "randomdir",
        filename: str = "randomfilename.yaml",
    ) -> tuple[pathlib.Path, list[t.Union[t.Any, pathlib.Path]], list["ConfigDict"]]:
        """Callable function type signature for load_yaml pytest fixture."""
        ...


@pytest.fixture
def load_yaml(tmp_path: pathlib.Path) -> LoadYAMLFn:
    """Return a yaml loading function that uses temporary directory path."""

    def fn(
        content: str, dir: str = "randomdir", filename: str = "randomfilename.yaml"
    ) -> tuple[pathlib.Path, list[pathlib.Path], list["ConfigDict"]]:
        """Return vcspull configurations and write out config to temp directory."""
        _dir = tmp_path / dir
        _dir.mkdir()
        _config = _dir / filename
        _config.write_text(content, encoding="utf-8")

        configs = config.find_config_files(path=_dir)
        repos = config.load_configs(configs, cwd=_dir)
        return _dir, configs, repos

    return fn


def test_simple_format(load_yaml: LoadYAMLFn) -> None:
    """Test simple configuration YAML file for vcspull."""
    dir, _, repos = load_yaml(
        """
vcspull:
  libvcs: git+https://github.com/vcs-python/libvcs
   """
    )

    assert len(repos) == 1
    repo = repos[0]

    assert dir / "vcspull" == repo["dir"].parent
    assert dir / "vcspull" / "libvcs" == repo["dir"]


def test_relative_dir(load_yaml: LoadYAMLFn) -> None:
    """Test configuration files for vcspull support relative directories."""
    dir, _, repos = load_yaml(
        """
./relativedir:
  docutils: svn+http://svn.code.sf.net/p/docutils/code/trunk
   """
    )

    config_files = config.find_config_files(path=dir)
    repos = config.load_configs(config_files, dir)

    assert len(repos) == 1
    repo = repos[0]

    assert dir / "relativedir" == repo["dir"].parent
    assert dir / "relativedir" / "docutils" == repo["dir"]
