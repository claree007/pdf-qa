# Document Q/A

This application allows you to upload a pdf file and ask questions about it. This is done with the help of similarity search and answer generation using openai embeddings and models.

## Setup

**Requirements**
1. Python>=3.8
2. Internet access to install libraries and dependencies.
3. OpenAI API key

**Clone the repository**

```
git clone https://github.com/claree007/pdf-qa.git
cd pdf-qa
```

**Configuration**

Default configuration has been provided in `cfg.py`. Few configurations need to be changed like default path for vector db persistant storage. Each configuration is provided under the appropriate heading.

**Installing dependencies**

Create a virtual environment and install the dependencies from `requirements.txt`.

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Export your OpenAI key

```
export OPENAI_API_KEY=<your-key-goes-here>
```

## Running the application
Open 2 terminal windows to run the backend and streamlit applications separately. You need to create a logs directory, if required.
```
mkdir logs
cd src
```

1. To start the backend application,
```
python app.py
```

2. To start the streamlit application,
```
streamlit run streamlit_app.py
```