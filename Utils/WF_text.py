# -*- coding: utf-8 -*-
"""
"""
import os.path

def read_from_file(filename):
    """ Read the complete ASCII file *filename* (if possible) into a unique 
    string and return the string 
    (or None in case of error).

    Controls are done on *filename*.
    
    *filename* : (string) full path name.
    """         
    if filename and os.path.exists(filename):
        try:
            __m_f=open(filename,'r')
            # read the complete ASCII file if possible into a unique string
            try:
                m_string = __m_f.read()
            except:
                __m_f.close()
                print "\nERROR : The file " + str(filename) + \
                  " cannot be fully read !"                    
                return None
            finally:
                __m_f.close()
            __m_f.close()
            return m_string
        except:
            print "\nERROR : The file " + str(filename) + \
              " cannot be opened in read mode !"
            return None
    else:
        if os.path.exists(filename) == False:
            print "\nERROR : " + str(filename) + " not a valid file !"                  
        return None


def read_from_file_to_list(filename):
    """ Read the complete ASCII file *filename* (if possible) into a unique 
    list of strings and return the list 
    (or None in case of error).

    Controls are done on *filename*.
    
    *filename* : (string) full path name.
    """         
    if filename and os.path.exists(filename):
        try:
            __m_f=open(filename,'r')
            # read the complete ASCII file if possible into a unique list of strings
            try:
                #m_strings = __m_f.readlines()
                m_strings = __m_f.read().splitlines()
            except:
                __m_f.close()
                print "\nERROR : The file " + str(filename) + \
                  " cannot be fully read !"                    
                return None
            finally:
                __m_f.close()
            __m_f.close()
            return m_strings
        except:
            print "\nERROR : The file " + str(filename) + \
              " cannot be opened in read mode !"
            return None
    else:
        if os.path.exists(filename) == False:
            print "\nERROR : " + str(filename) + " not a valid file !"                  
        return None
    
def write_into_file(filename=None, text=None):
    """ Write the text into an ASCII file.
    
    Return True if success, false if not.
    
    *filename* : (string) full path name.
    
    *text* : (string) the text to write.
    """
    if filename != None and text != None:
        try:
            __m_f=open(filename,'w')
            __m_f.write(text)
            __m_f.close()
            return True
        except:
            print "\nERROR : The file " + str(filename) + \
              " cannot be opened in write mode !"
            return False
    else:
        return False
    
  
def append_into_file(filename=None,  text="" ):
    """ Print text on screen or add text at the end of an existing ASCII text file.
    
    *filename* : (string) full path name.

    *text*  : (string) the text to add at the end of the file.
    """
    if text.__class__.__name__ != 'str': 
        return None
    if filename and os.path.exists(filename):
        try:
            __m_f=open(filename,'r+')
            __m_f.readlines()
            __m_f.write(text+'\n')
            __m_f.close()
        except:
            print "\nERROR : The file " + str(filename) + \
              " can not be opened for append mode !"
            return False
    else:
        print text +'\n' 