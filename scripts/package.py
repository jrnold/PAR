"""Stage `package`: build the data package and the Zenodo zip files."""

from par.package import build_package
from par.tables import load_tables

if __name__ == "__main__":
    build_package(load_tables())
