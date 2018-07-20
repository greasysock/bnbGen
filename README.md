# bnbGen

## About

bnbGen is a software for generating monthly reports for AirBNB and VRBO .csv files. bnbGen will output an easy to understand excel file.

### Requirements

* Python 3 and pip
* Python Libraries `xlsxwriter`
* GTK+3 libraries and desktop environment support
  * bnbGen can work on MacOS and Windows, however due to lack of support on MacOS, bnbGen will not function properly. Windows is untested.

### Installation

```bash
mkdir ~/git
cd ~/git
git clone https://github.com/greasysock/bnbGen.git
```

### Usage

1. Launch `python3 ~/git/bnbGen/bnbGenui.py `
2. To start a new client report, do `File -> New` and then enter the client's first and last name.
3. After the client files has been started, now it is time to export the .csv files from AirBNB and VRBO. Export the `.csv` files that are relevant to the client and then do `Tools -> Import...` to import the `.csv` files.
4. To add new titles to the report, click the plus sign in the bottom toolbar. You can then rearrange the listings under new/old titles.
5. Once everything is in the right order, click the gear button on the button toolbar to generate the report. Select the correct month and a save location. The report should then be generated.

### Screenshots

![Opening for the first time](/screenshots/first_open.png)

![Adding new client](/screenshots/new_client.png)

![About](/screenshots/about.png)

![Adding new title](/screenshots/add_title.png)