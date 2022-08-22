from os import scandir, getcwd

def print_dir(dir=getcwd()+'/',fold=''):
    dic = {}
    itr = scandir(dir)
    for e in itr:
        if e.is_file():
            dic[e.name] = fold+e.path[len(dir):]
        elif e.is_dir():
            buff = print_dir(dir=e.path,fold=e.name+'/')
            dic.update(buff)
    return dic

def get_dir(dir=getcwd()):
    return scandir(dir)

if __name__ == '__main__':
    dic = print_dir()
    for val in dic.keys():
        print(val+' | '+dic[val])