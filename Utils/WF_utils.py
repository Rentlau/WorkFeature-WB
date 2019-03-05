# -*- coding: utf-8 -*-


def print_attributes(obj, doc=False):
    """ Print all the attributes of this object and their value.
    """
    __m_type = obj.__class__.__name__
    print('* Attributes print for ' + str(__m_type) + '*')
    for names in dir(obj):
        attr = getattr(obj, names)
        if not callable(attr):
            if doc:
                print(str(names), ':', str(attr))
            else:
                print(str(names))


def print_methods(obj, doc=False):
    """ Print all the methods of this object and their doc string.
    """
    __m_type = obj.__class__.__name__
    print('\n* Methods print for ' + str(__m_type) + '*')
    for names in dir(obj):
        attr = getattr(obj, names)
        if callable(attr):
            if doc:
                print(str(names), ':', str(attr.__doc__))
            else:
                print(str(names))


def linkSubList_convertToOldStyle(references):
    """("input: [(obj1, (sub1, sub2)), (obj2, (sub1, sub2))]\n"
    "output: [(obj1, sub1), (obj1, sub2), (obj2, sub1), (obj2, sub2)]")"""
    result = []
    for tup in references:
        if type(tup[1]) is tuple or type(tup[1]) is list:
            for subname in tup[1]:
                result.append((tup[0], subname))
            if len(tup[1]) == 0:
                result.append((tup[0], ''))
        else:
            # old style references, no conversion required
            result.append(tup)
    return result