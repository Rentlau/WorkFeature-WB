# -*- coding: utf-8 -*-
"""
***************************************************************************
*   This file is part of Work Feature workbench                           *
*                                                                         *
*   Copyright (c) 2017-2019 <rentlau_64>                                  *
***************************************************************************
Set of functions to use for tests
"""
import os
import FreeCAD as App
import FreeCADGui as Gui


def saveImage(m_image):
    if os.path.isfile(m_image):
        os.unlink(m_image)
    Gui.activeDocument().activeView().saveImage(m_image, 869, 590, 'Current')
    assert os.path.isfile(m_image)


def saveFile(doc_name, m_file):
    if os.path.isfile(m_file):
        os.unlink(m_file)
    App.getDocument(doc_name).saveAs(m_file)
    App.getDocument(doc_name).save()
    Gui.SendMsgToActiveView("Save")
    assert os.path.isfile(m_file)


def closeDoc(doc_name):
    App.closeDocument(doc_name)
    App.setActiveDocument("")
    App.ActiveDocument = None
    Gui.ActiveDocument = None


def imagesCmp(img1, img2):
    """ Check if 2 images are equals.
    """
    import cv2
    import numpy as np

    if os.path.isfile(img1):
        m_img1 = cv2.imread(img1)
    else:
        raise Exception(
            "No Image file {0:s} !".format(img1))
    if os.path.isfile(img2):
        m_img2 = cv2.imread(img2)
    else:
        raise Exception(
            "No Image file {0:s} !".format(img2))

    if m_img1.shape == m_img2.shape:
        # The images have same size and channels
        difference = cv2.subtract(m_img2, m_img1)
        b, g, r = cv2.split(difference)
        if cv2.countNonZero(b) == 0 and cv2.countNonZero(
                g) == 0 and cv2.countNonZero(r) == 0:
            # The images are completely Equal
            return True
    return False
