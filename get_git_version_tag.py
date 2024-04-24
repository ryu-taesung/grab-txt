import subprocess

def get_git_version_tag():
    try:
      output = subprocess.check_output(['git', 'describe', '--always']).decode('ASCII').replace('\n','')
    except:
      output = "version ERR"
    return output

def write_git_version_tag():
    try:
      output = subprocess.check_output(['git', 'describe', '--always']).decode('ASCII').replace('\n','')
    except:
      output = "version ERR"
    with open('version.txt', 'w') as file:
        file.write(output)

if __name__ == '__main__':
    get_git_version_tag()
