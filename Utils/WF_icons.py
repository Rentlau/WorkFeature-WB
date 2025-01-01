# -*- coding: utf-8 -*-

###############
M_DEBUG = True
###############
import sys
import os.path

# get the path of the current python script    
m_current_path = os.path.realpath(__file__)
# Go up in directories once
# ./Src            
m_parent_path = os.path.dirname(m_current_path)
# ./Src/Utils
PATH_WF_UTILS = os.path.join(m_parent_path, 'Utils')
# Go up in directories once
# ./
m_parent2_path = os.path.dirname(m_parent_path)    
# ./Icons
PATH_WF_ICONS = os.path.join(m_parent2_path, 'Icons')
    
if not sys.path.__contains__(str(PATH_WF_UTILS)):
    sys.path.append(str(PATH_WF_UTILS))
    
def get_icon(icon_path, icon_name):
    """  Return the icon file or a default one if the file do not exists!
    
    The file icon_path/icon_name is assumed valid and the file must exists!
    The file must be images in svg  or xpm format
    
    *icon_path* : (string) full path name.
    *icon_name* : (string) file name.      
    """
    m_full_name = os.path.join(icon_path, icon_name)
    if m_full_name and os.path.exists(m_full_name):
        return (m_full_name)
    else :
        if M_DEBUG:
            print "DEBUG :" + str(m_full_name) + " not a valid file !"  
        return default_icon()

