import language_check, sys, os


def autocorrect(text):
    return language_check.correct(text, language_check.LanguageTool("en-US").check(
        text))

if __name__ == '__main__':
    args = sys.argv[1:]
    filepath = args[0]
    abspath = os.path.abspath(filepath)
    if os.path.exists(abspath):
        with open(abspath, 'r+') as f:
            lines = f.readlines()
            corrected = []
            for line in lines:
                corrected.append(autocorrect(line))
            f.seek(0)
            f.writelines(corrected)
            f.truncate()
    else:
        print("Path Error: path does not exist;\n\t please check the path to the file is correct.")
    sys.exit()

