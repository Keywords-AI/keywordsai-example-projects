User signs up and login

They send the first log:

-  Proxy
    - Use the prompt management feature so that variables can be replaced for different test cases
- Logging
    - Use custom prompt id for external prompt tracking
        - Add variables so that this log can be replaceable in different test cases
- Tracing
    - Different parts of traces can be imported as logs into datasets

Now user want to do evals:
- Experiments:
    - Import prompts: they are the columns of the experiment
    - Import test set sheet: they are the rows of the experiment, filling in the variables of the prompts to generate the complete prompt message
    - Run the experiment and we will have the results

- Datasets:
    - Create a dataset with logs (the endpoint forces the users to select initial logs by specifying the time range and filters)
    - Run eval
    - List eval results

