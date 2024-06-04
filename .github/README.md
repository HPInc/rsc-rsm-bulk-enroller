HP Remote System Controller bulk enrollment script
----------------------------------------------------------

_Note: This readme file, the "repo README", is located in .github/README.md. The README.md file in the root of the project is intended as documentation for the generated python distributions - sdist and wheel. The repo README has information on how to build and setup the environment which should not be needed by end users._

This script is used to enroll multiple HP Anyware Remote System Controllers
to the HP Anyware Remote System Management cloud fleet manager in one go. 
It uses the Redfish API to do so.

How to run
----------

1. Install Python 3. Windows or Linux versions are available here: https://www.python.org/downloads/.
2. Open a the command promt application (Windows), or a terminal (Linux). Navigate to the scripts directory.
3. Create a virtual environment for the scripts to run in. This is not required, but recommended.

   `python3 -m venv rscvenv`
4. Activate the virtual environment. In case you did not create one, skip this step.

   Linux: `source rscvenv/bin/activate`
   
   Windows: `rscvenv\Scripts\activate.bat`
5. Install the required packages.

    `pip3 install poetry`
6. Run the script. To get help and examples, run the script with the --examples option.

    `poetry run rsc_bulk_enrollment --examples`

How to build
------------
This will build a wheel file in the dist directory.

`poetry build`

How to install
--------------
`python3 -m pip install <path to wheel file>`


Usage
-----

```
rsc_bulk_enrollment [-h] [-c CSVFilePath] [-e] [-p] [-i [addr,curPass[,newPass] [addr,curPass[,newPass] ...]]] [--verbose] [-d] [--proxy PROXY]
                     [--ntp NTP]

RSC Bulk Cloud Enroller

optional arguments:
  -h, --help            show this help message and exit
  -c CSVFilePath        CSV file path
  -e, --examples        Display help message with usage examples.
  -p                    Only validate passwords and exit.
  -i [addr,curPass[,newPass] [addr,curPass[,newPass] ...]]
                        Specify an RSC's IP, current password and new password (if necessary), separated by commas.
  --verbose, -v         Verbose logging. Can be used up to 2 times.
  -d                    Discover RSCs in the network and exit.
  --proxy PROXY         Set this proxy for cloud access.
  --ntp NTP             Set this NTP server to correct RSCs' times.
```

The script automates the following steps for each RSC:
1. Change the default administrator password of the RSC to a user provided password if needed.
2. Adjust NTP settings of the RSC if informed to do so.
3. Tell the RSC to enroll into the RSM.

Step 3 generates a verification URI that is used to verify the enrollment.
The script aggregates all verification URIs and prints a single URI to the console,
which can be used to verify all enrollments at once. The script then monitors the 
enrollment status of every RSC.

Users can provide a list of RSCs to enroll in two ways:
1. Specify all RSCs in the command line directly. Example:

    `rsc_bulk_enrollment -i 192.168.0.88,CurrentPassword1 rschostname,CurrentPassword2,Newpassword2`
2. Specify a CSV file with RSCs. Example:

    `rsc_bulk_enrollment -c RSC.csv`

See the next section for the CSV format.
    
CSV Format
----------
Given RSC.csv as a file with the following contents:
```
192.168.240.172,CurrentPassword1,Newpassword1
192.168.240.46,CurrentPassword2,Newpassword2
192.168.240.42,CurrentPassword3
rsc-8DD123FFF,CurrentPassword4
```
The first two lines specify an address, current password and a new password. 
If a password change is required, that is, the RSC's password is still the 
default administrator password set at the factory, the script will change the
current password to the new password.
The third line only specifies the current password. If a password change is 
required the script will fail.
The fourth line specifies the RSC hostname instead of the IP address, which 
by default is "rsc-" with the serial number of the RSC, which can be scanned on 
the RSC QR code label. 
For example, the hostname for serial number 8DD123FFF would be, rsc-8DD123FFF.

Examples
--------
- Pass in a CSV of RSCs to enroll to cloud:

    `python3 rsc_bulk_enroll -c RSC.csv`

- Pass in RSCs as parameters:
    
    `python3 rsc_bulk_enroll -i 192.168.240.172,CurrentPassword1 192.168.240.46,CurrentPassword2,Newpassword2`
- Pass in a CSV of RSCs but only verify if the passwords are ok:

    `python3 rsc_bulk_enroll -c RSC.csv -p`
- Pass in a CSV of RSCs to enroll to cloud, informing proxy and NTP settings:

    `python3 rsc_bulk_enroll -c RSC.csv --ntp myNTPserver.com --proxy http://myproxy.com:8080`
