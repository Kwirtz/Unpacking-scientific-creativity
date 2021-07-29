import numpy as np
import time
import pyautogui
import pyperclip
import pandas as pd
import numpy as np
import re

pmids = pd.read_csv('D:\PKG\PMID_list.csv')['PMID']

def copy_clipboard():
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(.01)
    return pyperclip.paste()

def _workaround_write(text):
    
    pyperclip.copy(text)
    pyautogui.hotkey('ctrl', 'v')
    
from_ = int(open('D:\WOS_PKG\last_i.txt','r').read())
chunksize = 6000

for i in range(from_,len(pmids),chunksize):
    try:
        data = list(pmids[i:(i+chunksize)])
        
        print(i)
        print(data[0])
        url_text = [909,48]
        pyautogui.moveTo(url_text[0], url_text[1])
        pyautogui.click()
        pyautogui.hotkey('ctrl', 'a')
        url = 'apps.webofknowledge.com/'
        pyautogui.write(str(url), interval=0.02)
        time.sleep(1)
        pyautogui.press('enter')
        time.sleep(5)
        print('a_search')
        a_search = [675,457]
        #a_search= [676,526]
        ##a_search = [658,460]
        pyautogui.moveTo(a_search[0], a_search[1])
        pyautogui.click()
        time.sleep(10)
        
        print('a_search_b')
        #a_search_b = [174,711]
        a_search_b = [172,654]
        pyautogui.moveTo(a_search_b[0], a_search_b[1])
        pyautogui.click()
        time.sleep(2)
        pyautogui.hotkey('ctrl', 'a')
        query = str('PMID = ('+ str(' OR '.join(map(str,data))) +')')
        _workaround_write(query)
        
        
        time.sleep(float(abs(np.random.normal(2, 0.5, 1))))
        search = [166,713]
        #search = [193,789]
        pyautogui.moveTo(search[0], search[1])
        time.sleep(1)
        pyautogui.click()
        time.sleep(40)
        time.sleep(float(abs(np.random.normal(2, 0.5, 1))))
        querylink = [232,775]
        pyautogui.moveTo(querylink[0], querylink[1])
        pyautogui.click()
        print('30sec')
        time.sleep(30)
        time.sleep(float(abs(np.random.normal(2, 0.5, 1))))
        results1 = [229,264]
        results2 = [279,262]
        pyautogui.moveTo(results1[0], results1[1])
        pyautogui.click()
        pyautogui.keyDown('shift') 
        pyautogui.moveTo(results2[0], results2[1])
        pyautogui.click()
        pyautogui.keyUp('shift') 
        time.sleep(1)
        nb_paper = copy_clipboard()
        time.sleep(1)
        nb_paper = re.sub(' ', '', str(nb_paper))
        nb_paper = re.sub(',', '', nb_paper)#.replace(r"/[\[\]']+/g",'')
        nb_paper = int(nb_paper)
        print('export')
        for j in np.arange(1, nb_paper, 500):
            last_rec = j + 499
            if last_rec > nb_paper:
                last_rec = nb_paper
            export = [656,338]
            pyautogui.moveTo(export[0], export[1])
            pyautogui.click()
            time.sleep(3)
            
            r_from = [571,423]
            pyautogui.moveTo(r_from[0], r_from[1])
            pyautogui.click()
            time.sleep(float(abs(np.random.normal(2, 0.5, 1))))
            
            r_from_i = [724,436]
            pyautogui.moveTo(r_from_i[0], r_from_i[1])
            pyautogui.doubleClick()
            pyautogui.write(str(j), interval=0.25)
            time.sleep(float(abs(np.random.normal(2, 0.5, 1))))
            r_from_last = [828,431]
            pyautogui.moveTo(r_from_last[0], r_from_last[1])
            pyautogui.doubleClick()
            pyautogui.write(str(last_rec), interval=0.25)
            time.sleep(float(abs(np.random.normal(2, 0.5, 1))))
            
            r_cont = [770,553]
            pyautogui.moveTo(r_cont[0], r_cont[1])
            pyautogui.click()
            time.sleep(float(abs(np.random.normal(2, 0.5, 1))))
            r_cont_f_c = [629,688]
            pyautogui.moveTo(r_cont_f_c[0], r_cont_f_c[1])
            pyautogui.click()
            time.sleep(float(abs(np.random.normal(2, 0.5, 1))))
            
            export_f = [832,749]
            pyautogui.moveTo(export_f[0], export_f[1])
            pyautogui.click()
            
            time.sleep(12)
            
            time.sleep(30)
    except:
        with open('D:\WOS_PKG\\failed.txt','a') as failed:
            failed.write(str(i)+'\n')

    with open('D:\WOS_PKG\last_i.txt','w') as last_i:
        last_i.write(str(i+chunksize))

    
