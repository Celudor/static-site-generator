from functions import copy_dir, generate_page


def main():
    copy_dir("static", "public")
    generate_page("content/index.md", "template.html", "public/index.html")


if __name__ == "__main__":
    main()
