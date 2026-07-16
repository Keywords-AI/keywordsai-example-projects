import {
  createRuntime,
  createWorkflowContext,
  emit,
  getTraceWorkflowName,
  logExampleResult,
  runWithFlueTrace,
} from "./_shared.js";

const workflowName = "Flue Error Coverage.workflow";
const { respan } = createRuntime(workflowName);

const result = await runWithFlueTrace(respan, workflowName, async () => {
  const traceWorkflowName = getTraceWorkflowName(workflowName);
  const ctx = createWorkflowContext(traceWorkflowName, {
    command: "cat missing-file.txt",
  });

  emit(ctx, {
    type: "run_start",
    workflowName: traceWorkflowName,
    startedAt: new Date().toISOString(),
    payload: ctx.payload,
  });
  emit(ctx, {
    type: "operation_start",
    operationId: "shell-op",
    operationKind: "shell",
  });
  emit(ctx, {
    type: "tool_start",
    operationId: "shell-op",
    toolCallId: "shell-tool",
    toolName: "shell",
    args: { command: "cat missing-file.txt" },
  });
  emit(ctx, {
    type: "tool",
    operationId: "shell-op",
    toolCallId: "shell-tool",
    toolName: "shell",
    isError: true,
    result: { stderr: "missing-file.txt: No such file", exitCode: 1 },
    durationMs: 18,
  });
  emit(ctx, {
    type: "operation",
    operationId: "shell-op",
    operationKind: "shell",
    durationMs: 30,
    isError: true,
    error: { name: "ShellError", message: "Command failed" },
    result: { stderr: "missing-file.txt: No such file", exitCode: 1 },
  });
  ctx.log.error("shell command failed", { exitCode: 1, command: "cat missing-file.txt" });
  emit(ctx, {
    type: "run_end",
    isError: true,
    error: { name: "WorkflowError", message: "Unable to read required file" },
    durationMs: 75,
  });

  return { recovered: false, error: "Unable to read required file" };
});

logExampleResult(workflowName, {
  expectedSpans: ["tool", "tool", "task", "workflow"],
  result,
});
