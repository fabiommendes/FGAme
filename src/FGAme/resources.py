'''
Gerencia os recursos disponíveis para o jogo na forma de arquivos.

Por padrão, a FGAme assume que os arquivos estão numa pasta chamada
``resources`` junto ao módulo principal de jogo.

'''

import os
import sys
from FGAme import draw

IMG_PRIORITIES = ['.png', '.gif', '.bmp', '.jpeg', '.jpg', '.tiff']
SND_PRIORITIES = ['.wav', '.ogg', '.mp3']
MEDIA_PRIORITIES = IMG_PRIORITIES + SND_PRIORITIES


class ResourceManager(object):

    def __init__(self, root=None):
        self._root = root

    @property
    def root(self):
        if self._root is not None:
            return self._root

        root = self.__find_root()
        if isinstance(root, str):
            root = os.path.expanduser(root)
            root = os.path.expandvars(root)
        self._root = root
        return root

    def get_root(self):
        '''Retorna o valor de root. Produz um RuntimeError caso root não tenha
        sido encontrado
        '''

        root = self.root
        if root is None:
            raise RuntimeError('could not find resource root')
        return root

    def __find_root(self):
        # Tenta encontrar o root em um dos caminhos especificados

        return self.__try_find_root_methods([
            self.__find_root_from_environ,
            self.__find_root_from_main,
        ])

    def __find_root_from_path(self, path):
        # Inspeciona caminho dado e tenta encontrar a pasta resources a partir
        # deste caminho. Caso não encontre, retorne None

        base = 'resources'
        while base:
            resources = os.path.join(path, 'resources')
            if os.path.exists(resources):
                return resources

            path, base = os.path.split(path)

    def __find_root_from_main(self):
        # Procura root a partir do pacote '__main__'

        main = sys.modules['__main__']
        path = os.path.split(main.__file__)[0]
        path = self.__find_root_from_path(path)
        if path is not None:
            return path

    def __find_root_from_environ(self):
        # Procura na variável de estado RESOURCES_PATH

        return os.environ.get('RESOURCES_PATH')

    def __try_find_root_methods(self, funcs):
        # Retorna o primeiro valor bem sucedido na lista de funções que
        # tentam encontrar a pasta resources

        for func in funcs:
            out = func()
            if out is not None:
                return out

    def find_data(self, name, mode='r', encoding=None, priorities=None):
        '''Retorna um objeto do tipo arquivo com o primeiro arquivo encontrado
        compatível com o nome dade.'''

        path = self.find_path(name, priorities)
        return open(self.get_data(path), mode, encoding=encoding)

    def find_path(self, name, priorities=None):
        '''Retorna o caminho para o arquivo de maior prioridade com o nome
        compatível com o valor fornecido
        '''

        root = self.get_root()
        root_size = len(root) + 1
        for ext in priorities:
            path = os.path.join(root, name + ext)
            if os.path.exists(path):
                return path[root_size:]
        raise RuntimeError('could not find %s' % os.path.join(root, name))

    def find_image(self, name):
        '''Retorna a imagem de maior prioridade com o nome compatível com o
        valor fornecido
        '''

        path = self.find_path(name, priorities=IMG_PRIORITIES)
        abspath = os.path.join(self.root, path)
        return draw.get_texture(abspath)

    def find_animation(self, name):
        '''Retorna a animação caminho para o arquivo de maior prioridade com o
        nome compatível com o valor fornecido
        '''

        return self.find_path(name, priorities=IMG_PRIORITIES)

    def find_abspath(self, path, priorities=None):
        '''Retorna o caminho absoluto de "path" no sistema de arquivos'''

        path = self.find_path(path, priorities)
        return os.path.join(self.root, path)


resources = ResourceManager()
