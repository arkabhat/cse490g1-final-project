# cse490g1-final-project

## General Instructions

Run the following to download the dataset tarball and extract the files:
```
wget -c https://storage.googleapis.com/gresearch/dakshina/dakshina_dataset_v1.0.tar
tar -xvf dakshina_dataset_v1.0.tar
rm -rf dakshina_dataset_v1.0.tar
```

Once the dataset has been downloaded, optionally set up and activate a Python virtual environment to isolate any libraries needed for this project from any system libraries:
```
python3 -m venv ./venv
source ./venv/bin/activate
```

Then, install all of the required libraries:
```
pip3 install -r requirements.txt
```

## Development Notes

### How To: Use Jupyter Notebook on attu on Remote Machine
Jupyter should have been installed on your machine when installing the required libraries as it is one of the dependencies listed in `requirements.txt`.

Since attu does not have a GUI, we want to start our Jupyter notebook server without a browser. We can specify any port of our choice, and for this project, we have chosen port 8080:
```
# on attu
jupyter notebook --no-browser --port=8080
```

Once this command is run, you will notice some output from Jupyter. Specifically look for the output lines that look similar to the following:
```
[I 23:56:01.097 NotebookApp] Jupyter Notebook 6.4.6 is running at:
[I 23:56:01.097 NotebookApp] http://localhost:8080/?token=8b5f30b92cce57dbff42a2ef9670dcf82f79add3350c2a69
```
The token in the above output will be needed later.

At this point, the Jupyter notebook server is running on attu. Then, the next step is to access the Jupyter notebook server on attu through our local machine. For this, we set up an SSH tunnel from our local machine to attu (use another terminal window for this as we want our attu terminal to stay active):
```
# on local machine
ssh -N -L 8080:localhost:8080 <YOUR-CSE-NETID>@attu.cs.washington.edu
```

This command creates a tunnel from port 8080 on attu to port 8080 on our local machine. Now, navigating to `localhost:8080` on our local machine should open a Jupyter window. This window will ask for a password or token to login since we are accessing the server remotely. Copy-paste the token from the Jupyter output that we noted before. Then, we will be able to access our Jupyter server on attu through our local machine and edit our notebooks.

Note: the above instructions for setting up Jupyter on attu over SSH are based on the instructions from [here](https://fizzylogic.nl/2017/11/06/edit-jupyter-notebooks-over-ssh/).