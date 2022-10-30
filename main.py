from time import sleep

from functions import run, main_remove


if __name__ == '__main__':
    run('tiger')
    path_tiger = 'dataset/tiger'
    main_remove(path_tiger)
    sleep(10)
    print('\n\n')
    run('leopard')
    path_leopard = 'dataset/leopard'
    main_remove(path_leopard)
    print('the end')