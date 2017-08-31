from support import version

__author__ = version.get_author()
__version__ = version.get_version()

alph = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']

class convert():
    def __init__(self, set=alph):
        self.__set = set
        self.__set_len = len(self.__set)
    def tran(self, num_val):
        try:
            return self.__set[num_val]
        except:
            ##not implemented
            return -1
