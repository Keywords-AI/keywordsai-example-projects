from example_workflows.multi_modal_tool_evals.logs import get_logs
from example_workflows.multi_modal_tool_evals.constants import EVALUATION_IDENTIFIER
from datetime import datetime, timedelta

logs = get_logs(
    start_time=datetime.now() - timedelta(days=1),
    end_time=datetime.now(),
    filters={
        "evaluation_identifier": {
            "value": EVALUATION_IDENTIFIER,
        },
    },
)



