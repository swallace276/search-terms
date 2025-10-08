## TFDD Database 
- 
- geography/FullProcess.py is the file that will be run to download results
- 
- The remaining structure of this geography repository is as follows:
- * data folder
- - downloads folder - contains downloaded results for each basin code and subfolders for download type (excel/pdf)
- - status folder - contains information the main script will use for each basin's download process
- 
- * geography subfolder
- - FullProcess.py - this is the main file that will be run to download results
- - search_terms.xlsx - file with the search terms the script will use on Nexis Uni site
- - classes folder - the main script will use the Python classes in this folder for different behavior, including getting user information (UserClass.py), logging in to Nexis Uni (LoginClass.py), the search process (NoLinkClass.py), downloading (DownloadClass.py), as well as file format conversions needed in the process

- * setup folder
- HelloClass.py checks if Python is installed
- PandasTest.py checks if pandas is installed
- ChromeTest.py checks if selenium is installed and if the driver is compatible with browser 

### Prerequisites
- Setup documentation in Box
- * Computer setup - https://oregonstate.box.com/s/68ob9mulyf8q5k2mebktmmtbbu7twt4t
- * Accessing script - https://oregonstate.box.com/s/vw8wlwaupbxnvhs8q0xu11q51ovfibr3 
- * requirements.txt contains the packages and libraries needed to run the script

### Installation and Running
- * How to download https://oregonstate.box.com/s/dzdijzw7glxo63niarajqg0adhw4ur7p 