def default_icon():
    """ Return the icon in XMP format """
    return """
        /* XPM */
        static char *Free_Converter_com_wf_point_54933158[] = {
        /* columns rows colors chars-per-pixel */
        "32 32 95 2 ",
        "   c #01A8014100CE",
        ".  c #0BD809A30639",
        "X  c #0CB70B600909",
        "o  c #15150F0E0707",
        "O  c #11910E8F0A8A",
        "+  c #149410900B0B",
        "@  c #1C1C15950B8B",
        "#  c #181816161414",
        "$  c #1AC5196F16C1",
        "%  c #1E731C7119C4",
        "&  c #222119590C8C",
        "*  c #29281E9E0E0D",
        "=  c #2F2F22210F0F",
        "-  c #232322221F1F",
        ";  c #363528281211",
        ":  c #282727272625",
        ">  c #292928272625",
        ",  c #2D2D2C2C2B2B",
        "<  c #30302F2F2F2F",
        "1  c #3DBE3DBE3DBE",
        "2  c #464631311312",
        "3  c #4D4C37361615",
        "4  c #56553C3C1717",
        "5  c #630D45441919",
        "6  c #6CED4BCC1B1B",
        "7  c #70704E4D1C1C",
        "8  c #7A7A55551E1E",
        "9  c #434241413F3F",
        "0  c #439943994399",
        "q  c #4A4948484646",
        "w  c #549454945494",
        "e  c #5A5A5A5A5A5A",
        "r  c gray39",
        "t  c #6A846A826A7F",
        "y  c #741E73F4739E",
        "u  c #7ABA7ABA7ABA",
        "i  c #85855D5D2121",
        "p  c #89895F5F2222",
        "a  c #8C8C61612323",
        "s  c #969668682525",
        "d  c #A0A06F6F2727",
        "f  c #A8A875752929",
        "g  c #ADAD78782B2B",
        "h  c #B2B27BFC2C2C",
        "j  c #BB54821B2DFB",
        "k  c #C3C387873030",
        "l  c #C9C98C0C31B2",
        "z  c #D95997173535",
        "x  c #DF5F9B1B3737",
        "c  c #E5659F9F3838",
        "v  c #E9E9A24C398F",
        "b  c #F474A9D43C67",
        "n  c #FCE5AFA03E3C",
        "m  c #FCFCB1E04389",
        "M  c #FCFCB5014B31",
        "N  c #FCFCB7B75151",
        "B  c #FCFCB8F85454",
        "V  c #FD13BBA45B72",
        "C  c #FDFDBEFE63A3",
        "Z  c #FDFDC0C06767",
        "A  c #FDFDC2426B56",
        "S  c #FDFDC5F8740D",
        "D  c #FDFDC7C77878",
        "F  c #FDFDC9C97CEA",
        "G  c #838383838383",
        "H  c #8D8D8D8D8D8D",
        "J  c #933D933D933D",
        "K  c #9A9A9A9A9A9A",
        "L  c #A4FAA4FAA4FA",
        "P  c gray71",
        "I  c #BD12BD12BD12",
        "U  c #FDFDCD778686",
        "Y  c #FDFDCF9C8B58",
        "T  c #FDFDD1D18F8F",
        "R  c #FDFDD3059393",
        "E  c #FE30D66F9BCE",
        "W  c #FEFED972A309",
        "Q  c #FEFEDCDCAAAA",
        "!  c #FEFEDF5FB1B1",
        "~  c #FEFEE161B575",
        "^  c #FEFEE439BDBD",
        "/  c gray76",
        "(  c #CE16CE16CE16",
        ")  c #D328D328D328",
        "_  c #DD32DD32DD32",
        "`  c #FEFEE767C544",
        "'  c #FEFEEA3FCB75",
        "]  c #FEFEED42D2D2",
        "[  c #FEFEF1F1DDDD",
        "{  c #E6E6E6E6E6E6",
        "}  c #EBC6EBC6EBC6",
        "|  c #FFFFF777EB6B",
        " . c #FFFFF8F8EEEE",
        ".. c #F39DF39DF39D",
        "X. c None",
        /* pixels */
        "X.X.X.X.X.X.X.X.X.X.X.X.X.X.X.X.X.X.X.X.X.X.X.X.X.X.X.X.X.X.X.X.",
        "X.X.X.X.X.X.X.X.X.X.X.X.X...) ( _ X.X.X.X.X.X.X.X.X.X.X.X.X.X.X.",
        "X.X.X.X.X.X.X.X.X.X.) y %         X q K X.X.X.X.X.X.X.X.X.X.X.X.",
        "X.X.X.X.X.X.X.X.{ r   ; a k c c z f 5 X % P X.X.X.X.X.X.X.X.X.X.",
        "X.X.X.X.X.X.X.) $ * j n n m M M m n n v 7   y X.X.X.X.X.X.X.X.X.",
        "X.X.X.X.X.X.) O 3 b n M V C Z Z C V m n m h . y X.X.X.X.X.X.X.X.",
        "X.X.X.X.X...: 3 n n V A F Y Y U F A V m n n j   K X.X.X.X.X.X.X.",
        "X.X.X.X.X.y & v m V D Y E Q Q W T F C M n n n i + } X.X.X.X.X.X.",
        "X.X.X.X.} . d n V D T Q ` ' ` ! W U Z M n n n b & u X.X.X.X.X.X.",
        "X.X.X.X.J @ b N A Y W ` [ | ] ` W U Z M n n n n p % X.X.X.X.X.X.",
        "X.X.X.X.q 5 n V D R ~ ] |  .] ~ R F V m n n n n x   ( X.X.X.X.X.",
        "X.X.X.X.# d m V F E ! ` ] ' ^ W U Z M n n n n n n O L X.X.X.X.X.",
        "X.X.X.X.. g m C D T W ! ~ ! E Y S B n n n n n n n = u X.X.X.X.X.",
        "X.X.X.X.  j n B A F Y T T Y F Z N n n n n n n n n * 0 ..X.X.X.X.",
        "X.X.X.X.% s n m V Z S D S Z V M n n n n n n n n n o 1 K X.X.X.X.",
        "X.X.X.X.9 6 n n m M N B N m n n n n n n n n n n x   w t _ X.X.X.",
        "X.X.X.X.H @ n n n n n n n n n n n n n n n n n n s . t t K X.X.X.",
        "X.X.X.X.{   g n n n n n n n n n n n n n n n n n & < t t t ..X.X.",
        "X.X.X.X.X.t & b n n n n n n n n n n n n n n n s   r t t t _ X.X.",
        "X.X.X.X.X...$ 4 n n n n n n n n n n n n n n l   1 t t t t ( X.X.",
        "X.X.X.X.X.X.( X 5 b n n n n n n n n n n n j . > t t t t t ( X.X.",
        "X.X.X.X.X.X.X./ O = l n n n n n n n n b 8   , t t t t t t ) X.X.",
        "X.X.X.X.X.X.X.X.J -   2 s z b n v j 6 o O 0 t t t t t t t } X.X.",
        "X.X.X.X.X.X.X.X.) t w > .           $ 1 r t t t t t t t G X.X.X.",
        "X.X.X.X.X.X.X.X.X.y t t t e w q w t t t t t t t t t t t P X.X.X.",
        "X.X.X.X.X.X.X.X.X.I t t t t t t t t t t t t t t t t t y X.X.X.X.",
        "X.X.X.X.X.X.X.X.X.X.H t t t t t t t t t t t t t t t t ) X.X.X.X.",
        "X.X.X.X.X.X.X.X.X.X...u t t t t t t t t t t t t t t P X.X.X.X.X.",
        "X.X.X.X.X.X.X.X.X.X.X...H t t t t t t t t t t t t / X.X.X.X.X.X.",
        "X.X.X.X.X.X.X.X.X.X.X.X.X.I y t t t t t t t t J } X.X.X.X.X.X.X.",
        "X.X.X.X.X.X.X.X.X.X.X.X.X.X.X.( L H G G K P } X.X.X.X.X.X.X.X.X.",
        "X.X.X.X.X.X.X.X.X.X.X.X.X.X.X.X.X.X.X.X.X.X.X.X.X.X.X.X.X.X.X.X."
        };

        """

if __name__ == '__main__':
    if M_DEBUG:
        print "DEBUG : m_current_path is " +  str(m_current_path)
        print "DEBUG : m_parent_path  is " +  str(m_parent_path)
        print "DEBUG : m_parent2_path is " +  str(m_parent2_path)
        print "DEBUG : PATH_WF_UTILS  is " +  str(PATH_WF_UTILS)
        print "DEBUG : PATH_WF_ICONS  is " +  str(PATH_WF_ICONS) 
    print get_icon(PATH_WF_ICONS, 'WF_point.svg')