import sys

from functions import copy_dir, generate_pages_recursive


def main():
    basepath = sys.argv[1] if len(sys.argv) >= 2 else "/"
    copy_dir("static", "docs")
    generate_pages_recursive("content", "template.html", "docs", basepath)


if __name__ == "__main__":
    main()
