# Ebay-Description-Translator
Asynchronous python script to automate translating of item descriptions found on eBay. This script will translate all the visible texts found on your item description.


# Steps to run this script locally

1. `Python 3.8` or higher versions must be installed in your system. You can download appropriate version 
through this link https://www.python.org/downloads/release/python-380/

2. You can download the file and unzip it to a directory.

3. Open the terminal by typing `cmd` in Windows search bar. Type `pip install virtualenv`, it will download virtualenv.

4. Now you have to create, activate and install all dependencies inside to virtual environment.
    
    1. In your windows command prompt, head to your project location: ``cd`` my_project
    2. Once inside the project folder run: ``virtualenv env``
    3. To activate virtualenv on Windows, and activate the script is in the Scripts folder : ``\pathto\env\Scripts\activate``. `\pathto\` can be `C:\Users\'Username'\envScripts\activate`.
    4. Upon activation `(env)` will be visible in shell, indicating that the virtual environment is activated. Instructions have taken from this link : https://www.liquidweb.com/kb/how-to-setup-a-python-virtual-environment-on-windows-10/
    5. Now we will install all the dependencies/libraries by typing ``pip install -r requirements.txt``. (Make sure your are in correct directory because you have to be able to access requirements.txt)

5. Open up ``html_text_translator.py`` using an Editor or you can just open with Notepad. Change these 3 lines only ;

    1. ```python
        CSV_FILE_PATH = "C:/Users/----/----/example.csv"
       
        OUTPUT_DIRECTORY_PATH = "C:/Users/----/----/example/{0}"
       
        LANGUAGES = ['de', 'fr', 'it', 'es']
       ```
       Note: Make sure that the file is .csv format and contains only 1 column and correct format of item numbers.
       Not like this :  1.14E+11. To avoid this you can select the column, then Right Click > Format Cells > Category(Custom) > Switch Type to 0.

       Note: Make sure you create output folder before you set ``OUTPUT_DIRECTORY_PATH``
       
6. Finally you can type `python html_text_translator.py` and it will basically achieve
    
    1. Read your item numbers from .csv file
    2. Go to eBay get currently existing descriptions for those items.
    3. Translate and rewrite to ``OUTPUT_DIRECTORY_PATH``.
    
    
# Referencing and Extra information for Developers.

This script uses `deep-translator` (https://github.com/nidhaloff/deep-translator) library for translation of the visible texts found on the eBay description. I have made a research and unofficial APIs for Google Translate were not working correctly except `deep-translator`.

Script will translate all the `visible` text in your html. However you can customize it by adding if conditionals here. 
For example

```python
for elem in texts:
    if elem.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        continue
    elif isinstance(elem, Comment):
        continue
    else:
        if len(elem.strip()) != 1 and len(elem.strip()) != 0 and str(
             elem.strip()).isdecimal() != True and not re.match(r'^[_\W]+$', str(elem.strip())):
            # Here 1 letter or 0 letter, only number, only special character won't reach inside
            # this conditional.
            # The reason is that deep-translator will throw NotInvalidPayload exception 
            # if GoogleTranslator() gets 1 letter or above payload.
      
```
You can exclude some specific words if you don't wish to translate them.
```python
if str(elem.strip()) in ['Ford','BMW','Citroen','Peugeot','Vauxhall','Mercedes']:
    continue
```
       